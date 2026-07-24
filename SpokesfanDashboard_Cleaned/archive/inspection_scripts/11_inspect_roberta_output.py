import pandas as pd

# Inspect RoBERTa output
df = pd.read_csv(
    "data/processed/reviews_with_roberta_sentiment.csv",
    low_memory=False
)

print("\n========== COLUMNS ==========")
print(df.columns.tolist())


print("\n========== SAMPLE ROWS ==========")
print(df.head())


print("\n========== SENTIMENT COUNTS ==========")
print(df["roberta_label"].value_counts())


print("\n========== RANDOM SENTIMENT EXAMPLES ==========")

print(
    df[
        [
            "review_description",
            "roberta_label",
            "roberta_confidence"
        ]
    ]
    .sample(10)
)