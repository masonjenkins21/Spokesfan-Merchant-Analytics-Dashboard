"""
Script 21 - Create Dashboard Metrics

Purpose:
    Validate and enrich product_negative_themes.csv with consistent impact
    and risk metrics.

Updates:
    - product_negative_themes.csv
"""

from pathlib import Path

import pandas as pd


project_root = Path(__file__).resolve().parent.parent
dashboard_path = (
    project_root / "data" / "processed" / "dashboard_metrics"
)

product_theme_file = dashboard_path / "product_negative_themes.csv"


print("\nCreating dashboard metrics...\n")
print("Loading product negative themes...")

df = pd.read_csv(product_theme_file)

required_columns = [
    "merchant",
    "product_name",
    "theme",
    "mentions",
    "negative_review_count",
    "total_reviews",
    "average_rating",
    "theme_severity",
]

missing = [column for column in required_columns if column not in df.columns]
if missing:
    raise ValueError(
        "Run Script 20 first. Missing required columns: "
        f"{missing}"
    )


df["negative_review_rate"] = (
    df["negative_review_count"]
    / df["total_reviews"].replace(0, 1)
)

df["theme_prevalence_in_negative_reviews"] = (
    df["mentions"]
    / df["negative_review_count"].replace(0, 1)
)

df["overall_customer_impact"] = (
    df["mentions"]
    / df["total_reviews"].replace(0, 1)
)

df["weighted_theme_mentions"] = (
    df["mentions"] * df["theme_severity"]
)

# Interpretable theme-level risk:
# percent of all reviews represented by the theme, weighted by severity.
df["customer_risk_score"] = (
    df["overall_customer_impact"]
    * df["theme_severity"]
    * 100
).round(2)

df["impact_rank"] = (
    df.groupby("merchant")["customer_risk_score"]
    .rank(ascending=False, method="dense")
    .astype(int)
)

rate_columns = [
    "negative_review_rate",
    "theme_prevalence_in_negative_reviews",
    "overall_customer_impact",
]

df[rate_columns] = df[rate_columns].round(4)
df["average_rating"] = df["average_rating"].round(2)
df["weighted_theme_mentions"] = df["weighted_theme_mentions"].round(2)

df = df.sort_values(
    ["merchant", "impact_rank", "product_name", "theme"],
    ascending=[True, True, True, True],
)

df.to_csv(product_theme_file, index=False)


print("\n========== COMPLETE ==========")
print(f"Saved:\n{product_theme_file}")
print("\nPreview:")
print(df.head(20).to_string(index=False))
