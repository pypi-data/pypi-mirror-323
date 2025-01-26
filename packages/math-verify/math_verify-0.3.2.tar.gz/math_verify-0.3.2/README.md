# Math-Verify
A robust mathematical expression evaluation system designed for assessing Large Language Model outputs in mathematical tasks. This evaluator achieves the highest accuracy and most correct scores compared to existing evaluators:


| Evaluator     | Score   |
|---------------|---------|
| Harness       | 0.0802  |
| Qwen          | 0.1288  |
| Math-Verify   | 0.1328  |

## Installation

```bash
pip install math-verify
```

## Example Usage
```python
from math_verify import parse, verify

# Parse the gold and answer
# If you know that gold will only contain latex or expr (no latex env), use
# parse(gold, extraction_config=[LatexExtractionConfig()]) or parse(gold, extraction_config=[ExprExtractionConfig()])

gold = parse("${1,3} \\cup {2,4}$")
answer = parse("${1,2,3,4}$")

# Order here is important!
verify(gold, answer)
# >>> True
```

## Why Another Math Evaluator?

Existing math evaluators often fail to correctly assess model outputs due to:
1. Strict format requirements (expecting exact patterns like "Final answer is X")
2. Limited parsing capabilities (especially for complex mathematical notations)
3. Inflexible comparison logic (unable to recognize equivalent expressions)
As result, this can lead to significant underestimation of model performance, in extreme cases, even by 40 points.

## Key Features

### 1. Robust Answer Extraction
- Multiple extraction strategies (LaTeX, Plain Numerical Expressions)
- Answer retrieval is done in format agnostic manner, with best effort to extract the answer.
- Supports all standard latex formats for the best retrieval.

### 2. Advanced Parsing Capabilities
- Complete set theory support (Intervals, FiniteSets, set operations)
- Unicode symbol substituion support (e.g. `β -> beta`)
- Applies Latex fixes for common malformations (e.g. `frac13 -> 1/3`)
- Equation and inequality parsing, with symbol assignment resolution (e.g. `x = 1 -> 1`)
- Percentage best effort conversion (e.g. `10% -> 0.1`)
- Units in text handling (e.g. `10 cm -> 10`)
- Exact representation of the input expressions (e.g. `0.333 -> Float(333, 3)`)

### 3. Intelligent Expression Comparison
- Both numerical and symbolic comparison support
- Precise numerical comparison for numerical types with configurable rounding tolerance
- Matrix expression equivalence validation
- Set and interval comparison
- Relation evaluation with flip support (e.g., `a < 2 == 2 > a`)

## Advanced Usage
If you already have a model outputs, format them into a csv file with `answer`, `gold` columns.
Then run the following command:
```bash
python evaluate_model_outputs.py --input_csv <path_to_csv> (examples/model_outputs.csv) --output_csv <path_to_csv> (output.csv)
```

If you want to evaluate a model from ground up, we have provided a script for end to end evaluation with support for following datasets:
- MATH-Hard
- MATH-500
- GSM8K
- AMC23
- AIME24

Run the following command to evaluate a model:
```bash
python evaluate_model.py --model_name <model_name> (Qwen/Qwen2.5-72B-Instruct) --use_chat_template (True) --dataset <dataset_name> (math_hard)
```

Lastly if you want to only extract the answers from model outputs, you can run the following command:
```bash
python extract_answers.py --input_csv <path_to_csv> (examples/sample_answers.csv) --output_csv <path_to_csv> (output.csv)
```

## Architecture

![Architecture](./assets/flow.svg)


The grading process follows a three-step algorithm:
Answer Extraction -> Expression Common Representation Conversion (SymPy) -> Gold Comparison

1. **Answer Extraction** (see `math_verify/parser.py`): 
   Retrieves the answer from the model output in a format-agnostic manner.
   1. Regex patterns are prepared based on configuration, each with a priority indicating the order of application.
   2. Priorities range from the most concrete answer format to the most abstract.
   3. Regex patterns are applied in order of priority; if multiple matches occur, those appearing last are chosen first.
   4. The first regex match that successfully converts to a common representation (SymPy) is returned; additionally, returning the first match is also allowed.

2. **Answer Parsing** (see `latex2sympy2_extended/latex2sympy2.py`):
   - Converts the extracted answer to a common representation (SymPy).
   1. Normalizes the extracted answer to address the following issues:
      - Basic LaTeX commands (e.g., \mathrm, \displaystyle)
      - Units and their variations
      - Malformed operators (e.g., \sqrt, \frac)
      - Minor formatting fixes (spaces, dots, etc.)
      - Boxed environments
      - Equation splitting and approximations
   2. Parses the normalized answer using ANTLR4 grammar to convert it to a SymPy expression.
   3. Handles special cases:
      - Percentage conversion
      - Matrix operations 
      - Derivatives and integrals
      - Complex numbers
      - Sets and intervals

3. **Gold Comparison** (see `math_verify/grader.py`):
   - Compares the parsed answer with the gold answer.
   1. Initially attempts string comparison and basic SymPy equality:
      - Direct string comparison after normalization
      - Basic SymPy structural equality (e.g., a + b vs b + a)
   
   2. For numeric expressions:
      - Numeric equality within specified precision (e.g., 0.333333 ≈ 1/3)
      - Symbolic equality by simplifying the difference (a - b = 0)
   
   3. Special handling for different types:
      - Relational expressions (equations/inequalities):
        * Compares normalized forms
        * Handles flipped inequalities (e.g., a ≤ b equals b ≥ a)
      
      - Sets and intervals:
        * Direct set equality and symmetric difference
        * Element-wise comparison for finite sets
        * Special handling for interval vs. finite set cases
        * Interval endpoint comparison with precision
      
      - Matrices and vectors:
        * Element-wise comparison
        * Shape validation
        * Special handling for matrix operations
   
   4. Complex number support:
      - Detection of complex expressions
      - Handling of different complex notations (e.g., i, ℂ)
      - Matrix operations (e.g., det, trace, rank)
      - Complex functions (e.g., Re, Im, arg)
   
   5. Robust error handling:
      - Timeout protection for long computations
      - Graceful fallback for failed comparisons
      - Multiple comparison attempts with different methods