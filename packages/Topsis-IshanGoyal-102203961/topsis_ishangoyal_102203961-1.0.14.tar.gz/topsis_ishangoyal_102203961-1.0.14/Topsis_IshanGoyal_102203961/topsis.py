import pandas as pd
import math
import numpy as np
import sys
import os

class Topsis:
    def _init_(self, filename):
        # Load the file based on extension
        if os.path.isfile(filename):
            if filename.endswith('.csv'):
                self.data = pd.read_csv(filename)
            elif filename.endswith('.xlsx'):
                self.data = pd.read_excel(filename)
            else:
                print("Unsupported file format. Please provide a CSV or XLSX file.")
                sys.exit(1)
        else:
            print("File not found.")
            sys.exit(1)
        
        # Extract the decision matrix
        self.decision_matrix = self.data.iloc[:, 1:].values
        self.features = len(self.decision_matrix[0])
        self.samples = len(self.decision_matrix)

    def evaluate(self, weights=None, impacts=None):
        if weights is None:
            weights = [1] * self.features
        if impacts is None:
            impacts = ["+"] * self.features

        d = self.decision_matrix
        features = self.features
        samples = self.samples

        # Normalize the decision matrix and apply weights
        for i in range(features):
            norm_factor = math.sqrt(sum(d[:, i] ** 2))
            for j in range(samples):
                d[j, i] = (d[j, i] / norm_factor) * weights[i]

        # Calculate ideal best and worst
        ideal_best = []
        ideal_worst = []
        for i in range(features):
            if impacts[i] == "+":
                ideal_best.append(max(d[:, i]))
                ideal_worst.append(min(d[:, i]))
            else:
                ideal_best.append(min(d[:, i]))
                ideal_worst.append(max(d[:, i]))

        # Calculate distances to ideal best and worst
        scores = []
        for i in range(samples):
            distance_best = math.sqrt(sum((d[i, :] - ideal_best) ** 2))
            distance_worst = math.sqrt(sum((d[i, :] - ideal_worst) ** 2))
            score = distance_worst / (distance_best + distance_worst)
            scores.append(score)

        # Add scores and ranks to the original dataset
        self.data["Topsis Score"] = scores
        self.data["Rank"] = self.data["Topsis Score"].rank(ascending=False).astype(int)

        return self.data


def main():
    # Ensure correct number of parameters
    if len(sys.argv) != 5:
        print("Incorrect number of parameters. Usage:")
        print("python <script_name.py> <input_file> <weights> <impacts> <output_file>")
        sys.exit(1)

    # Read arguments
    input_file = sys.argv[1]
    weights = list(map(float, sys.argv[2].split(',')))
    impacts = sys.argv[3].split(',')
    output_file = sys.argv[4]

    # Validate weights and impacts
    if len(weights) != len(impacts):
        print("Error: The number of weights and impacts must match.")
        sys.exit(1)

    # Run Topsis and save output
    topsis = Topsis(input_file)
    result = topsis.evaluate(weights, impacts)
    
    # Save output based on the extension of the input file
    if output_file.endswith('.csv'):
        result.to_csv(output_file, index=False)
    elif output_file.endswith('.xlsx'):
        result.to_excel(output_file, index=False)
    else:
        print("Unsupported output file format. Please use CSV or XLSX.")
        sys.exit(1)

    print(f"Output saved to {output_file}")


if __name__ == "__main__":
    main()