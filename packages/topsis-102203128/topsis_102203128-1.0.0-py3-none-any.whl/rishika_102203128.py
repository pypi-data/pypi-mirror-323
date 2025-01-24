import pandas as pd
import numpy as np
import os
import sys

def calculate_topsis(input_file, weights, impacts, result_file):
    """
    Perform TOPSIS calculation and save the results to the output file.
    """
    # Check if the input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File '{input_file}' not found.")

    # Convert XLSX to CSV if necessary
    if input_file.endswith('.xlsx'):
        input_file = convert_to_csv(input_file)

    # Load the dataset
    data = pd.read_csv(input_file)

    # Validate input dataset
    if data.shape[1] < 3:
        raise ValueError("Input file must contain at least three columns.")

    weights = [float(w) for w in weights.split(',')]
    impacts = impacts.split(',')

    if len(weights) != len(impacts) or len(weights) != data.shape[1] - 1:
        raise ValueError("Number of weights, impacts, and decision columns must be the same.")

    if not all(i in ['+', '-'] for i in impacts):
        raise ValueError("Impacts must be either '+' or '-'.")

    # Ensure all columns except the first are numeric
    try:
        numeric_data = data.iloc[:, 1:].astype(float)
    except ValueError:
        raise ValueError("All decision columns must contain numeric values.")

    # Step 2: Normalize the dataset
    normalized_data = numeric_data / np.sqrt((numeric_data**2).sum(axis=0))

    # Step 3: Apply weights to normalized data
    weighted_data = normalized_data * weights

    # Step 4: Calculate ideal best and worst
    ideal_best = [max(weighted_data.iloc[:, i]) if impacts[i] == '+' else min(weighted_data.iloc[:, i]) for i in range(len(weights))]
    ideal_worst = [min(weighted_data.iloc[:, i]) if impacts[i] == '+' else max(weighted_data.iloc[:, i]) for i in range(len(weights))]

    # Step 5: Calculate distances to ideal best and worst
    distance_to_best = np.sqrt(((weighted_data - ideal_best)**2).sum(axis=1))
    distance_to_worst = np.sqrt(((weighted_data - ideal_worst)**2).sum(axis=1))

    # Step 6: Calculate performance scores
    scores = distance_to_worst / (distance_to_best + distance_to_worst)

    # Step 7: Add scores and ranks to the dataset
    data['Topsis Score'] = scores
    data['Rank'] = scores.rank(ascending=False, method='dense').astype(int)

    # Save the results to the output file
    data.to_csv(result_file, index=False)

def convert_to_csv(xlsx_file):
    """
    Convert an XLSX file to CSV and return the new filename.
    """
    base_filename = os.path.splitext(os.path.basename(xlsx_file))[0]
    csv_file = f"102203958-{base_filename}.csv"
    data = pd.read_excel(xlsx_file)
    data.to_csv(csv_file, index=False)
    return csv_file

def main():
    if len(sys.argv) != 5:
        print("Usage: topsis <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        sys.exit(1)

    input_file = sys.argv[1]
    weights = sys.argv[2]
    impacts = sys.argv[3]
    result_file = sys.argv[4]

    try:
        calculate_topsis(input_file, weights, impacts, result_file)
        print(f"Result file saved as '{result_file}'.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
