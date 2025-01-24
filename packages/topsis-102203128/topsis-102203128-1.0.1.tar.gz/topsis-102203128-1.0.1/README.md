
# TOPSIS Package for Multi-Criteria Decision Making

## What is TOPSIS?
TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) is a widely used multi-criteria decision-making (MCDM) method. It ranks alternatives based on their closeness to an ideal solution and their distance from the worst solution.

## About This Package
This package provides an easy-to-use implementation of the TOPSIS method for ranking alternatives. It processes a dataset in `.csv` or `.xlsx` format and outputs the original dataset with two additional columns: `Topsis Score` and `Rank`.

### Features:
- Accepts both `.csv` and `.xlsx` input files.
- Automatically converts `.xlsx` to `.csv` if needed.
- Validates input data to ensure correctness.
- Handles weighted and impacted criteria for decision-making.

## Installation
To install or upgrade to the latest version of this package, use the following command:
```bash
pip install --upgrade topsis-102203128
```

## Usage
This package is designed to run as a command-line utility.

### Command Syntax:
```bash
python topsis <InputDataFile> <Weights> <Impacts> <ResultFileName>
```

### Parameters:
- `<InputDataFile>`: The input file containing the decision matrix (e.g., `data.xlsx` or `data.csv`).
- `<Weights>`: A comma-separated list of weights for the criteria (e.g., `1,1,1,2`).
- `<Impacts>`: A comma-separated list of impacts (`+` for maximization, `-` for minimization) (e.g., `+,+,-,+`).
- `<ResultFileName>`: The name of the output file (e.g., `result.csv`).

### Example:
Input file `data.xlsx`:
```
| Model | Criterion 1 | Criterion 2 | Criterion 3 | Criterion 4 |
|-------|-------------|-------------|-------------|-------------|
| M1    | 250         | 16          | 12          | 5           |
| M2    | 200         | 20          | 15          | 8           |
| M3    | 300         | 18          | 10          | 6           |
```

Command:
```bash
python topsis data.xlsx "1,1,1,2" "+,+,-,+" result.csv
```

## Input File Requirements
- The file must contain **at least three columns**:
  - First column: Object/alternative names (e.g., M1, M2, M3).
  - Remaining columns: Numeric values only (criteria).
- If the input file is not `.csv`, it will be converted to `102203958-data.csv`.
- Weights and impacts must match the number of criteria columns.

## Error Handling
The package includes robust error handling for the following scenarios:
1. **File Not Found:** Displays an error if the input file does not exist.
2. **Incorrect Parameters:** Ensures the number of weights, impacts, and criteria columns match.
3. **Non-Numeric Values:** Verifies that all criteria columns contain numeric values only.
4. **Invalid Impacts:** Checks that impacts are either `+` or `-`.

## License
This package is distributed under the MIT License. See the LICENSE file for details.
