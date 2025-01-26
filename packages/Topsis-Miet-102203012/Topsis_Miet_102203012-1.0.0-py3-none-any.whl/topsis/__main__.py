import sys
import pandas as pd
import numpy as np

def validate_and_read_inputs(input_file, weights, impacts):
    """Validate the input data, weights, and impacts."""
    try:
        data = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Check for minimum number of columns
    if data.shape[1] < 3:
        print("Error: Input file must have at least 3 columns (1 ID column and 2 numeric columns).")
        sys.exit(1)

    # Ensure numeric data in all columns except the first
    if not data.iloc[:, 1:].apply(pd.api.types.is_numeric_dtype).all():
        print("Error: All columns (except the first) must contain numeric values only.")
        sys.exit(1)

    weights_list = weights.split(",")
    impacts_list = impacts.split(",")

    # Validate weights and impacts length
    if len(weights_list) != len(impacts_list) or len(weights_list) != (data.shape[1] - 1):
        print("Error: The number of weights and impacts must match the number of numeric columns.")
        sys.exit(1)

    try:
        weights_list = [float(w) for w in weights_list]
    except ValueError:
        print("Error: Weights must be numeric values separated by commas.")
        sys.exit(1)

    if not all(impact in ["+", "-"] for impact in impacts_list):
        print("Error: Impacts must be '+' or '-' separated by commas.")
        sys.exit(1)

    return data, weights_list, impacts_list

def normalize_matrix(data):
    """Normalize the decision matrix using the Euclidean norm."""
    return data.apply(lambda col: col / np.sqrt((col ** 2).sum()), axis=0)

def apply_weights(normalized_matrix, weights):
    """Apply weights to the normalized matrix."""
    return normalized_matrix * weights

def get_ideal_solutions(weighted_matrix, impacts):
    """Calculate the ideal best and worst solutions."""
    ideal_best = []
    ideal_worst = []

    for i, impact in enumerate(impacts):
        column = weighted_matrix.iloc[:, i]
        if impact == "+":
            ideal_best.append(column.max())  # Max for benefit criteria
            ideal_worst.append(column.min())  # Min for benefit criteria
        else:
            ideal_best.append(column.min())  # Min for cost criteria
            ideal_worst.append(column.max())  # Max for cost criteria

    return np.array(ideal_best), np.array(ideal_worst)

def calculate_distances(weighted_matrix, ideal_best, ideal_worst):
    """Calculate distances from ideal best and worst solutions."""
    distances_best = np.sqrt(((weighted_matrix - ideal_best) ** 2).sum(axis=1))
    distances_worst = np.sqrt(((weighted_matrix - ideal_worst) ** 2).sum(axis=1))
    return distances_best, distances_worst

def calculate_topsis_scores(distances_best, distances_worst):
    """Calculate the TOPSIS scores for each alternative."""
    return distances_worst / (distances_best + distances_worst)

def save_results(data, scores, result_file):
    """Save the results with TOPSIS scores and rankings to a CSV file."""
    data["TOPSIS Score"] = scores
    data["Rank"] = scores.rank(ascending=False).astype(int)

    try:
        data.to_csv(result_file, index=False)
        print(f"Results saved to '{result_file}'.")
    except Exception as e:
        print(f"Error saving result file: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 5:
        print("Usage: python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        sys.exit(1)

    input_file = sys.argv[1]
    weights = sys.argv[2]
    impacts = sys.argv[3]
    result_file = sys.argv[4]

    # Step 1: Validate inputs and read data
    data, weights_list, impacts_list = validate_and_read_inputs(input_file, weights, impacts)

    # Step 2: Normalize the numeric data (excluding the first column)
    numeric_data = data.iloc[:, 1:]
    normalized_matrix = normalize_matrix(numeric_data)

    # Step 3: Apply weights to the normalized data
    weighted_matrix = apply_weights(normalized_matrix, weights_list)

    # Step 4: Calculate ideal best and worst solutions
    ideal_best, ideal_worst = get_ideal_solutions(weighted_matrix, impacts_list)

    # Step 5: Calculate distances from ideal solutions
    distances_best, distances_worst = calculate_distances(weighted_matrix, ideal_best, ideal_worst)

    # Step 6: Calculate TOPSIS scores
    topsis_scores = calculate_topsis_scores(distances_best, distances_worst)

    # Step 7: Save results to the output file
    save_results(data, topsis_scores, result_file)

if __name__ == "__main__":
    main()
