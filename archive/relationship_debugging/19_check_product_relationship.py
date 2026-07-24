import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

catalog = pd.read_csv(
    PROJECT_ROOT /
    "data" /
    "processed" /
    "dashboard_metrics" /
    "product_catalog.csv"
)

sentiment = pd.read_csv(
    PROJECT_ROOT /
    "data" /
    "processed" /
    "dashboard_metrics" /
    "product_sentiment_summary.csv"
)


print("Product Catalog:")
print(f"Rows: {len(catalog)}")
print(f"Unique product names: {catalog['product_name'].nunique()}")
print(f"Duplicates: {catalog['product_name'].duplicated().sum()}")


print("\nProduct Sentiment:")
print(f"Rows: {len(sentiment)}")
print(f"Unique product names: {sentiment['product_name'].nunique()}")
print(f"Duplicates: {sentiment['product_name'].duplicated().sum()}")