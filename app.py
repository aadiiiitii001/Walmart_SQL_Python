import pandas as pd
import os
from sqlalchemy import create_engine

# Load environment variables (optional if running locally)
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "walmart_sales")

# Load cleaned Walmart data
df = pd.read_csv("walmart_clean_data.csv")

print("✅ Data loaded successfully. Shape:", df.shape)

# Example: connect to MySQL database (optional)
try:
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
    print("✅ Database connection successful")
except Exception as e:
    print("❌ Database connection failed:", e)

# Simple output to verify Render logs
print("🚀 Walmart Data Analysis project deployed successfully!")
