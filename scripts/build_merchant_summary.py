import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]



# File paths
METRICS_DIR = PROJECT_ROOT / "data" / "processed" / "dashboard_metrics"

MERCHANT_FILE = (
    METRICS_DIR /
    "merchant_sentiment_summary.csv"
)

QUALITY_FILE = (
    METRICS_DIR /
    "review_quality_metrics.csv"
)

RISK_FILE = (
    METRICS_DIR /
    "product_risk_analysis.csv"
)

OUTPUT_FILE = (
    METRICS_DIR /
    "merchant_dashboard_summary.csv"
)



# Load data
print("Loading dashboard datasets...")

merchant_df = pd.read_csv(
    MERCHANT_FILE
)

quality_df = pd.read_csv(
    QUALITY_FILE
)

risk_df = pd.read_csv(
    RISK_FILE
)



# Count risk products
risk_summary = (
    risk_df
    .groupby("merchant")
    .agg(

        total_products=(
            "product_name",
            "count"
        ),

        medium_risk_products=(
            "risk_category",
            lambda x: (x == "Medium").sum()
        ),

        high_risk_products=(
            "risk_category",
            lambda x: (x == "High").sum()
        )

    )
    .reset_index()
)



# Merge datasets
summary = merchant_df.merge(
    quality_df,
    on="merchant",
    how="left",
    suffixes=("", "_quality")
)

summary = summary.merge(
    risk_summary,
    on="merchant",
    how="left"
)



# Fill missing values
summary[
    [
        "total_products",
        "medium_risk_products",
        "high_risk_products"
    ]
] = summary[
    [
        "total_products",
        "medium_risk_products",
        "high_risk_products"
    ]
].fillna(0)


summary[
    [
        "total_products",
        "medium_risk_products",
        "high_risk_products"
    ]
] = summary[
    [
        "total_products",
        "medium_risk_products",
        "high_risk_products"
    ]
].astype(int)



# Remove duplicate columns
summary = summary.drop(
    columns=[
        "total_reviews_quality",
        "average_rating_quality"
    ],
    errors="ignore"
)



# Arrange columns
summary = summary[
    [
        "merchant",
        "total_reviews",
        "total_products",
        "average_rating",
        "positive_percent",
        "negative_percent",
        "average_review_length",
        "average_sentiment_confidence",
        "medium_risk_products",
        "high_risk_products"
    ]
]



# Sort
summary = summary.sort_values(
    "total_reviews",
    ascending=False
)



# Save
summary.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n========== COMPLETE ==========")

print("Saved:")

print(OUTPUT_FILE)

print("\nPreview:")

print(summary)