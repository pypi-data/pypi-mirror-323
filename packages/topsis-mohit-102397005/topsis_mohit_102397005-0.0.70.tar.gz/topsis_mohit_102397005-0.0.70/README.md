# TOPSIS Package

This package implements the `TOPSIS` technique for Multi-Criteria Decision Making Problems.

## Installation

You can install the package using `pip`. First,run:
```
pip install topsis-mohit-102397005

import topsis_mohit_102397005
```

## Usage
After installing the package, you can use it from the command line.

## Command Line Usage
To use the TOPSIS package from the command line, run the following command:
```
python -m topsis_mohit_102397005.topsis_102397005 inputFileName weights impacts resultFileName
```

### Example
Suppose you have an input file `data.csv` with the following content:
```
Model,Price,Quality,Service:
M1,25000,7,8
M2,30000,8,6
M3,27500,9,7
M4,28000,6,9
```

You can run the following command:
```
python -m topsis_mohit_102397005.topsis_102397005 data.csv "0.25,0.25,0.5" "-,+,+" result.csv
```
This is the `result.csv` file created after running the command:
```
Model,Price,Quality,Service,TOPSIS Score,Rank
M1,25000,7,8,0.5345,2
M2,30000,8,6,0.3083,4
M3,27500,9,7,0.6912,1
M4,28000,6,9,0.4657,3
```

## Function Usage
You can also use the TOPSIS package by calling the function directly in your Python code.

### Example
```
inputFileName = 'data.csv'
weights = '0.25,0.25,0.5'
impacts = '-,+,+'
resultFileName = 'result.csv'

run_topsis(inputFileName, weights, impacts, resultFileName)
```

This will produce the same output as the command line example, saving the results to `result.csv`.

## Parameters

- `inputFileName`: The name of the input CSV file containing the data.
- `weights`: A string of weights separated by commas (e.g., "1,1,1").
- `impacts`: A string of impacts separated by commas, where each impact is either + or - (e.g., "+,+,-").
- `resultFileName`: The name of the output CSV file where the results will be saved.


## About
- `Author`: Mohit Bansal
- `Github`: https://github.com/Mohit-Bansal-31/Topsis-Mohit-102397005
- `Contact`: mohitbansal0031@gmail.com
- `Date`: 20-Jan-2025
