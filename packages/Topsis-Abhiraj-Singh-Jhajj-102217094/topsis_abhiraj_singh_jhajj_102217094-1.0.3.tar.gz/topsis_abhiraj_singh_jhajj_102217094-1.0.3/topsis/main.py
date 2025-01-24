import sys
import pandas as pd
from .topsis import topsis

def main():
    try:
        if len(sys.argv) != 5:
            raise ValueError("Usage: python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        
        input_file = sys.argv[1]
        weights = [float(w) for w in sys.argv[2].split(',')]
        impacts = sys.argv[3].split(',')
        result_file = sys.argv[4]

        data = pd.read_csv(input_file)

        result = topsis(data, weights, impacts)

        result.to_csv(result_file, index=False)
        print(f"Results saved to {result_file}")

    except Exception as e:
        print(f"Error: {e}")
