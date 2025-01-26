import pandas as pd
import numpy as np
import sys

def read_input_file(input_file):
    """Read input file (CSV or Excel)."""
    try:
        if input_file.endswith('.xlsx'):
            return pd.read_excel(input_file)
        elif input_file.endswith('.csv'):
            return pd.read_csv(input_file)
        else:
            raise ValueError("Input file must be in .csv or .xlsx format.")
    except FileNotFoundError:
        raise FileNotFoundError("The specified input file was not found.")
    except Exception as e:
        raise Exception(f"Error reading input file: {e}")

def validate_inputs(input_file, weights, impacts):
    """Validate input file, weights, and impacts."""
    try:
        # Read input file
        df = read_input_file(input_file)

        # Ensure there are at least three columns
        if len(df.columns) < 3:
            raise ValueError("Input file must contain at least three columns.")

        # Convert weights and impacts to lists
        weights = [float(w.strip()) for w in weights.split(',')]
        impacts = [impact.strip() for impact in impacts.split(',')]

        # Validate numeric columns (from the second column onwards)
        for col in df.columns[1:]:
            if not pd.to_numeric(df[col], errors='coerce').notnull().all():
                raise ValueError(f"Column '{col}' contains non-numeric values.")

        # Validate the number of weights matches the number of numeric columns
        if len(weights) != len(df.columns) - 1:
            raise ValueError("The number of weights must match the number of numeric columns (excluding the first column).")

        # Validate the number of impacts matches the number of numeric columns
        if len(impacts) != len(df.columns) - 1:
            raise ValueError("The number of impacts must match the number of numeric columns (excluding the first column).")

        # Validate impacts are either '+' or '-'
        if not all(impact in ['+', '-'] for impact in impacts):
            raise ValueError("Impacts must be '+' or '-' and separated by commas.")

    except FileNotFoundError:
        raise FileNotFoundError("The specified input file was not found.")
    except Exception as e:
        raise Exception(f"Error validating inputs: {e}")

    return df, weights, impacts

def calculate_topsis(df, weights, impacts):
    """Perform TOPSIS calculation and return scores and ranks."""
    try:
        # Extract the numeric matrix, excluding the first column
        numeric_matrix = df.iloc[:, 1:].values.astype(float)

        # Step 1: Normalize the matrix
        normalized_matrix = numeric_matrix / np.sqrt(np.sum(numeric_matrix**2, axis=0))

        # Step 2: Apply weights to the normalized matrix
        weights = np.array(weights)
        weighted_normalized = normalized_matrix * weights

        # Step 3: Determine ideal best and worst values
        ideal_best = np.zeros(weighted_normalized.shape[1])
        ideal_worst = np.zeros(weighted_normalized.shape[1])

        for i in range(weighted_normalized.shape[1]):
            if impacts[i] == '+':
                ideal_best[i] = np.max(weighted_normalized[:, i])
                ideal_worst[i] = np.min(weighted_normalized[:, i])
            else:
                ideal_best[i] = np.min(weighted_normalized[:, i])
                ideal_worst[i] = np.max(weighted_normalized[:, i])

        # Step 4: Calculate separation measures
        s_best = np.sqrt(np.sum((weighted_normalized - ideal_best) ** 2, axis=1))
        s_worst = np.sqrt(np.sum((weighted_normalized - ideal_worst) ** 2, axis=1))

        # Step 5: Calculate TOPSIS scores
        topsis_scores = s_worst / (s_best + s_worst)

        # Step 6: Rank scores (higher score = better rank)
        ranks = topsis_scores.argsort()[::-1].argsort() + 1

        return topsis_scores, ranks

    except Exception as e:
        raise Exception(f"Error calculating TOPSIS: {e}")

def main():
    try:
        # Validate command-line arguments
        if len(sys.argv) != 5:
            print("Usage: python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>")
            sys.exit(1)

        input_file = sys.argv[1]
        weights = sys.argv[2]
        impacts = sys.argv[3]
        output_file = sys.argv[4]

        # Validate inputs and parse data
        df, processed_weights, processed_impacts = validate_inputs(input_file, weights, impacts)

        # Perform TOPSIS calculation
        topsis_scores, ranks = calculate_topsis(df, processed_weights, processed_impacts)

        # Add results to the dataframe
        df['Topsis Score'] = np.round(topsis_scores, 4)  # Round scores to 4 decimal places
        df['Rank'] = ranks

        # Save the results to the output file
        df.to_csv(output_file, index=False)
        print(f"Results successfully saved to '{output_file}'.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
