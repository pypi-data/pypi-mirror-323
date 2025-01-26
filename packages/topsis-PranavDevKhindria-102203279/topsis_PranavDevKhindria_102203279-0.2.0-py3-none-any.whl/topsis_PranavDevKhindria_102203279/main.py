    #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on: Jan 19, 2025
Author: Pranav Dev Khindria
Description: A command line TOPSIS implementation in Python.
"""

import sys
import os   
import pandas as pd
import numpy as np

def topsis(input_file, weights, impacts, output_file):
    """
    Perform the TOPSIS analysis on the given CSV input_file and write the result to output_file.
    
    Parameters:
    -----------
    input_file : str
        Path to the input CSV file (must have at least 3 columns).
        First column: name/label for each row.
        Next columns: numeric values.
    weights : list of float
        List of weights corresponding to each numeric column (excluding the first column).
    impacts : list of str
        List of '+' or '-' signs for each numeric column to indicate beneficial or non-beneficial.
    output_file : str
        Filename/path to store the output with Topsis Score and Rank columns added.
    """
    
    # 1. Read the data
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading '{input_file}': {e}")
        sys.exit(1)
        
    # 2. Validate input data
    
    # Must contain at least 3 columns
    if df.shape[1] < 3:
        print("Error: Input file must contain at least three columns.")
        sys.exit(1)
        
    # Split into identifier column and numeric columns
    # First column is an identifier; from 2nd to last columns are numeric
    identifier_col = df.iloc[:, 0]  # object/variable names
    numeric_df = df.iloc[:, 1:]
    
    # Check if numeric columns indeed contain numeric values only
    for col in numeric_df.columns:
        if not pd.api.types.is_numeric_dtype(numeric_df[col]):
            print(f"Error: Column '{col}' contains non-numeric values. All columns (except the first) must be numeric.")
            sys.exit(1)
    
    # Check weights, impacts length
    if len(weights) != numeric_df.shape[1]:
        print(f"Error: Number of weights ({len(weights)}) does not match the number of numeric columns ({numeric_df.shape[1]}).")
        sys.exit(1)
    if len(impacts) != numeric_df.shape[1]:
        print(f"Error: Number of impacts ({len(impacts)}) does not match the number of numeric columns ({numeric_df.shape[1]}).")
        sys.exit(1)
    
    # Check if impacts are only '+' or '-'
    for imp in impacts:
        if imp not in ['+', '-']:
            print("Error: Impacts must be either '+' or '-'.")
            sys.exit(1)
    
    # Convert numeric_df to numpy for easier calculations
    data = numeric_df.values.astype(float)
    
    # 3. Normalize the decision matrix
    #    For each column, we calculate the denominator = sqrt(sum of squares of that column)
    #    Then data[:, j] = data[:, j] / denominator
    denom = np.sqrt((data**2).sum(axis=0))
    data_normalized = data / denom
    
    # 4. Multiply each column by its corresponding weight
    #    Normalize the weights first so that sum(weights) = 1 is not strictly required
    #    but is usually a recommended step. If the user wants them unnormalized, you can remove normalizing step.
    #    For standard TOPSIS, let's just take them as given and ensure they sum to 1 if you like.
    #    We'll assume the user has assigned them properly. You can normalize if required:
    # weights = np.array(weights) / sum(weights)
    
    weights = np.array(weights)
    data_weighted = data_normalized * weights
    
    # 5. Determine the Ideal Best (v+) and Ideal Worst (v-) for each column
    #    If impact is '+', ideal best = max, ideal worst = min
    #    If impact is '-', ideal best = min, ideal worst = max
    v_best = []
    v_worst = []
    for j, imp in enumerate(impacts):
        if imp == '+':
            v_best.append(np.max(data_weighted[:, j]))
            v_worst.append(np.min(data_weighted[:, j]))
        else:  # imp == '-'
            v_best.append(np.min(data_weighted[:, j]))
            v_worst.append(np.max(data_weighted[:, j]))
    
    v_best = np.array(v_best)
    v_worst = np.array(v_worst)
    
    # 6. Calculate Euclidean distance from ideal best and worst
    #    For each row i: 
    #       S+ = sqrt( sum( (x_ij - v_best_j)^2 ) )
    #       S- = sqrt( sum( (x_ij - v_worst_j)^2 ) )
    
    dist_best = np.sqrt(((data_weighted - v_best)**2).sum(axis=1))
    dist_worst = np.sqrt(((data_weighted - v_worst)**2).sum(axis=1))
    
    # 7. Calculate the performance score = dist_worst / (dist_best + dist_worst)
    performance_score = dist_worst / (dist_best + dist_worst)
    
    # 8. Rank the solutions based on the performance score (descending order)
    #    Higher score => better rank
    rank = performance_score.argsort()[::-1]  # indices of sorted scores in descending order
    ranks = np.empty_like(rank)
    ranks[rank] = np.arange(1, len(performance_score) + 1)
    
    # 9. Prepare the result dataframe
    result_df = df.copy()
    result_df['Topsis Score'] = performance_score
    result_df['Rank'] = ranks
    
    # 10. Save the result to output_file
    try:
        result_df.to_csv(output_file, index=False)
        print(f"TOPSIS analysis completed successfully. Output written to '{output_file}'.")
    except Exception as e:
        print(f"Error writing result to '{output_file}': {e}")
        sys.exit(1)


def main():
    # 1. Parse the command line arguments
    #    Usage: python YourRollNumber.py <InputDataFile> <Weights> <Impacts> <ResultFileName>
    if len(sys.argv) != 5:
        print("Usage: python YourRollNumber.py <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        print('Example: python 101556.py 101556-data.csv "1,1,1,2" "+,+,-,+" 101556-result.csv')
        sys.exit(1)
    
    script, input_file, weights_str, impacts_str, output_file = sys.argv
    
    # Process weights
    # Weights given like "1,1,1,2"
    try:
        weights = [float(w.strip()) for w in weights_str.split(',')]
    except ValueError:
        print("Error: Weights must be numeric and separated by commas, e.g. '1,1,1,2'.")
        sys.exit(1)
    
    # Process impacts
    # Impacts given like "+,+,-,+"
    impacts = [imp.strip() for imp in impacts_str.split(',')]
    
    # 2. Call the topsis function
    topsis(input_file, weights, impacts, output_file)


if __name__ == "__main__":
    main()
