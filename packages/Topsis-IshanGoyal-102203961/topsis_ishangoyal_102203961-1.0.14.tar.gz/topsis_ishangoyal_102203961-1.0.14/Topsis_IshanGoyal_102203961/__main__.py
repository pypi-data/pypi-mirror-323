import numpy as np
import pandas as pd
import sys

def topsis(input_file, weights, impacts, output_file):
    if input_file.lower().endswith('.xlsx'):
        data = pd.read_excel(input_file)
    elif input_file.lower().endswith('.csv'):
        data = pd.read_csv(input_file)
    else:
        print("Unsupported file format. Please provide a .csv or .xlsx file.")
        sys.exit(1)

    decision = data.iloc[:, 1:]
    decision = np.array(decision).astype(float)
    weights = np.array(weights).astype(float)
    impacts = [char for char in impacts]
    
    nrow = decision.shape[0]
    ncol = decision.shape[1]
    
    # Validations
    assert len(decision.shape) == 2, "Decision matrix must be two-dimensional."
    assert len(weights.shape) == 1, "Weights array must be one-dimensional."
    assert len(weights) == ncol, f"Incorrect number of weights. Expected {ncol}, but got {len(weights)}."
    assert len(impacts) == ncol, f"Incorrect number of impacts. Expected {ncol}, but got {len(impacts)}."
    assert all(i in ['+', '-'] for i in impacts), "Impacts must only contain '+' or '-'."
    
    # Normalize weights
    weights = weights / sum(weights)
    
    # Normalize decision matrix
    N = np.zeros((nrow, ncol))
    nf = [np.sqrt(sum((decision[:, j]) ** 2)) for j in range(ncol)]
    for i in range(nrow):
        for j in range(ncol):
            N[i][j] = decision[i][j] / nf[j]
    
    # Apply weights
    W = np.diag(weights)
    V = np.matmul(N, W)
    
    # Determine ideal best (u) and worst (l)
    u = [max(V[:, j]) if impacts[j] == '+' else min(V[:, j]) for j in range(ncol)]
    l = [min(V[:, j]) if impacts[j] == '+' else max(V[:, j]) for j in range(ncol)]
    
    # Calculate distances to ideal best (du) and worst (dl)
    du = [np.sqrt(sum([(v1 - u1) ** 2 for v1, u1 in zip(V[i], u)])) for i in range(nrow)]
    dl = [np.sqrt(sum([(v1 - l1) ** 2 for v1, l1 in zip(V[i], l)])) for i in range(nrow)]
    
    du = np.array(du).astype(float)
    dl = np.array(dl).astype(float)
    
    # Calculate TOPSIS scores and ranks
    score = dl / (dl + du)
    score = pd.Series(score)
    ranks = score.rank(ascending=False, method='min').astype(int)
    data['Topsis Score'] = score
    data['Rank'] = ranks
    
    # Save to output file
    data.to_csv(output_file, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Incorrect number of parameters. Usage:")
        print("Topsis_KrishnaVig_102217119 <input_file> <weights> <impacts> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    weights = list(map(float, sys.argv[2].split(",")))  # Convert "1,2,3" into [1.0, 2.0, 3.0]
    impacts = sys.argv[3].split(",")  # Convert "+,+,-" into ['+', '+', '-']
    output_file = sys.argv[4]
    
    try:
        topsis(input_file, weights, impacts, output_file)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)