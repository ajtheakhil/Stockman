import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
import json

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: python dashboard_creator.py <csv_path> <output_html_path>"}))
        sys.exit(1)

    csv_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(csv_path):
        print(json.dumps({"error": f"File not found: {csv_path}"}))
        sys.exit(1)

    try:
        # Load Data
        df = pd.read_csv(csv_path)
        
        # Identify columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        
        if len(numeric_cols) == 0 and len(categorical_cols) == 0:
            print(json.dumps({"error": "Could not identify numeric or categorical columns."}))
            sys.exit(1)

        # Initialize Plotly Figure
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{"type": "xy"}, {"type": "xy"}], 
                   [{"type": "xy"}, {"type": "xy"}]],
            subplot_titles=("Distribution of Numerical Data", "Top Categories", "Correlation", "Price/Cost Analysis")
        )

        # 1. Histogram of first numeric column (Distribution)
        if len(numeric_cols) > 0:
            fig.add_trace(go.Histogram(x=df[numeric_cols[0]], name=f"Distribution of {numeric_cols[0]}"), row=1, col=1)

        # 2. Bar Chart of first categorical column (Frequency)
        if len(categorical_cols) > 0:
            val_counts = df[categorical_cols[0]].value_counts().head(5)
            fig.add_trace(go.Bar(x=val_counts.index, y=val_counts.values, name=f"Top 5 {categorical_cols[0]}"), row=1, col=2)

        # 3. Scatter Plot if we have 2+ numeric columns (Correlation)
        if len(numeric_cols) >= 2:
            fig.add_trace(go.Scatter(x=df[numeric_cols[0]], y=df[numeric_cols[1]], mode='markers', name='Correlation'), row=2, col=1)
        else:
            # Fallback if no correlation possible
            fig.add_trace(go.Bar(y=[len(df)], x=["Total Records"], name="Total Records"), row=2, col=1)

        # 4. Box plot of numeric columns (Outlier detection)
        if len(numeric_cols) > 0:
            # Use the last numeric column as the target for the box plot (e.g., Price)
            target_col = numeric_cols[-1]
            fig.add_trace(go.Box(y=df[target_col], name=f"Box Plot: {target_col}", boxpoints='all', jitter=0.3, pointpos=-1.8), row=2, col=2)

        # Layout
        fig.update_layout(height=800, width=1000, title_text="Auto-Generated Data Dashboard", showlegend=False)
        fig.update_xaxes(title_text="Value", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_xaxes(title_text="Category", row=1, col=2)
        fig.update_yaxes(title_text="Count", row=1, col=2)
        
        if len(numeric_cols) >= 2:
            fig.update_xaxes(title_text=numeric_cols[0], row=2, col=1)
            fig.update_yaxes(title_text=numeric_cols[1], row=2, col=1)

        # Save to a serveable location within the UI dist folder
        # This ensures the HTML file is accessible via the web server
        serveable_path = os.path.join('tools', 'ui', 'dist', 'dashboards', output_path)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(serveable_path), exist_ok=True)
        
        fig.write_html(serveable_path)
        
        # Also save to the original relative path for local access
        fig.write_html(output_path)

        print(json.dumps({"status": "success", "message": f"Dashboard created at {serveable_path}"}))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
