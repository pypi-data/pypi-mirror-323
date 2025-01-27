import pandas as pd
import numpy as np
import os

def topsis(input_file, weights, impacts, result_file):
    try:
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"File '{input_file}' not found.")
        
        data = pd.read_csv(input_file)
        if len(data.columns) < 3:
            raise ValueError("Input file must contain at least 3 columns.")
        
        weights = list(map(float, weights.split(',')))
        impacts = impacts.split(',')
        if len(weights) != len(impacts) or len(weights) != (data.shape[1] - 1):
            raise ValueError("Number of weights, impacts, and data columns must match.")
        
        if not all(impact in ['+', '-'] for impact in impacts):
            raise ValueError("Impacts must be '+' or '-'.")

        matrix = data.iloc[:, 1:].values
        norm_matrix = matrix / np.sqrt((matrix ** 2).sum(axis=0))
        weighted_matrix = norm_matrix * weights
        
        ideal_best = np.where(np.array(impacts) == '+', weighted_matrix.max(axis=0), weighted_matrix.min(axis=0))
        ideal_worst = np.where(np.array(impacts) == '+', weighted_matrix.min(axis=0), weighted_matrix.max(axis=0))
        
        dist_best = np.sqrt(((weighted_matrix - ideal_best) ** 2).sum(axis=1))
        dist_worst = np.sqrt(((weighted_matrix - ideal_worst) ** 2).sum(axis=1))
        
        scores = dist_worst / (dist_best + dist_worst)
        data['Topsis Score'] = scores
        data['Rank'] = scores.rank(ascending=False).astype(int)
        
        data.to_csv(result_file, index=False)
        print(f"Results saved to '{result_file}'.")
    except Exception as e:
        print(f"Error: {e}")
