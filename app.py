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

# --- Clean, Convert, and Compute Metrics ---
if not df.empty:
    # 1️⃣ Clean currency column
    df['unit_price'] = (
        df['unit_price']
        .astype(str)
        .replace('[\$,]', '', regex=True)  # Remove $ and commas
        .astype(float)
    )

    # 2️⃣ Ensure quantity is numeric
    df['quantity'] = pd.to_numeric(df.get('quantity', 0), errors='coerce').fillna(0)

    # 3️⃣ Compute Sales
    df['Sales'] = df['unit_price'] * df['quantity']
    print("🧮 Computed Sales column successfully!")

    # 4️⃣ Summary Metrics
    total_sales = df['Sales'].sum()
    avg_sales = df['Sales'].mean()
    unique_branches = df['Branch'].nunique() if 'Branch' in df.columns else 0

    # 5️⃣ Data Health Check
    missing_values = df.isna().sum().sum()
    invalid_rows = df[df['Sales'].isna()].shape[0]
else:
    total_sales = avg_sales = unique_branches = missing_values = invalid_rows = 0

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
    body { font-family: Arial, sans-serif; background: #f4f4f9; text-align: center; padding: 30px; }
    h1 { color: #2d3436; }
    .card { background: white; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 20px; width: 350px; margin: 20px auto; }
    .metric { font-size: 20px; color: #0984e3; }
    .chart { width: 80%; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .health { margin-top: 20px; font-size: 16px; color: #636e72; }
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

  <div class="health">
    <h3>🧾 Data Health Check</h3>
    <p>Missing or invalid entries detected: <strong>{{ missing_values }}</strong></p>
    <p>Rows with invalid Sales values: <strong>{{ invalid_rows }}</strong></p>
  </div>

  <p>🚀 Deployment Successful on Render!</p>
</body>
</html>
"""

# --- Flask Route ---
@app.route("/")
def home():
    return render_template_string(
        html,
        total_records=len(df),
        total_sales=f"{total_sales:,.2f}",
        avg_sales=f"{avg_sales:,.2f}",
        unique_branches=unique_branches,
        missing_values=missing_values,
        invalid_rows=invalid_rows,
        sales_chart_html=sales_chart_html
    )

# --- Run the App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render sets PORT dynamically
    app.run(host="0.0.0.0", port=port)

