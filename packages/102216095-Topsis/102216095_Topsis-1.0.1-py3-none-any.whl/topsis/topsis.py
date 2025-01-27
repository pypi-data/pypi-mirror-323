import numpy as np
import pandas as pd
import sys

def validate_inputs(args):
    print("Validating inputs...")
    if len(args) != 5:
        raise ValueError("Incorrect number of parameters. Usage: python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>")

    input_file, weights, impacts, result_file = args[1:]

    # Validate weights and impacts
    weights = weights.split(',')
    impacts = impacts.split(',')

    try:
        weights = [float(w) for w in weights]
    except ValueError:
        raise ValueError("Weights must be numeric and separated by commas.")

    if not all(i in ['+', '-'] for i in impacts):
        raise ValueError("Impacts must be '+' or '-' and separated by commas.")

    print("Inputs validated successfully.")
    return input_file, weights, impacts, result_file

def load_and_validate_data(input_file):
    print(f"Loading data from '{input_file}'...")
    try:
        data = pd.read_csv(input_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{input_file}' not found.")

    print("Data loaded successfully.")
    if data.shape[1] < 3:
        raise ValueError("Input file must contain at least three columns.")

    for col in data.columns[1:]:
        if not pd.api.types.is_numeric_dtype(data[col]):
            raise ValueError(f"Column '{col}' must contain numeric values only.")

    print("Data validation complete.")
    return data

def topsis(data, weights, impacts):
    print("Performing TOPSIS...")
    # Convert data to numpy array for calculations
    matrix = data.iloc[:, 1:].values

    # Step 1: Normalize the decision matrix
    norm_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))
    print("Normalization complete.")

    # Step 2: Weight the normalized matrix
    weighted_matrix = norm_matrix * weights
    print("Weighting complete.")

    # Step 3: Identify the ideal (best) and anti-ideal (worst) solutions
    ideal_solution = np.zeros(weighted_matrix.shape[1])
    anti_ideal_solution = np.zeros(weighted_matrix.shape[1])

    for i in range(weighted_matrix.shape[1]):
        if impacts[i] == '+':  # Beneficial criterion
            ideal_solution[i] = weighted_matrix[:, i].max()
            anti_ideal_solution[i] = weighted_matrix[:, i].min()
        elif impacts[i] == '-':  # Non-beneficial criterion
            ideal_solution[i] = weighted_matrix[:, i].min()
            anti_ideal_solution[i] = weighted_matrix[:, i].max()

    print("Ideal and anti-ideal solutions identified.")

    # Step 4: Calculate the separation measures
    separation_ideal = np.sqrt(((weighted_matrix - ideal_solution) ** 2).sum(axis=1))
    separation_anti_ideal = np.sqrt(((weighted_matrix - anti_ideal_solution) ** 2).sum(axis=1))
    print("Separation measures calculated.")

    # Step 5: Calculate the TOPSIS score
    scores = separation_anti_ideal / (separation_ideal + separation_anti_ideal)
    print("TOPSIS scores calculated.")

    return scores

def main():
    try:
        print("Starting TOPSIS analysis...")
        # Validate command-line arguments
        input_file, weights, impacts, result_file = validate_inputs(sys.argv)

        # Load and validate the input data
        data = load_and_validate_data(input_file)

        # Validate the consistency of weights, impacts, and columns
        if len(weights) != len(impacts) or len(weights) != data.shape[1] - 1:
            raise ValueError("Number of weights, impacts, and columns (from 2nd to last) must be the same.")

        print("Consistency of weights, impacts, and columns validated.")

        # Perform TOPSIS
        scores = topsis(data, weights, impacts)

        # Add TOPSIS scores and rank to the data
        data['Topsis Score'] = scores
        data['Rank'] = data['Topsis Score'].rank(ascending=False).astype(int)
        print("Scores and ranks added to the data.")

        # Save the result to a file
        data.to_csv(result_file, index=False)
        print(f"Results saved to '{result_file}'.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()