from flask import Flask, render_template_string
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import plotly.express as px
import os

app = Flask(__name__)

# --- Load data safely ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "Walmart.csv")  # Capital W

try:
    df = pd.read_csv(csv_path)
    print(f"✅ Data loaded successfully. Shape: {df.shape}")
except FileNotFoundError:
    print("⚠️ Walmart.csv not found — check filename or path.")
    df = pd.DataFrame()

# --- Convert to numeric ---
if not df.empty:
    df['unit_price'] = pd.to_numeric(df.get('unit_price', []), errors='coerce')
    df['quantity'] = pd.to_numeric(df.get('quantity', []), errors='coerce')

    # --- Compute Sales ---
    df['Sales'] = df['unit_price'] * df['quantity']
    print("🧮 Computed sales column successfully!")

    # --- Compute Metrics ---
    total_sales = df['Sales'].sum()
    avg_sales = df['Sales'].mean()
    unique_branches = df['Branch'].nunique() if 'Branch' in df.columns else 0

    # --- Create Bar Chart ---
    try:
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
    except Exception as e:
        sales_chart_html = f"<p>⚠️ Chart could not be generated: {e}</p>"
else:
    total_sales = avg_sales = unique_branches = 0
    sales_chart_html = "<p>⚠️ No data available to plot.</p>"

# --- Database connection (optional) ---
try:
    engine = create_engine("mysql+pymysql://root:password@localhost:3306/testdb")
    with engine.connect() as conn:
        print("✅ Database connection successful")
except Exception as e:
    print(f"⚠️ Database connection failed: {e}")

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
        sales_chart_html=sales_chart_html
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
