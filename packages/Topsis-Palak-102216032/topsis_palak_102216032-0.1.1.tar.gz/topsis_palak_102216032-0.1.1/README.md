# Topsis-Palak-102216032

## Overview

`Topsis-Palak-102216032` is a Python package that implements the **TOPSIS** (Technique for Order of Preference by Similarity to Ideal Solution) method for multi-criteria decision analysis (MCDA). This package allows you to evaluate and rank alternatives based on multiple criteria, considering both positive and negative impacts of each criterion.

The implementation supports reading input data from a CSV file, applying weights to the criteria, and calculating the TOPSIS score and rankings. The final results are saved to an output CSV file with the TOPSIS score and corresponding rank for each alternative.

## Features

- Normalize the decision matrix.
- Apply weights to the normalized data.
- Identify the ideal best and worst solutions based on the specified impacts.
- Calculate the distances to the ideal best and worst solutions.
- Compute the TOPSIS score for each alternative.
- Rank the alternatives based on the TOPSIS score.
- Save the results in a CSV file.

## Installation

You can install this package from PyPI using the following command:

```bash
pip Topsis-Palak-102216032
```bash


## Usage
Please provide the filename for the CSV, including the .csv extension. After that, enter the weights vector with values separated by commas. Following the weights vector, input the impacts vector, where each element is denoted by a plus (+) or minus (-) sign. Lastly, specify the output file name along with the .csv extension.

```py -m topsis.__main__ [input_file_name.csv] [weight as string] [impact as string] [result_file_name.csv]```

## Example Usage
The below example is for the data have 5 columns.
```topsis-ridham input.csv "1,1,2,0.5,0.75" "+,+,-,-,-" output.csv ```

## Example Dataset

Fund Name | P1 | P2 | P3 | P4 | P5
------------ | ------------- | ------------ | ------------- | ------------ | ------------
M1 | 0.78 | 0.61 | 5.5 | 34.7 | 10.4
M2 | 0.88 | 0.77 | 5 | 58.4 | 16.26
M3 | 0.61 | 0.37 | 5.9 | 39.9 | 11.7
M4 | 0.76 | 0.58 | 4.2 | 57.7 | 15.81
M5 | 0.84 | 0.71 | 3.2 | 48 | 13.19
M6 | 0.76 | 0.58 | 4 | 68.8 | 18.54
M7 | 0.81 | 0.66 | 6.5 | 38.2 | 11.54
M8 | 0.81 | 0.66 | 3.2 | 32.8 | 9.37

## Output Dataset
Fund Name | P1 | P2 | P3 | P4 | P5 | TOPSIS Score | Rank
------------ | ------------- | ------------ | ------------- | ------------ | ------------ | ------------ | ------------
M1 | 0.78 | 0.61 | 5.5 | 34.7 | 10.4 | 0.45384759973942024 | 6
M2 | 0.88 | 0.77 | 5 | 58.4 | 16.26 | 0.5250616666395651 | 5
M3 | 0.61 | 0.37 | 5.9 | 39.9 | 11.7 | 0.286469615636936 | 8
M4 | 0.76 | 0.58 | 4.2 | 57.7 | 15.81 | 0.6022625270239917 | 3
M5 | 0.84 | 0.71 | 3.2 | 48 | 13.19 | 0.8452645767159974 | 2
M6 | 0.76 | 0.58 | 4 | 68.8 | 18.54 | 0.5852919015001125 | 4
M7 | 0.81 | 0.66 | 6.5 | 38.2 | 11.54 | 0.3427884605083087 | 7
M8 | 0.81 | 0.66 | 3.2 | 32.8 | 9.37 | 0.8900689209819633 | 1

<br>

## Important Points
1) There should be only numeric columns except the first column i.e. Fund Name.
2) Input file must contain atleast three columns.

<br>