import os
from flask import Flask, render_template_string
import pandas as pd
import plotly.express as px

app = Flask(__name__)

# --- Locate and Load the CSV File ---
try:
    csv_path = os.path.join(os.path.dirname(__file__), "walmart.csv")
    df = pd.read_csv(csv_path)
    print(f"✅ Data loaded successfully. Shape: {df.shape}")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    df = pd.DataFrame()

# --- Clean & Prepare Data ---
if not df.empty:
    # Clean currency symbols and commas from unit_price
    if 'unit_price' in df.columns:
        df['unit_price'] = (
            df['unit_price']
            .astype(str)
            .replace(r'[\$,]', '', regex=True)   # <-- raw string (fixes warning)
        )

    # Convert numeric columns safely
    df['unit_price'] = pd.to_numeric(df.get('unit_price', 0), errors='coerce')
    df['quantity'] = pd.to_numeric(df.get('quantity', 0), errors='coerce')

    # Compute sales
    df['Sales'] = df['unit_price'] * df['quantity']
    print("🧮 Computed sales column successfully!")

    # --- Data Health Check ---
    missing_count = df.isna().sum().sum()
    invalid_sales_count = df['Sales'].isna().sum()

    # Drop invalid rows (keep only clean data)
    df = df.dropna(subset=['unit_price', 'quantity', 'Sales'])

    total_sales = df['Sales'].sum()
    avg_sales = df['Sales'].mean()
    unique_branches = df['Branch'].nunique() if 'Branch' in df.columns else 0
else:
    total_sales = avg_sales = unique_branches = missing_count = invalid_sales_count = 0

# --- Create Bar Chart (Sales by Branch) ---
try:
    if not df.empty and 'Branch' in df.columns:
        branch_sales = df.groupby('Branch')['Sales'].sum().reset_index()
        fig = px.bar(
            branch_sales,
            x='Branch',
            y='Sales',
            title='Total Sales by Branch',
            text_auto='.2s',
            color='Sales',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='black')
        )
        sales_chart_html = fig.to_html(full_html=False)
    else:
        sales_chart_html = "<p>⚠️ Chart data unavailable.</p>"
except Exception as e:
    sales_chart_html = f"<p>⚠️ Chart generation error: {e}</p>"

# --- HTML Template ---
html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Walmart Data Analysis</title>
  <style>
    body { font-family: Arial; background: #f4f4f9; text-align: center; padding: 30px; }
    h1 { color: #2d3436; }
    .card { background: white; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 20px; width: 350px; margin: 20px auto; }
    .metric { font-size: 20px; color: #0984e3; }
    .chart { width: 80%; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
  </style>
</head>
<body>
  <h1>📊 Walmart Data Analysis</h1>
  <div class="card">
    <p><strong>Total Records:</strong> {{ total_records }}</p>
    <p class="metric"><strong>Total Sales:</strong> ${{ total_sales }}</p>
    <p class="metric"><strong>Average Sales:</strong> ${{ avg_sales }}</p>
    <p class="metric"><strong>Unique Branches:</strong> {{ unique_branches }}</p>
  </div>
  
  <div class="chart">
    <h2>📈 Sales by Branch</h2>
    {{ sales_chart_html|safe }}
  </div>

  <div class="card">
    <h2>🧾 Data Health Check</h2>
    <p>Missing or invalid entries detected: {{ missing_count }}</p>
    <p>Rows with invalid Sales values: {{ invalid_sales_count }}</p>
  </div>

  <p>🚀 Deployment Successful on Render!</p>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(
        html,
        total_records=len(df),
        total_sales=f"{total_sales:,.2f}",
        avg_sales=f"{avg_sales:,.2f}",
        unique_branches=unique_branches,
        sales_chart_html=sales_chart_html,
        missing_count=missing_count,
        invalid_sales_count=invalid_sales_count
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
