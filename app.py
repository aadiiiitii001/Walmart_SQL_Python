from flask import Flask, render_template_string
import pandas as pd
import pymysql
from sqlalchemy import create_engine

app = Flask(__name__)

# Load dataset
try:
    df = pd.read_csv("walmart_clean_data.csv")
    print(f"✅ Data loaded successfully. Shape: {df.shape}")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    df = pd.DataFrame()

# Database connection (optional – modify if needed)
try:
    engine = create_engine("mysql+pymysql://root:password@localhost/walmart_db")
    print("✅ Database connection successful")
except Exception as e:
    print(f"⚠️ Database connection failed: {e}")

@app.route("/")
def home():
    try:
        if df.empty:
            return "<h3>❌ No data available!</h3>"

        # Convert data types safely
        df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')

        # Compute sales
        df['Sales'] = df['unit_price'] * df['quantity']
        df['Sales'].fillna(0, inplace=True)

        print("🧮 Computed sales column successfully!")

        # Calculate summary metrics
        total_records = len(df)
        total_sales = round(df['Sales'].sum(), 2)
        avg_sales = round(df['Sales'].mean(), 2)
        unique_branches = df['Branch'].nunique()

        # HTML template for dashboard
        html = f"""
        <html>
        <head>
            <title>Walmart Data Analysis</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    text-align: center;
                    background-color: #f4f6f8;
                    color: #333;
                    padding: 40px;
                }}
                h1 {{ color: #0078d7; }}
                .card {{
                    display: inline-block;
                    background: white;
                    margin: 20px;
                    padding: 20px 40px;
                    border-radius: 12px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                }}
                .footer {{
                    margin-top: 30px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <h1>📊 Walmart Data Analysis</h1>
            <div class="card"><h3>Total Records:</h3><p>{total_records}</p></div>
            <div class="card"><h3>Total Sales:</h3><p>${total_sales:,.2f}</p></div>
            <div class="card"><h3>Average Sales:</h3><p>${avg_sales:,.2f}</p></div>
            <div class="card"><h3>Unique Branches:</h3><p>{unique_branches}</p></div>
            <div class="footer">🚀 Deployment Successful on Render!</div>
        </body>
        </html>
        """
        return render_template_string(html)

    except Exception as e:
        print(f"❌ Error in home route: {e}")
        return f"<h3>Internal Server Error: {e}</h3>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
