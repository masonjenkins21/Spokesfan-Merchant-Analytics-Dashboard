import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]



# File paths
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "reviews_with_roberta_sentiment.csv"

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "dashboard_metrics"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_FILE = (
    OUTPUT_DIR /
    "product_risk_analysis.csv"
)



# Load data
print("Loading sentiment dataset...")


df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)


print(
    f"Loaded {len(df)} reviews"
)


# Use existing product name if available
if "product_name" not in df.columns:
    df["product_name"] = (
        df["product_url"]
        .str.extract(r"/products/([^/?]+)")
    )

    df["product_name"] = (
        df["product_name"]
        .str.replace("-", " ", regex=False)
        .str.title()
    )



# Product metrics
print("\nCalculating product metrics...")


product_metrics = (
    df
    .groupby(
        [
            "merchant",
            "product_name"
        ]
    )
    .agg(

        total_reviews=(
            "review_text",
            "count"
        ),

        negative_reviews=(
            "roberta_label",
            lambda x:
                (x == "negative").sum()
        ),

        average_rating=(
            "rating",
            "mean"
        ),

        low_rating_reviews=(
            "rating",
            lambda x:
                (x <= 2).sum()
        ),

        average_confidence=(
            "roberta_confidence",
            "mean"
        )

    )

    .reset_index()
)




# Calculate percentages
product_metrics["negative_percent"] = (
    product_metrics["negative_reviews"]
    /
    product_metrics["total_reviews"]
    *
    100
)


product_metrics["low_rating_percent"] = (
    product_metrics["low_rating_reviews"]
    /
    product_metrics["total_reviews"]
    *
    100
)




# Normalize review volume
max_reviews = (
    product_metrics["total_reviews"]
    .max()
)


product_metrics["review_volume_score"] = (
    product_metrics["total_reviews"]
    /
    max_reviews
    *
    100
)

product_metrics["review_confidence"] = (
    product_metrics["total_reviews"]
    /
    50
)

product_metrics["review_confidence"] = (
    product_metrics["review_confidence"]
    .clip(upper=1)
)


# Risk score
product_metrics["risk_score"] = (

    product_metrics["negative_percent"] * 0.40

    +

    product_metrics["low_rating_percent"] * 0.30

    +

    product_metrics["review_volume_score"] * 0.20

    +

    (product_metrics["review_confidence"] * 100) * 0.10

)


# Risk category
def categorize_risk(row):

    if (
        row["negative_percent"] >= 15
        and row["total_reviews"] >= 25
    ):
        return "High"

    elif (
        row["negative_percent"] >= 5
        and row["total_reviews"] >= 25
    ):
        return "Medium"

    else:
        return "Low"



product_metrics["risk_category"] = (
    product_metrics.apply(
        categorize_risk,
        axis=1
    )
)




# Sort results
product_metrics = (
    product_metrics
    .sort_values(
        "risk_score",
        ascending=False
    )
)




# Save
product_metrics.to_csv(
    OUTPUT_FILE,
    index=False
)



print(
    "\n========== COMPLETE =========="
)


print(
    "Saved:"
)

print(
    OUTPUT_FILE
)


print(
    "\nTop risk products:"
)


print(
    product_metrics.head(10)
)