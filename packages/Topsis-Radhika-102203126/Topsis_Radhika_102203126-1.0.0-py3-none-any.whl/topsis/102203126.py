import pandas as pd
import numpy as np
import sys
import os

def check_and_parse_inputs(df, weight_input, impact_input):
    # Check that the dataset has at least 3 columns
    if df.shape[1] < 3:
        raise ValueError("The uploaded dataset should have at least three columns.")
    
    try:
        # Parse the weights and impacts
        weights = [float(w) for w in weight_input.split(',')]
        impacts = impact_input.split(',')
    except ValueError:
        raise ValueError("Weights must be numerical values separated by commas.")
    
    # Ensure the number of weights and impacts match the number of criteria columns (excluding the first column for alternatives)
    if len(weights) != len(impacts) or len(weights) != df.shape[1] - 1:
        raise ValueError("The number of weights and impacts must match the number of criteria columns.")
    
    # Check if all impacts are valid ('+' or '-')
    if not all(impact in ['+', '-'] for impact in impacts):
        raise ValueError("Impacts should only be '+' (benefit) or '-' (cost).")
    
    return weights, impacts

def perform_topsis_analysis(df, weights, impacts):
    # Extract numeric data (excluding the first column with alternatives)
    criteria_data = df.iloc[:, 1:].to_numpy()
    
    # Normalize the data
    normalization_factors = np.sqrt(np.sum(criteria_data**2, axis=0))
    normalized_matrix = criteria_data / normalization_factors
    
    # Apply weights to the normalized data
    weighted_matrix = normalized_matrix * weights
    
    # Calculate the ideal best and worst solutions based on the impact
    ideal_best = [np.max(weighted_matrix[:, i]) if impacts[i] == '+' else np.min(weighted_matrix[:, i]) 
                  for i in range(len(impacts))]
    ideal_worst = [np.min(weighted_matrix[:, i]) if impacts[i] == '+' else np.max(weighted_matrix[:, i]) 
                   for i in range(len(impacts))]
    
    # Calculate the Euclidean distance from the ideal best and worst solutions
    distance_best = np.sqrt(np.sum((weighted_matrix - ideal_best) ** 2, axis=1))
    distance_worst = np.sqrt(np.sum((weighted_matrix - ideal_worst) ** 2, axis=1))
    
    # Prevent division by zero in the calculation of TOPSIS score
    topsis_scores = distance_worst / (distance_best + distance_worst + 1e-6)
    
    # Add the scores and ranks to the dataframe
    df['TOPSIS Score'] = topsis_scores
    df['Rank'] = pd.Series(topsis_scores).rank(ascending=False, method='min').astype(int)
    
    return df

def main():
    # Ensure correct number of arguments
    if len(sys.argv) != 5:
        print("Usage: python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        sys.exit(1)

    input_file = sys.argv[1]
    weight_input = sys.argv[2]
    impact_input = sys.argv[3]
    result_file = sys.argv[4]
    
    # Check if input file exists
    if not os.path.isfile(input_file):
        print(f"Error: The file '{input_file}' was not found.")
        sys.exit(1)

    try:
        # Load the data
        data = pd.read_csv(input_file)
        
        # Parse and validate inputs
        weights, impacts = check_and_parse_inputs(data, weight_input, impact_input)
        
        # Perform the TOPSIS analysis
        result_df = perform_topsis_analysis(data, weights, impacts)
        
        # Save the results to a new CSV file
        result_df.to_csv(result_file, index=False)
        print(f"Results have been saved to '{result_file}'.")
    
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except ValueError as ve:
        print(f"Input Error: {ve}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
