import pandas as pd
import numpy as np
import os

ROLL_NUMBER = "102217020"

def convert_xlsx_to_csv(input_xlsx, output_csv):
    try:
        data = pd.read_excel(input_xlsx)
        data.to_csv(output_csv, index=False)
        print(f"Converted '{input_xlsx}' to '{output_csv}'.")
    except Exception as e:
        raise Exception(f"Error in converting file: {e}")

def validate_file(input_file):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Error: File '{input_file}' not found.")
    data = pd.read_csv(input_file)
    if data.shape[1] < 3:
        raise ValueError("Error: Input file must have at least 3 columns.")
    if not all(np.issubdtype(dtype, np.number) for dtype in data.dtypes[1:]):
        raise ValueError("Error: Non-numeric values found in the numeric columns.")
    return data

def normalize_data(data):
    norm_data = data.copy()
    for col in data.columns[1:]:
        norm_data[col] = data[col] / np.sqrt((data[col] ** 2).sum())
    return norm_data

def apply_weights_and_impacts(data, weights, impacts):
    for i, col in enumerate(data.columns[1:]):
        data[col] = data[col] * weights[i]
        if impacts[i] == '-':
            data[col] = -data[col]
    return data

def calculate_topsis(data):
    ideal_best = data.max()
    ideal_worst = data.min()
    distance_best = np.sqrt(((data - ideal_best) ** 2).sum(axis=1))
    distance_worst = np.sqrt(((data - ideal_worst) ** 2).sum(axis=1))
    scores = distance_worst / (distance_best + distance_worst)
    return scores

def topsis(input_file, weights, impacts, output_file):
    try:
        data = validate_file(input_file)
        normalized_data = normalize_data(data.iloc[:, 1:])
        weights = [float(w) for w in weights.split(',')]
        impacts = impacts.split(',')
        if len(weights) != len(impacts) or len(weights) != normalized_data.shape[1]:
            raise ValueError("Error: Number of weights, impacts, and columns must match.")
        if not all(impact in ['+', '-'] for impact in impacts):
            raise ValueError("Error: Impacts must be '+' or '-'.")
        weighted_data = apply_weights_and_impacts(normalized_data, weights, impacts)
        scores = calculate_topsis(weighted_data)
        data['Topsis Score'] = scores
        data['Rank'] = scores.rank(ascending=False).astype(int)
        data.to_csv(output_file, index=False)
        print(f"Results saved to '{output_file}' successfully.")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    input_xlsx = "/content/data.xlsx"
    input_csv = f"{102217020}-data.csv"
    output_csv = f"{102217020}-result.csv"
    weights = "1,1,1,2,1"
    impacts = "+,+,-,+,+"

    try:
        convert_xlsx_to_csv(input_xlsx, input_csv)
        topsis(input_csv, weights, impacts, output_csv)
    except Exception as e:
        print(e)