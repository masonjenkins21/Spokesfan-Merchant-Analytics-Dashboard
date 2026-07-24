"""
Script 20 - Create Negative Theme Metrics

Purpose:
    Build product- and merchant-level negative theme datasets from actual
    validated customer reviews.

Creates:
    - product_negative_themes.csv
    - negative_sentiment_themes.csv
"""

from pathlib import Path

import pandas as pd

from dashboard_review_logic import prepare_review_data


project_root = Path(__file__).resolve().parent.parent
processed_path = project_root / "data" / "processed"
dashboard_path = processed_path / "dashboard_metrics"

input_file = processed_path / "reviews_with_roberta_sentiment.csv"
product_output = dashboard_path / "product_negative_themes.csv"
merchant_output = dashboard_path / "negative_sentiment_themes.csv"


print("\nCreating negative theme metrics...\n")
print("Loading review data...")

df = pd.read_csv(input_file, low_memory=False)
reviews = prepare_review_data(df)

dashboard_path.mkdir(parents=True, exist_ok=True)

validated_negative = reviews[
    reviews["is_valid_negative"]
].copy()

print(f"Prepared reviews: {len(reviews)}")
print(f"Validated negative reviews: {len(validated_negative)}")


product_base = (
    reviews.groupby(["merchant", "product_name"])
    .agg(
        total_reviews=("review_text", "size"),
        average_rating=("rating", "mean"),
    )
    .reset_index()
)

negative_counts = (
    validated_negative.groupby(["merchant", "product_name"])
    .size()
    .reset_index(name="negative_review_count")
)

product_themes = (
    validated_negative.groupby(
        ["merchant", "product_name", "theme", "theme_severity"]
    )
    .size()
    .reset_index(name="mentions")
)

product_themes = (
    product_themes
    .merge(
        product_base,
        on=["merchant", "product_name"],
        how="left",
    )
    .merge(
        negative_counts,
        on=["merchant", "product_name"],
        how="left",
    )
)

product_themes["negative_review_count"] = (
    product_themes["negative_review_count"].fillna(0).astype(int)
)

product_themes["negative_review_rate"] = (
    product_themes["negative_review_count"]
    / product_themes["total_reviews"].replace(0, 1)
)

product_themes["theme_prevalence_in_negative_reviews"] = (
    product_themes["mentions"]
    / product_themes["negative_review_count"].replace(0, 1)
)

product_themes["overall_customer_impact"] = (
    product_themes["mentions"]
    / product_themes["total_reviews"].replace(0, 1)
)

product_themes["weighted_theme_mentions"] = (
    product_themes["mentions"]
    * product_themes["theme_severity"]
)

rate_columns = [
    "negative_review_rate",
    "theme_prevalence_in_negative_reviews",
    "overall_customer_impact",
]

product_themes[rate_columns] = product_themes[rate_columns].round(4)
product_themes["average_rating"] = product_themes["average_rating"].round(2)
product_themes["weighted_theme_mentions"] = (
    product_themes["weighted_theme_mentions"].round(2)
)

product_themes = product_themes.sort_values(
    [
        "merchant",
        "product_name",
        "mentions",
        "theme_severity",
    ],
    ascending=[True, True, False, False],
)

product_themes.to_csv(product_output, index=False)


merchant_base = (
    reviews.groupby("merchant")
    .agg(total_reviews=("review_text", "size"))
    .reset_index()
)

merchant_negative_counts = (
    validated_negative.groupby("merchant")
    .size()
    .reset_index(name="negative_review_count")
)

merchant_themes = (
    validated_negative.groupby(["merchant", "theme", "theme_severity"])
    .size()
    .reset_index(name="mentions")
)

merchant_themes = (
    merchant_themes
    .merge(merchant_base, on="merchant", how="left")
    .merge(merchant_negative_counts, on="merchant", how="left")
)

merchant_themes["negative_review_rate"] = (
    merchant_themes["negative_review_count"]
    / merchant_themes["total_reviews"].replace(0, 1)
)

merchant_themes["theme_prevalence_in_negative_reviews"] = (
    merchant_themes["mentions"]
    / merchant_themes["negative_review_count"].replace(0, 1)
)

merchant_themes["overall_customer_impact"] = (
    merchant_themes["mentions"]
    / merchant_themes["total_reviews"].replace(0, 1)
)

merchant_themes[rate_columns] = merchant_themes[rate_columns].round(4)

merchant_themes = merchant_themes.sort_values(
    ["merchant", "mentions", "theme_severity"],
    ascending=[True, False, False],
)

merchant_themes.to_csv(merchant_output, index=False)


print("\n========== COMPLETE ==========")
print(f"Saved:\n{product_output}")
print(f"Saved:\n{merchant_output}")

print("\nProduct theme preview:")
print(product_themes.head(20).to_string(index=False))
