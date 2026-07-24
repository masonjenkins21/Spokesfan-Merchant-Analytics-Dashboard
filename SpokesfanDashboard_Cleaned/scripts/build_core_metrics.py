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



# Load data
print("Loading sentiment dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Loaded {len(df)} reviews")



# Convert review dates and create month field
# Convert review dates and create month field
df["review_date"] = pd.to_datetime(
    df["review_date"],
    format="mixed",
    errors="coerce",
    utc=True
)

df["month"] = (
    df["review_date"]
    .dt.to_period("M")
    .astype(str)
)



# 1. Merchant Summary
print("\nCreating merchant summary...")


merchant_summary = (
    df.groupby("merchant")
    .agg(
        total_reviews=("review_description", "count"),
        positive_reviews=(
            "roberta_label",
            lambda x: (x == "positive").sum()
        ),
        neutral_reviews=(
            "roberta_label",
            lambda x: (x == "neutral").sum()
        ),
        negative_reviews=(
            "roberta_label",
            lambda x: (x == "negative").sum()
        ),
        average_rating=("rating", "mean"),
        average_confidence=(
            "roberta_confidence",
            "mean"
        )
    )
    .reset_index()
)


merchant_summary["positive_percent"] = (
    merchant_summary["positive_reviews"]
    /
    merchant_summary["total_reviews"]
    *
    100
)

merchant_summary["negative_percent"] = (
    merchant_summary["negative_reviews"]
    /
    merchant_summary["total_reviews"]
    *
    100
)


merchant_summary.to_csv(
    OUTPUT_DIR / "merchant_sentiment_summary.csv",
    index=False
)



# 2. Product Sentiment
print("Creating product summary...")


product_summary = (
    df.groupby(
        [
            "merchant",
            "product_name"
        ]
    )
    .agg(
        total_reviews=("review_description", "count"),
        average_rating=("rating", "mean"),
        average_confidence=(
            "roberta_confidence",
            "mean"
        ),
        positive_percent=(
            "roberta_label",
            lambda x:
            (x == "positive").mean() * 100
        ),
        negative_percent=(
            "roberta_label",
            lambda x:
            (x == "negative").mean() * 100
        )
    )
    .reset_index()
)


product_summary.to_csv(
    OUTPUT_DIR / "product_sentiment_summary.csv",
    index=False
)



# 3. Rating vs Sentiment
print("Creating rating sentiment analysis...")


rating_sentiment = (
    df.groupby("rating")
    .agg(
        total_reviews=("review_description", "count"),
        positive_percent=(
            "roberta_label",
            lambda x:
            (x == "positive").mean() * 100
        ),
        negative_percent=(
            "roberta_label",
            lambda x:
            (x == "negative").mean() * 100
        )
    )
    .reset_index()
)


rating_sentiment.to_csv(
    OUTPUT_DIR / "rating_sentiment_analysis.csv",
    index=False
)



# 4. Monthly Trends

print("Creating monthly trends...")

monthly_trends = (
    df.groupby(
        [
            "merchant",
            "month"
        ]
    )
    .agg(
        total_reviews=("review_description", "count"),
        positive_percent=(
            "roberta_label",
            lambda x:
            (x == "positive").mean() * 100
        ),
        negative_percent=(
            "roberta_label",
            lambda x:
            (x == "negative").mean() * 100
        )
    )
    .reset_index()
)


monthly_trends.to_csv(
    OUTPUT_DIR / "monthly_sentiment_trends.csv",
    index=False
)


print("\n========== COMPLETE ==========")


# 5. Recent Product Performance

print("Creating recent product performance...")


latest_date = df["review_date"].max()

recent_reviews = df[
    df["review_date"] >= latest_date - pd.Timedelta(days=90)
]


recent_product_performance = (
    recent_reviews
    .groupby(
        [
            "merchant",
            "product_name"
        ]
    )
    .agg(
        recent_reviews=("review_description", "count"),
        recent_positive_percent=(
            "roberta_label",
            lambda x: (x == "positive").mean() * 100
        ),
        recent_average_rating=(
            "rating",
            "mean"
        )
    )
    .reset_index()
)


recent_product_performance.to_csv(
    OUTPUT_DIR / "recent_product_performance.csv",
    index=False
)


print(
    "Dashboard files saved to:"
)

print(
    OUTPUT_DIR
)