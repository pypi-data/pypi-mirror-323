# TOPSIS Command Line Program
# Pranav Dev Khindria 102203279
A Python program to perform the **TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)** analysis on a given dataset.

## Description

TOPSIS is a multi-criteria decision-making approach that ranks a set of alternatives based on their distance to the ideal best and ideal worst solutions. This program:

1. **Normalizes** the criteria values.
2. Applies **user-defined weights**.
3. Identifies the **ideal best (v+)** and **ideal worst (v-)** values.
4. Calculates the **Euclidean distance** of each alternative from these ideal solutions.
5. Computes the **TOPSIS score** (`dist_worst / (dist_best + dist_worst)`).
6. **Ranks** the alternatives (higher score → better rank).

## Requirements

- **Python 3.x**
- **pandas** (Install via `pip install pandas`)
- **numpy** (Install via `pip install numpy`)

## File Structure

- **Script Name**: `main.py`   

- **Input CSV File**: `102203279-data.csv`  
  - Must contain at least 3 columns.
  - The **first column** is the identifier (e.g., M1, M2, ...).
  - The **remaining columns** are numeric (no missing or non-numeric values).

- **Output CSV File**: `102203279-result.csv`  
  - Will contain the original columns plus two additional columns:  
    - **Topsis Score**  
    - **Rank**

## Usage

Open a terminal/command prompt in the directory containing your Python script and run:

```bash
python main.py <InputDataFile> <Weights> <Impacts> <ResultFileName>
```

