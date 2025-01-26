import argparse
import numpy as np
import pandas as pd

def topsis(input_file, weights, impacts, output_file):
    try:
        data = pd.read_csv(input_file)

        if data.shape[1] < 3:
            raise Exception("Input file must have at least three columns: identifier and criteria.")

        identifiers = data.iloc[:, 0]
        matrix = data.iloc[:, 1:].values

        weights = np.array([float(w) for w in weights.split(',')])
        impacts = impacts.split(',')

        if len(weights) != matrix.shape[1] or len(impacts) != matrix.shape[1]:
            raise Exception("Number of weights and impacts must match the number of criteria.")

        if not all(i in ['+', '-'] for i in impacts):
            raise Exception("Impacts must be '+' or '-'.")

        norm_matrix = matrix / np.sqrt((matrix ** 2).sum(axis=0))
        weighted_matrix = norm_matrix * weights

        ideal_best = [max(weighted_matrix[:, j]) if impacts[j] == '+' else min(weighted_matrix[:, j]) 
                      for j in range(len(impacts))]
        ideal_worst = [min(weighted_matrix[:, j]) if impacts[j] == '+' else max(weighted_matrix[:, j]) 
                       for j in range(len(impacts))]

        distances_best = np.sqrt(((weighted_matrix - ideal_best) ** 2).sum(axis=1))
        distances_worst = np.sqrt(((weighted_matrix - ideal_worst) ** 2).sum(axis=1))

        scores = distances_worst / (distances_best + distances_worst)
        ranks = scores.argsort()[::-1] + 1

        output_data = data.copy()
        output_data['Topsis Score'] = scores
        output_data['Rank'] = ranks
        output_data.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")

    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="TOPSIS Calculator")
    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument("weights", help="Comma-separated weights (e.g., '0.5,0.3,0.2')")
    parser.add_argument("impacts", help="Comma-separated impacts (e.g., '+,+,-')")
    parser.add_argument("output_file", help="Path to the output CSV file")
    args = parser.parse_args()

    topsis(args.input_file, args.weights, args.impacts, args.output_file)

if __name__ == "__main__":
    main()
