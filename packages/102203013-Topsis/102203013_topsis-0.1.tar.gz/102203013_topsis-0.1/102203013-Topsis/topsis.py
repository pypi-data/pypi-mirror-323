import pandas as pd
import numpy as np
import sys
import os

def topsis(input_file, weights, impacts, output_file):
    try:
        
        dataset = pd.read_csv(input_file)
        
        
        if len(dataset.columns) < 3:
            raise ValueError("Input file must contain at least three columns.")
        
       
        for col in dataset.columns[1:]:
            if not pd.api.types.is_numeric_dtype(dataset[col]):
                raise ValueError(f"Columns must contain numeric values only.")
        
        
        weights = list(map(float, weights.split(',')))
        impacts = impacts.split(',')
        
        
        if len(weights) != len(dataset.columns[1:]) or len(impacts) != len(dataset.columns[1:]):
            raise ValueError("Number of weights, impacts, and columns must be the same.")
        
    
        if not all(impact in ['+', '-'] for impact in impacts):
            raise ValueError("Impacts can either be '+' or '-'.")
        
        
        ndataset = dataset.copy()
        for col in dataset.columns[1:]:
            col_sq_sum = np.sqrt(np.sum(dataset[col] ** 2))
            ndataset[col] = dataset[col] / col_sq_sum
        
        
        for i, col in enumerate(dataset.columns[1:]):
            ndataset[col] = ndataset[col] * weights[i]
        

        ideal_best = []
        ideal_worst = []
        for i, impact in enumerate(impacts):
            col = dataset.columns[i + 1]
            if impact == '+':
                ideal_best.append(ndataset[col].max())
                ideal_worst.append(ndataset[col].min())
            else:
                ideal_best.append(ndataset[col].min())
                ideal_worst.append(ndataset[col].max())
        

        ideal_best = np.array(ideal_best)
        ideal_worst = np.array(ideal_worst)
        distance_best = np.sqrt(np.sum((ndataset.iloc[:, 1:] - ideal_best) ** 2, axis=1))
        distance_worst = np.sqrt(np.sum((ndataset.iloc[:, 1:] - ideal_worst) ** 2, axis=1))
        
        
        performance_score = distance_worst / (distance_best + distance_worst)
        

        dataset['Topsis Score'] = performance_score
        dataset['Rank'] = dataset['Topsis Score'].rank(ascending=False).astype(int)
        
        # Save the result file
        dataset.to_csv(output_file, index=False)
        print(f" file saved as {output_file}")
    
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    weights = sys.argv[2]
    impacts = sys.argv[3]
    output_file = sys.argv[4]
    

    topsis(input_file, weights, impacts, output_file)
