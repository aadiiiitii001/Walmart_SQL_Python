from flask import Flask
import pandas as pd
import os
from sqlalchemy import create_engine

app = Flask(__name__)

# --- Load environment variables ---
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "walmart_sales")

# --- Load Data ---
try:
    df = pd.read_csv("walmart_clean_data.csv")
    print("✅ Data loaded successfully. Shape:", df.shape)
except Exception as e:
    print("❌ Failed to load CSV:", e)
    df = pd.DataFrame()

# --- Connect to Database (optional) ---
try:
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
    print("✅ Database connection successful")
except Exception as e:
    print("⚠️ Database connection failed:", e)


# --- Home Route ---
@app.route('/')
def home():
    if df.empty:
        return "<h2>❌ No data available. Please check your CSV file.</h2>"

    # Auto-detect or compute Sales column
    sales_col = next((c for c in df.columns if 'sale' in c.lower()), None)

    if not sales_col:
        if 'unit_price' in df.columns and 'quantity' in df.columns:
            df['Sales'] = df['unit_price'] * df['quantity']
            sales_col = 'Sales'
        else:
            return f"<h2>⚠️ No 'sales' column found, and unable to compute one.</h2><br>Columns: {df.columns.tolist()}"

    # Compute summary stats
    total_sales = round(df[sales_col].sum(), 2)
    avg_sales = round(df[sales_col].mean(), 2)
    unique_branches = df['Branch'].nunique() if 'Branch' in df.columns else 0
    num_rows = len(df)

    # --- HTML Dashboard ---
    html = f"""
    <html>
        <head>
            <title>Walmart Data Analysis Dashboard</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: #f4f7fa;
                    padding: 40px;
                }}
                .container {{
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                    padding: 30px;
                    max-width: 600px;
                    margin: auto;
                }}
                h1 {{ color: #2a7ae4; text-align: center; }}
                p {{ font-size: 18px; }}
                .metric {{ font-weight: bold; color: #222; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Walmart Data Analysis</h1>
                <p><span class="metric">Total Records:</span> {num_rows}</p>
                <p><span class="metric">Detected Sales Column:</span> {sales_col}</p>
                <p><span class="metric">Total Sales:</span> ${total_sales:,.2f}</p>
                <p><span class="metric">Average Sales:</span> ${avg_sales:,.2f}</p>
                <p><span class="metric">Unique Branches:</span> {unique_branches}</p>
                <p style="text-align:center; margin-top:25px;">🚀 Deployment Successful on Render!</p>
            </div>
        </body>
    </html>
    """
    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
