import pandas as pd
from pathlib import Path



# File location
METRICS_DIR = Path(
    "data/processed/dashboard_metrics"
)



# Files to inspect
files = [
    "merchant_sentiment_summary.csv",
    "product_sentiment_summary.csv",
    "rating_sentiment_analysis.csv",
    "monthly_sentiment_trends.csv",
    "negative_sentiment_keywords.csv",
    "product_negative_themes.csv"
]



# Inspect files
for file in files:

    print("\n")
    print("=" * 50)
    print(file)
    print("=" * 50)


    path = METRICS_DIR / file


    if path.exists():

        df = pd.read_csv(
            path,
            low_memory=False
        )


        print("\nColumns:")
        print(
            df.columns.tolist()
        )


        print("\nShape:")
        print(
            df.shape
        )


        print("\nPreview:")
        print(
            df.head()
        )


    else:

        print(
            "FILE NOT FOUND"
        )