import sys
import pandas as pd
import numpy as np



def validate_inputs(inputFileName=None, weights=None, impacts=None, resultFileName=None):
    if inputFileName is None or weights is None or impacts is None or resultFileName is None:
        if len(sys.argv) != 5:
            print("Error: Incorrect number of parameters. Usage: python script.py inputFileName weights impacts resultFileName")
            sys.exit(1)
        inputFileName, weights, impacts, resultFileName = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    
    # Check if weights and impacts are separated by commas
    weights = weights.split(',')
    impacts = impacts.split(',')
    
    # Check if impacts are either +ve or -ve
    if not all(i in ['+', '-'] for i in impacts):
        print("Error: Impacts must be either '+' or '-'")
        sys.exit(1)

    # Check if the number of weights, impacts, and columns are the same
    try:
        df = pd.read_csv(inputFileName)
    except FileNotFoundError:
        print(f"Error: File '{inputFileName}' not found.")
        sys.exit(1)

    if df.shape[1] < 3:
        print("Error: Input file must contain three or more columns.")
        sys.exit(1)

    if len(weights) != len(impacts) or len(weights) != (df.shape[1] - 1):
        print("Error: Number of weights, impacts, and columns (from 2nd to last columns) must be the same.")
        sys.exit(1)

    # Check if columns from 2nd to last contain numeric values only
    for col in df.columns[1:]:
        if not pd.api.types.is_numeric_dtype(df[col]):
            print(f"Error: Column '{col}' must contain numeric values only.")
            sys.exit(1)
            
    return df, weights, impacts

def topsis(inputFileName, weights, impacts, resultFileName):
    df, weights, impacts = validate_inputs(inputFileName, weights, impacts, resultFileName)
    
    # Normalize the decision matrix
    normalized_df = df.iloc[:, 1:].apply(lambda x: x / np.sqrt((x**2).sum()), axis=0)
    
    # Apply weights
    weights = np.array(weights, dtype=float)
    weighted_df = normalized_df * weights
    
    # Determine ideal best and ideal worst
    ideal_best = []
    ideal_worst = []
    for i, impact in enumerate(impacts):
        if impact == '+':
            ideal_best.append(weighted_df.iloc[:, i].max())
            ideal_worst.append(weighted_df.iloc[:, i].min())
        else:
            ideal_best.append(weighted_df.iloc[:, i].min())
            ideal_worst.append(weighted_df.iloc[:, i].max())
    
    # Calculate the distance to ideal best and ideal worst
    distance_to_best = np.sqrt(((weighted_df - ideal_best) ** 2).sum(axis=1))
    distance_to_worst = np.sqrt(((weighted_df - ideal_worst) ** 2).sum(axis=1))
    
    # Calculate the TOPSIS score
    topsis_score = distance_to_worst / (distance_to_best + distance_to_worst)
    
    # Add the TOPSIS score to the original dataframe
    df['TOPSIS Score'] = topsis_score
    
    # Rank the scores
    df['Rank'] = df['TOPSIS Score'].rank(ascending=False)
    
    # Save the result to the result file
    df.to_csv(resultFileName, index=False)
    print(f"Results saved to '{resultFileName}'")

# 5 arguments used as we also have script name as an argument
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Error: Incorrect number of parameters. Usage: python script.py inputFileName weights impacts resultFileName")
        sys.exit(1)
    
    inputFileName = sys.argv[1]
    weights = sys.argv[2]
    impacts = sys.argv[3]
    resultFileName = sys.argv[4]
    
    topsis(inputFileName, weights, impacts, resultFileName)