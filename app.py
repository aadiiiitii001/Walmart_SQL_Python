from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)  # ✅ Flask app instance

# Load dataset
df = pd.read_csv("walmart_clean_data.csv")

@app.route('/')
def home():
    total_sales = round(df['Weekly_Sales'].sum(), 2)
    avg_sales = round(df['Weekly_Sales'].mean(), 2)
    top_store = df.groupby('Store')['Weekly_Sales'].sum().idxmax()
    return f"""
    <h2>🚀 Walmart Data Analysis</h2>
    <p>Total Sales: ${total_sales:,}</p>
    <p>Average Weekly Sales: ${avg_sales:,}</p>
    <p>Top Store: {top_store}</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
