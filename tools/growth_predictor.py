"""
growth_predictor_2.py

A robust tool for predicting animal weight growth based on historical CSV data.
It handles dates in column headers (DD/MM/YYYY format) and sparse (NA) data.

Usage:
    python growth_predictor_2.py <csv_file> [days_ahead]

Arguments:
    csv_file: Path to the CSV file containing the data.
    days_ahead: Number of days to predict into the future (default: 30).
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

def parse_csv_with_dates(csv_path):
    """
    Reads a CSV file and parses the column headers as dates.
    Assumes the first few columns are metadata (e.g., Tag, Category) 
    and the rest are dates.
    """
    if not os.path.exists(csv_path):
        print(f"Error: File '{csv_path}' not found.")
        return None

    try:
        df = pd.read_csv(csv_path, header=0)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

    # Identify date columns (excluding metadata columns like 'Official tag', 'Category')
    # We assume columns after the third one are dates.
    date_cols = df.columns[3:]
    
    parsed_dates = {}
    valid_cols = []
    
    for col in date_cols:
        try:
            # Attempt to parse DD/MM/YYYY format
            dt = datetime.strptime(str(col), "%d/%m/%Y")
            parsed_dates[col] = dt
            valid_cols.append(col)
        except ValueError:
            # If a column isn't a valid date, skip it or handle as metadata
            pass

    if not valid_cols:
        print("Error: No valid date columns found in headers.")
        return None

    # Sort columns chronologically
    valid_cols.sort(key=lambda x: parsed_dates[x])
    
    # Reorder dataframe to put dates in chronological order for regression
    df = df[list(df.columns[:3]) + valid_cols]
    
    return df, parsed_dates, valid_cols

def calculate_predictions(df, parsed_dates, valid_cols, days_ahead=30):
    """
    Calculates growth trends and predictions for each animal row.
    """
    if df is None or len(df) == 0:
        return []

    results = []
    
    # Determine the target prediction date
    last_date_obj = parsed_dates[valid_cols[-1]]
    pred_date_obj = last_date_obj + timedelta(days=days_ahead)
    
    print(f"Analysis Start: {valid_cols[0]}")
    print(f"Analysis End (Last Record): {valid_cols[-1]}")
    print(f"Prediction Target Date: {pred_date_obj.strftime('%d/%m/%Y')}")
    print("-" * 100)
    
    # Tag and Category column names are assumed to be the first 3
    tag_col = df.columns[0]
    
    for index, row in df.iterrows():
        tag = row[tag_col]
        
        # Extract valid (Date, Weight) pairs
        data_points = []
        for col in valid_cols:
            weight = row[col]
            if pd.notna(weight):
                try:
                    weight_val = float(weight)
                    data_points.append({
                        'date': parsed_dates[col],
                        'weight': weight_val
                    })
                except ValueError:
                    continue
        
        # Need at least 2 points for a linear regression
        if len(data_points) < 2:
            continue
            
        # Sort by date to ensure timeline accuracy
        data_points.sort(key=lambda x: x['date'])
        
        # --- Linear Regression (y = mx + c) ---
        # x = days elapsed since the first recorded date
        # y = weight
        x_vals = [(p['date'] - data_points[0]['date']).days for p in data_points]
        y_vals = [p['weight'] for p in data_points]
        
        # Calculate slope (ADG - Average Daily Gain) and intercept
        # polyfit returns coefficients for a polynomial of degree 1 (linear)
        slope, intercept = np.polyfit(x_vals, y_vals, 1)
        
        # --- Calculate Projection ---
        # Use the *last actual recorded weight* as the base for prediction
        # This prevents extrapolation error if the very last date had NA
        current_weight = data_points[-1]['weight']
        
        # Days between last recorded date and prediction date
        days_diff = (pred_date_obj - data_points[-1]['date']).days
        
        # Predicted Weight = Current + (ADG * Days_Diff)
        predicted_weight = current_weight + (slope * days_diff)
        
        # Gains
        total_gain = predicted_weight - current_weight
        weekly_gain = slope * 7  # Daily Gain * 7
        
        results.append({
            'Tag': tag,
            'Current': current_weight,
            'Predicted': predicted_weight,
            'Total_Gain': total_gain,
            'Weekly_Gain': weekly_gain
        })
        
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python growth_predictor_2.py <csv_file> [days_ahead]")
        print("Example: python growth_predictor_2.py cattle_weights.csv 30")
        sys.exit(1)

    csv_file = sys.argv[1]
    days_ahead = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    # 1. Parse Data
    df, parsed_dates, valid_cols = parse_csv_with_dates(csv_file)
    
    if df is None:
        sys.exit(1)

    # 2. Calculate Predictions
    results = calculate_predictions(df, parsed_dates, valid_cols, days_ahead)

    if not results:
        print("No valid growth data found to predict.")
        return

    # 3. Display Results
    print(f"{'Official Tag':<15} | {'Current (kg)':<14} | {'Predicted (kg)':<15} | {'30d Gain (kg)':<15} | {'Weekly Gain (kg)':<15}")
    print("-" * 100)
    
    for res in results:
        # Format output nicely
        print(f"{res['Tag']:<15} | {res['Current']:<14.1f} | {res['Predicted']:<15.1f} | {res['Total_Gain']:<+15.1f} | {res['Weekly_Gain']:<+15.1f}")

    # 4. (Optional) Save to CSV
    output_df = pd.DataFrame(results)
    output_filename = "growth_predictions.csv"
    output_df.to_csv(output_filename, index=False)
    print(f"\nDetailed results saved to '{output_filename}'")

if __name__ == "__main__":
    main()