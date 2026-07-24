import pandas as pd
from pathlib import Path



# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "dashboard_metrics"
    / "merchant_sentiment_summary.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "dashboard_metrics"
    / "merchant_sentiment_distribution.csv"
)



# Load Data
print("Loading merchant sentiment summary...")

df = pd.read_csv(INPUT_PATH)



# Convert Wide → Long Format
print("Creating sentiment distribution table...")

sentiment_rows = []


for _, row in df.iterrows():

    sentiment_rows.append({
        "merchant": row["merchant"],
        "sentiment": "Positive",
        "review_count": row["positive_reviews"]
    })

    sentiment_rows.append({
        "merchant": row["merchant"],
        "sentiment": "Neutral",
        "review_count": row["neutral_reviews"]
    })

    sentiment_rows.append({
        "merchant": row["merchant"],
        "sentiment": "Negative",
        "review_count": row["negative_reviews"]
    })


sentiment_distribution = pd.DataFrame(sentiment_rows)



# Save
sentiment_distribution.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\n========== COMPLETE ==========")

print("Saved:")
print(OUTPUT_PATH)

print("\nPreview:")

print(
    sentiment_distribution.to_string(
        index=False
    )
)