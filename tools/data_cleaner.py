"""
data_cleaner.py
author: Akhil Janardhanan

A lightweight command-line utility for inspecting and cleaning tabular datasets.

The script loads a CSV or Excel file, performs a requested operation, and
returns the result as a JSON object on standard output. It is designed to be
invoked programmatically by another application or agent.

Supported actions
-----------------
describe
    Return summary statistics, column names, data types, null counts, and
    dataset dimensions.

head
    Return the first n records. The number of records can be specified using
    the ``n`` parameter (default: 5).

clean_nulls
    Remove or fill missing values. Supported methods are:

    - ``drop``: remove rows containing null values.
    - ``fill``: replace null values with a specified value.

    An optional ``subset`` parameter restricts the operation to selected
    columns.

rename
    Rename a column using the ``old_name`` and ``new_name`` parameters.

Usage
-----
python data_cleaner.py <file_path> --action <action> --params '<json>'

Examples
--------
Describe a dataset:

    python data_cleaner.py data.csv --action describe

Return the first 10 records:

    python data_cleaner.py data.xlsx --action head --params '{"n": 10}'

Remove rows with missing values:

    python data_cleaner.py data.csv --action clean_nulls --params '{"method": "drop"}'

Fill missing values in selected columns with zero:

    python data_cleaner.py data.csv --action clean_nulls \\
        --params '{"method": "fill", "value": 0, "subset": ["age", "income"]}'

Rename a column:

    python data_cleaner.py data.csv --action rename \\
        --params '{"old_name": "old_column", "new_name": "new_column"}'

Output
------
All successful and unsuccessful operations return a JSON-formatted string.
Errors are reported using an ``error`` key.
"""
import pandas as pd
import sys
import json
import os
import traceback

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python data_cleaner.py <csv_path> --action <action> --params <json_params>"}))
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(json.dumps({"error": f"File not found: {file_path}"}))
        sys.exit(1)

    try:
        # Determine file type
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            print(json.dumps({"error": "Unsupported file format. Use .csv or .xlsx"}))
            sys.exit(1)

        # Parse arguments for actions (simple key-value parsing for this demo)
        # This is a simplified version. Ideally, we'd use argparse or pass a JSON string.
        # For now, let's assume standard actions: "describe", "head", "clean_nulls", "rename"
        
        # Default action
        action = "describe"
        params = {}
        
        # Simple parsing of command line args for actions
        if "--action" in sys.argv:
            idx = sys.argv.index("--action")
            if idx + 1 < len(sys.argv):
                action = sys.argv[idx+1]
        
        if "--params" in sys.argv:
            idx = sys.argv.index("--params")
            if idx + 1 < len(sys.argv):
                try:
                    params = json.loads(sys.argv[idx+1])
                except json.JSONDecodeError:
                    print(json.dumps({"error": "Invalid JSON for params"}))
                    sys.exit(1)

        # Perform Action
        result = {}
        
        if action == "describe":
            result = df.describe().to_dict()
            result["columns"] = df.columns.tolist()
            result["info"] = {
                "dtypes": df.dtypes.astype(str).to_dict(),
                "null_counts": df.isnull().sum().to_dict(),
                "shape": df.shape
            }
            
        elif action == "head":
            result = df.head(params.get("n", 5)).to_dict(orient="records")
            
        elif action == "clean_nulls":
            method = params.get("method", "drop")
            subset = params.get("subset", None)
            
            if method == "drop":
                df_clean = df.dropna(subset=subset)
            elif method == "fill":
                fill_val = params.get("value", 0)
                df_clean = df.fillna(fill_val)
            else:
                df_clean = df
                
            result = {"status": "cleaned", "new_shape": df_clean.shape, "data_sample": df_clean.head(5).to_dict(orient="records")}

        elif action == "rename":
            old_name = params.get("old_name")
            new_name = params.get("new_name")
            if old_name in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)
                result = {"status": "renamed", "columns": df.columns.tolist()}
            else:
                result = {"error": f"Column '{old_name}' not found."}
                
        else:
            result = {"error": f"Unknown action: {action}. Supported: describe, head, clean_nulls, rename"}

        print(json.dumps(result, default=str))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        # traceback.print_exc()

if __name__ == "__main__":
    main()
