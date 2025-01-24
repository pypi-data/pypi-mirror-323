# Title
A Python package to perform TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) analysis.

# Description
This package implements the TOPSIS method for Multi-Criteria Decision-Making (MCDM). It takes an input dataset, weights, and impacts to calculate scores and ranks for the provided alternatives, helping users to make better decisions.

# Features
Implements the TOPSIS method for decision-making.
Supports both positive and negative impacts.
Provides a simple command-line interface for easy usage.

# Installation
Explain how users can install your package. Include steps for installation via pip.

pip install Topsis-YourName-RollNumber

If the package isn’t uploaded to PyPI yet, include instructions for installing it from the source code:
git clone https://github.com/abhirajsinghjhajj/Topsis_Abhiraj_Singh_Jhajj_102217094.git
cd Topsis_Abhiraj_Singh_Jhajj_102217094
pip install .

# Usage
Provide examples of how to use the package or run the program. Include command-line usage examples.
Example:
python 101556.py 101556-data.csv "1,1,1,2" "+,+,-,+" 101556-result.csv

Explain what each parameter means:
101556.py: The Python script file.
101556-data.csv: The input file containing the data.
"1,1,1,2": Weights for each criterion.
"+,+,-,+": Impacts for each criterion (+ for benefit, - for cost).
101556-result.csv: The output file to save the result.