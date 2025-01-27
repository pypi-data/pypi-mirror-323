# TOPSIS Package

This package implements the TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) method for decision-making.

## Installation
```bash
pip install topsis

## To run file :
pyhton topsis.py <input_file_location> "weights" "impacts" <output_file_location.csv>


Where:
<input_file> is the path to the CSV file containing the decision matrix.
<weights> is a comma-separated list of weights for the criteria (e.g., 1,1,1,1).
<impacts> is a comma-separated list of impact directions for the criteria (e.g., +,+,-,- where + indicates a benefit criterion and - indicates a cost criterion).
<output_file> is the path where the results will be saved, including the TOPSIS score and rank for each alternative.