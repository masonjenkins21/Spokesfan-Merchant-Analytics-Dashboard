"""
Script 22 - Create Customer Theme Summary

Purpose:
    Aggregate validated review-level themes into merchant-wide customer
    insight metrics for Power BI.

Creates:
    - customer_theme_summary.csv

Metrics:
    - total_theme_mentions
    - reviews_affected
    - products_affected
    - average_customer_impact
    - theme_risk_score
    - risk_level
    - theme_rank
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

project_root = Path(__file__).resolve().parent.parent

dashboard_path = (
    project_root
    / "data"
    / "processed"
    / "dashboard_metrics"
)

input_file = (
    dashboard_path
    / "product_negative_themes.csv"
)

output_file = (
    dashboard_path
    / "customer_theme_summary.csv"
)


print("\nCreating customer theme summary...\n")


# ---------------------------------------------------------
# Load product theme metrics
# ---------------------------------------------------------

print("Loading product negative themes...")

df = pd.read_csv(input_file)

print(f"Loaded {len(df)} theme records")

print("\nColumns:")
print(df.columns.tolist())


# ---------------------------------------------------------
# Validate required columns
# ---------------------------------------------------------

required_columns = [
    "theme",
    "mentions",
    "product_name",
    "total_reviews",
    "theme_severity",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "Run Scripts 14 and 21 first. "
        f"Missing required columns: {missing_columns}"
    )


# ---------------------------------------------------------
# Aggregate themes
# ---------------------------------------------------------

print("\nAggregating themes...")

theme_summary = (
    df
    .groupby(
        [
            "theme",
            "theme_severity",
        ]
    )
    .agg(
        total_theme_mentions=(
            "mentions",
            "sum",
        ),
        products_affected=(
            "product_name",
            "nunique",
        ),
        total_reviews_across_affected_products=(
            "total_reviews",
            "sum",
        ),
    )
    .reset_index()
)


# Each validated negative review receives one primary theme.
# Therefore, total theme mentions are actual reviews affected.
theme_summary["reviews_affected"] = (
    theme_summary["total_theme_mentions"]
)


# ---------------------------------------------------------
# Calculate customer impact
# ---------------------------------------------------------

theme_summary["average_customer_impact"] = (
    theme_summary["total_theme_mentions"]
    /
    theme_summary[
        "total_reviews_across_affected_products"
    ].replace(0, 1)
)


# Severity-adjusted percentage of customer reviews affected.
theme_summary["theme_risk_score"] = (
    theme_summary["average_customer_impact"]
    *
    theme_summary["theme_severity"]
    *
    100
).round(2)


# ---------------------------------------------------------
# Create risk levels
# ---------------------------------------------------------

print("Creating risk levels...")


def assign_risk(score: float) -> str:
    """
    Assign risk using thresholds aligned with the observed score scale.

    High:
        Theme has a severity-adjusted customer impact of at least 0.50.

    Medium:
        Theme has a severity-adjusted customer impact from 0.20 to 0.49.

    Low:
        Theme has a severity-adjusted customer impact below 0.20.
    """

    if score >= 0.50:
        return "High"

    if score >= 0.20:
        return "Medium"

    return "Low"


theme_summary["risk_level"] = (
    theme_summary["theme_risk_score"]
    .apply(assign_risk)
)


# ---------------------------------------------------------
# Rank themes
# ---------------------------------------------------------

theme_summary["theme_rank"] = (
    theme_summary["theme_risk_score"]
    .rank(
        ascending=False,
        method="dense",
    )
    .astype(int)
)


# ---------------------------------------------------------
# Format output
# ---------------------------------------------------------

theme_summary["average_customer_impact"] = (
    theme_summary["average_customer_impact"]
    .round(4)
)

theme_summary = theme_summary[
    [
        "theme_rank",
        "theme",
        "risk_level",
        "theme_risk_score",
        "theme_severity",
        "total_theme_mentions",
        "reviews_affected",
        "products_affected",
        "average_customer_impact",
        "total_reviews_across_affected_products",
    ]
]

theme_summary = (
    theme_summary
    .sort_values(
        [
            "theme_rank",
            "theme",
        ]
    )
    .reset_index(drop=True)
)


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

print("\nSaving customer theme summary...")

theme_summary.to_csv(
    output_file,
    index=False,
)


print("\n========== COMPLETE ==========")

print(f"Saved:\n{output_file}")

print("\nPreview:")

print(
    theme_summary
    .head(20)
    .to_string(index=False)
)