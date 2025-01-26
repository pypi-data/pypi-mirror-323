import pandas as pd
import numpy as np
import sys

def topsis(input_file, weights, impacts, result_file):
    try:
        # Read the input file
        if input_file.endswith('.xlsx'):
            data = pd.read_excel(input_file, engine='openpyxl')
        elif input_file.endswith('.csv'):
            data = pd.read_csv(input_file)
        else:
            raise ValueError("Unsupported file format. Use a .csv or .xlsx file.")


        # Validate the number of columns
        if data.shape[1] < 3:
            raise ValueError("Input file must contain at least three columns.")

        # Validate weights and impacts
        weights = list(map(float, weights.split(',')))
        impacts = impacts.split(',')

        if len(weights) != data.shape[1] - 1 or len(impacts) != data.shape[1] - 1:
            raise ValueError("Number of weights, impacts, and criteria must be the same.")
        
        if not all(impact in ['+', '-'] for impact in impacts):
            raise ValueError("Impacts must be either '+' or '-'.")

        # Validate numeric columns
        numeric_data = data.iloc[:, 1:]
        if not all(np.issubdtype(dtype, np.number) for dtype in numeric_data.dtypes):
            raise ValueError("All columns except the first must contain numeric values.")

        # Normalize the data
        norm_data = numeric_data / np.sqrt((numeric_data ** 2).sum())
        
        # Apply weights
        weighted_data = norm_data * weights

        # Determine ideal best and worst
        ideal_best = []
        ideal_worst = []
        for i, impact in enumerate(impacts):
            if impact == '+':
                ideal_best.append(weighted_data.iloc[:, i].max())
                ideal_worst.append(weighted_data.iloc[:, i].min())
            else:
                ideal_best.append(weighted_data.iloc[:, i].min())
                ideal_worst.append(weighted_data.iloc[:, i].max())

        # Calculate distances to ideal best and worst
        distances_best = np.sqrt(((weighted_data - ideal_best) ** 2).sum(axis=1))
        distances_worst = np.sqrt(((weighted_data - ideal_worst) ** 2).sum(axis=1))

        # Calculate TOPSIS score
        topsis_score = distances_worst / (distances_best + distances_worst)

        # Rank the scores
        data['Topsis Score'] = topsis_score
        data['Rank'] = topsis_score.rank(ascending=False).astype(int)

        # Save the result to output file
        data.to_csv(result_file, index=False)
        print(f"Result saved successfully in {result_file}")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")