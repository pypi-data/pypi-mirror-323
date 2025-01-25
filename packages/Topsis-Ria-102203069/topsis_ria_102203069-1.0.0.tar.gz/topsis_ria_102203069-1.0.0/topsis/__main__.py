import sys
import pandas as pd
import numpy as np

def validate_inputs(file_name, weights, impacts):
    # Check if the file exists
    try:
        data = pd.read_csv(file_name)
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        sys.exit(1)

    # Check if the file has at least 3 columns
    if data.shape[1] < 3:
        print("Error: Input file must have at least 3 columns.")
        sys.exit(1)

    # Check for non-numeric values in decision matrix (excluding the first column)
    if not np.all(data.iloc[:, 1:].applymap(np.isreal).all()):
        print("Error: All values in the decision matrix (except the first column) must be numeric.")
        sys.exit(1)

    # Validate weights and impacts
    weights = weights.split(',')
    impacts = impacts.split(',')

    if len(weights) != data.shape[1] - 1 or len(impacts) != data.shape[1] - 1:
        print("Error: Number of weights and impacts must match the number of criteria columns.")
        sys.exit(1)

    if not all(w.isdigit() for w in weights):
        print("Error: Weights must be numeric.")
        sys.exit(1)

    if not all(impact in ['+', '-'] for impact in impacts):
        print("Error: Impacts must be either '+' or '-'.")
        sys.exit(1)

    return data, list(map(float, weights)), impacts

def topsis(data, weights, impacts):
    # Normalize the decision matrix
    norm_data = data.iloc[:, 1:].div(np.sqrt((data.iloc[:, 1:] ** 2).sum()), axis=1)

    # Apply weights
    weighted_data = norm_data * weights

    # Determine ideal best and worst solutions
    ideal_best = [
        weighted_data[col].max() if imp == '+' else weighted_data[col].min()
        for col, imp in zip(weighted_data.columns, impacts)
    ]
    ideal_worst = [
        weighted_data[col].min() if imp == '+' else weighted_data[col].max()
        for col, imp in zip(weighted_data.columns, impacts)
    ]

    # Calculate distances to ideal best and worst
    dist_best = np.sqrt(((weighted_data - ideal_best) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((weighted_data - ideal_worst) ** 2).sum(axis=1))

    # Calculate TOPSIS score
    scores = dist_worst / (dist_best + dist_worst)

    # Rank the scores
    ranks = scores.rank(ascending=False)

    # Append scores and ranks to the original dataframe
    data['Topsis Score'] = scores
    data['Rank'] = ranks.astype(int)

    return data

def main():
    if len(sys.argv) != 5:
        print("Usage: python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        sys.exit(1)

    input_file, weights, impacts, result_file = sys.argv[1:]

    # Validate inputs
    data, weights, impacts = validate_inputs(input_file, weights, impacts)

    # Apply TOPSIS
    result_data = topsis(data, weights, impacts)

    # Save the result to a CSV file
    result_data.to_csv(result_file, index=False)
    print(f"Results saved to '{result_file}'.")

if __name__== "__main__":
    main()