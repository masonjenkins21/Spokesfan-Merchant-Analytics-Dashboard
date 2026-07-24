import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]



# Paths
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "reviews_with_roberta_sentiment.csv"

OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "dashboard_metrics" / "review_quality_metrics.csv"



# Load data
print("Loading review dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)


print(
    f"Loaded {len(df)} reviews"
)



# Feature engineering
print("\nCreating review quality metrics...")


# Review length
df["review_length"] = (
    df["review_text"]
    .fillna("")
    .str.len()
)


# Verified reviewer conversion
df["verified_numeric"] = (
    df["verified"]
    .astype(str)
    .str.lower()
    .isin(
        [
            "true",
            "yes",
            "verified",
            "1"
        ]
    )
)


# Helpful count cleanup
df["helpful_count"] = pd.to_numeric(
    df["helpful_count"],
    errors="coerce"
)


df["helpful_count"] = (
    df["helpful_count"]
    .fillna(0)
)




# Merchant metrics
metrics = (
    df
    .groupby("merchant")
    .agg(

        total_reviews=(
            "review_text",
            "count"
        ),

        average_review_length=(
            "review_length",
            "mean"
        ),


        average_rating=(
            "rating",
            "mean"
        ),

        average_sentiment_confidence=(
            "roberta_confidence",
            "mean"
        )

    )
    .reset_index()
)





# Sort
metrics = (
    metrics
    .sort_values(
        "total_reviews",
        ascending=False
    )
)




# Save
metrics.to_csv(
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
    "\nPreview:"
)

print(
    metrics
)