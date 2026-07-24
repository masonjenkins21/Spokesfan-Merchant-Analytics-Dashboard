import pandas as pd
from pathlib import Path



# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "reviews_with_roberta_sentiment.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "dashboard_metrics"
    / "product_catalog.csv"
)



# Load Data
print("Loading sentiment dataset...")

df = pd.read_csv(
    INPUT_PATH,
    low_memory=False
)

print(f"Loaded {len(df)} reviews")



# Create Product Catalog
print("\nCreating product catalog...")


catalog = (
    df[
        [
            "merchant",
            "product_name",
            "product_url"
        ]
    ]
    .dropna(subset=["product_name"])
    .drop_duplicates()
)


review_counts = (
    df
    .groupby(
        [
            "merchant",
            "product_name"
        ]
    )
    .size()
    .reset_index(
        name="total_reviews"
    )
)


catalog = catalog.merge(
    review_counts,
    on=[
        "merchant",
        "product_name"
    ],
    how="left"
)


catalog = catalog.sort_values(
    [
        "merchant",
        "product_name"
    ]
)



# Save
catalog.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\n========== COMPLETE ==========")

print("Saved:")
print(OUTPUT_PATH)

print("\nPreview:")
print(
    catalog.head(10)
)