import sys
import pandas as pd
import numpy as np
def validate_inputs(weights, impacts, num_criteria):
    try:
        weights = list(map(float, weights.split(',')))
        impacts = impacts.split(',')
    except ValueError:
        print("Error: Weights must be numeric and separated by commas.")
        sys.exit(1)
    
    if len(weights) != num_criteria or len(impacts) != num_criteria:
        print("Error: The number of weights, impacts, and criteria columns must be the same.")
        sys.exit(1)
    
    if not all(i in ['+', '-'] for i in impacts):
        print("Error: Impacts must be either '+' or '-'.")
        sys.exit(1)
    
    return weights, impacts

def topsis(input_file, weights, impacts, output_file):
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print("Error: Input file not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading the file: {e}")
        sys.exit(1)
    
    if df.shape[1] < 3:
        print("Error: Input file must have at least three columns.")
        sys.exit(1)
    
    try:
        data = df.iloc[:, 1:].astype(float)
    except ValueError:
        print("Error: All columns except the first one must contain numeric values.")
        sys.exit(1)
    
    num_criteria = data.shape[1]
    weights, impacts = validate_inputs(weights, impacts, num_criteria)
    
    # Step 1: Normalize the decision matrix
    norm_data = data / np.sqrt((data ** 2).sum())
    
    # Step 2: Multiply by weights
    norm_data *= weights
    
    # Step 3: Determine ideal best and ideal worst
    ideal_best = np.where(np.array(impacts) == '+', norm_data.max(), norm_data.min())
    ideal_worst = np.where(np.array(impacts) == '+', norm_data.min(), norm_data.max())
    
    # Step 4: Compute distances to ideal best and ideal worst
    dist_best = np.sqrt(((norm_data - ideal_best) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((norm_data - ideal_worst) ** 2).sum(axis=1))
    
    # Step 5: Compute Topsis Score
    topsis_score = dist_worst / (dist_best + dist_worst)
    
    # Step 6: Rank alternatives
    df['Topsis Score'] = topsis_score
    df['Rank'] = df['Topsis Score'].rank(method='max', ascending=False).astype(int)
    
    df.to_csv(output_file, index=False)
    print("TOPSIS Score and Rank Updated and saved to the output file = ",output_file)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        sys.exit(1)
    
    _, input_file, weights, impacts, output_file = sys.argv
    topsis(input_file, weights, impacts, output_file)
