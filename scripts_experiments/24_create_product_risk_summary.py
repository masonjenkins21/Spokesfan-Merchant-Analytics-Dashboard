"""
Script 24 - Create Product Risk Summary

Purpose:
    Create a BI-ready product risk dataset using validated negative review
    rates, issue severity, customer rating, and review-volume reliability.

Creates:
    - product_risk_summary.csv

Metrics:
    - total_reviews
    - total_negative_reviews
    - negative_review_rate
    - average_rating
    - primary_customer_concern
    - primary_concern_mentions
    - severity_weighted_issue_rate
    - product_risk_score
    - priority_rank
    - risk_level
    - review_volume_level
"""

from pathlib import Path
import math

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

theme_file = (
    dashboard_path
    / "product_negative_themes.csv"
)

output_file = (
    dashboard_path
    / "product_risk_summary.csv"
)


print("\nCreating product risk summary...\n")


# ---------------------------------------------------------
# Load product theme metrics
# ---------------------------------------------------------

print("Loading product negative themes...")

df = pd.read_csv(theme_file)

print(f"Loaded {len(df)} product-theme records")


# ---------------------------------------------------------
# Validate required columns
# ---------------------------------------------------------

required_columns = [
    "merchant",
    "product_name",
    "theme",
    "mentions",
    "negative_review_count",
    "negative_review_rate",
    "total_reviews",
    "average_rating",
    "theme_severity",
    "weighted_theme_mentions",
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
# Calculate product-level metrics
# ---------------------------------------------------------

print("\nCalculating product-level metrics...")

product_summary = (
    df
    .groupby(
        [
            "merchant",
            "product_name",
        ]
    )
    .agg(
        total_reviews=(
            "total_reviews",
            "max",
        ),
        total_negative_reviews=(
            "negative_review_count",
            "max",
        ),
        negative_review_rate=(
            "negative_review_rate",
            "max",
        ),
        average_rating=(
            "average_rating",
            "max",
        ),
        total_theme_mentions=(
            "mentions",
            "sum",
        ),
        weighted_theme_mentions=(
            "weighted_theme_mentions",
            "sum",
        ),
        distinct_concern_types=(
            "theme",
            "nunique",
        ),
    )
    .reset_index()
)


# ---------------------------------------------------------
# Find primary customer concern
# ---------------------------------------------------------

print("Finding primary customer concerns...")


# A primary concern should reflect both frequency and severity.
df["primary_concern_score"] = (
    df["mentions"]
    *
    df["theme_severity"]
)


# Prefer actionable themes over Other Feedback whenever a product
# has at least one specific concern category.
actionable_concerns = (
    df[
        df["theme"].ne("Other Feedback")
    ]
    .copy()
)


actionable_primary = (
    actionable_concerns
    .sort_values(
        [
            "merchant",
            "product_name",
            "primary_concern_score",
            "mentions",
            "theme_severity",
            "theme",
        ],
        ascending=[
            True,
            True,
            False,
            False,
            False,
            True,
        ],
    )
    .drop_duplicates(
        subset=[
            "merchant",
            "product_name",
        ],
        keep="first",
    )
)


fallback_primary = (
    df
    .sort_values(
        [
            "merchant",
            "product_name",
            "primary_concern_score",
            "mentions",
            "theme_severity",
            "theme",
        ],
        ascending=[
            True,
            True,
            False,
            False,
            False,
            True,
        ],
    )
    .drop_duplicates(
        subset=[
            "merchant",
            "product_name",
        ],
        keep="first",
    )
)


primary_concern = (
    fallback_primary
    [
        [
            "merchant",
            "product_name",
            "theme",
            "mentions",
            "theme_severity",
            "primary_concern_score",
        ]
    ]
    .rename(
        columns={
            "theme": "primary_customer_concern",
            "mentions": "primary_concern_mentions",
            "theme_severity": "primary_concern_severity",
        }
    )
)


actionable_primary = (
    actionable_primary
    [
        [
            "merchant",
            "product_name",
            "theme",
            "mentions",
            "theme_severity",
            "primary_concern_score",
        ]
    ]
    .rename(
        columns={
            "theme": "actionable_customer_concern",
            "mentions": "actionable_concern_mentions",
            "theme_severity": "actionable_concern_severity",
            "primary_concern_score": "actionable_concern_score",
        }
    )
)


primary_concern = (
    primary_concern
    .merge(
        actionable_primary,
        on=[
            "merchant",
            "product_name",
        ],
        how="left",
    )
)


has_actionable_concern = (
    primary_concern[
        "actionable_customer_concern"
    ]
    .notna()
)


primary_concern.loc[
    has_actionable_concern,
    "primary_customer_concern",
] = (
    primary_concern.loc[
        has_actionable_concern,
        "actionable_customer_concern",
    ]
)


primary_concern.loc[
    has_actionable_concern,
    "primary_concern_mentions",
] = (
    primary_concern.loc[
        has_actionable_concern,
        "actionable_concern_mentions",
    ]
)


primary_concern.loc[
    has_actionable_concern,
    "primary_concern_severity",
] = (
    primary_concern.loc[
        has_actionable_concern,
        "actionable_concern_severity",
    ]
)


primary_concern.loc[
    has_actionable_concern,
    "primary_concern_score",
] = (
    primary_concern.loc[
        has_actionable_concern,
        "actionable_concern_score",
    ]
)


primary_concern = primary_concern[
    [
        "merchant",
        "product_name",
        "primary_customer_concern",
        "primary_concern_mentions",
        "primary_concern_severity",
        "primary_concern_score",
    ]
]


product_summary = (
    product_summary
    .merge(
        primary_concern,
        on=[
            "merchant",
            "product_name",
        ],
        how="left",
    )
)


# ---------------------------------------------------------
# Create theme-specific issue counts
# ---------------------------------------------------------

print("Creating issue count columns...")

theme_columns = {
    "Skin Reaction / Sensitivity": "skin_reaction_count",
    "Shipping and Handling": "shipping_issue_count",
    "Packaging Quality": "packaging_issue_count",
    "Product Performance": "product_performance_issue_count",
    "Price / Value": "price_value_issue_count",
    "Texture": "texture_issue_count",
    "Color / Shade": "color_shade_issue_count",
    "Hydration": "hydration_issue_count",
    "Scent": "scent_issue_count",
    "Other Feedback": "other_feedback_count",
}


theme_pivot = (
    df
    .pivot_table(
        index=[
            "merchant",
            "product_name",
        ],
        columns="theme",
        values="mentions",
        aggfunc="sum",
        fill_value=0,
    )
    .reset_index()
    .rename(
        columns=theme_columns
    )
)


for output_column in theme_columns.values():

    if output_column not in theme_pivot.columns:
        theme_pivot[output_column] = 0


product_summary = (
    product_summary
    .merge(
        theme_pivot[
            [
                "merchant",
                "product_name",
                *theme_columns.values(),
            ]
        ],
        on=[
            "merchant",
            "product_name",
        ],
        how="left",
    )
)


# ---------------------------------------------------------
# Calculate risk components
# ---------------------------------------------------------

print("Calculating risk components...")


product_summary["severity_weighted_issue_rate"] = (
    product_summary["weighted_theme_mentions"]
    /
    product_summary["total_reviews"].replace(0, 1)
)


product_summary["rating_penalty"] = (
    (
        5
        -
        product_summary["average_rating"]
    )
    /
    4
).clip(
    lower=0,
    upper=1,
)


# Low-volume products remain visible, but their score is moderated
# until enough reviews exist. The multiplier reaches 1.0 at 50 reviews.
product_summary["volume_confidence"] = (
    product_summary["total_reviews"]
    .apply(
        lambda count: min(
            1.0,
            math.log1p(
                max(count, 0)
            )
            /
            math.log1p(50),
        )
    )
)


base_risk_score = (
    product_summary["negative_review_rate"]
    *
    100
    *
    0.55
    +
    product_summary["severity_weighted_issue_rate"]
    *
    100
    *
    0.30
    +
    product_summary["rating_penalty"]
    *
    100
    *
    0.15
)


product_summary["product_risk_score"] = (
    base_risk_score
    *
    (
        0.75
        +
        0.25
        *
        product_summary["volume_confidence"]
    )
).round(2)


# ---------------------------------------------------------
# Assign risk and volume levels
# ---------------------------------------------------------

print("Assigning risk levels...")


def assign_risk_level(score: float) -> str:
    """
    Risk thresholds aligned with the observed product score distribution.

    High:
        Score of 8 or greater.

    Medium:
        Score from 3 to 7.99.

    Low:
        Score below 3.
    """

    if score >= 8:
        return "High"

    if score >= 3:
        return "Medium"

    return "Low"


def assign_volume_level(total_reviews: int) -> str:

    if total_reviews >= 50:
        return "High"

    if total_reviews >= 15:
        return "Medium"

    return "Low"


product_summary["risk_level"] = (
    product_summary["product_risk_score"]
    .apply(assign_risk_level)
)


product_summary["review_volume_level"] = (
    product_summary["total_reviews"]
    .apply(assign_volume_level)
)


# ---------------------------------------------------------
# Rank products within each merchant
# ---------------------------------------------------------

print("Creating merchant-level priority ranking...")


product_summary = (
    product_summary
    .sort_values(
        [
            "merchant",
            "product_risk_score",
            "total_reviews",
            "product_name",
        ],
        ascending=[
            True,
            False,
            False,
            True,
        ],
    )
)


product_summary["priority_rank"] = (
    product_summary
    .groupby("merchant")
    .cumcount()
    +
    1
)


# ---------------------------------------------------------
# Format output
# ---------------------------------------------------------

round_columns = [
    "negative_review_rate",
    "severity_weighted_issue_rate",
    "rating_penalty",
    "volume_confidence",
    "primary_concern_score",
]


product_summary[round_columns] = (
    product_summary[round_columns]
    .round(4)
)


product_summary["average_rating"] = (
    product_summary["average_rating"]
    .round(2)
)


product_summary = product_summary[
    [
        "priority_rank",
        "merchant",
        "product_name",
        "risk_level",
        "product_risk_score",
        "review_volume_level",
        "total_reviews",
        "total_negative_reviews",
        "negative_review_rate",
        "average_rating",
        "primary_customer_concern",
        "primary_concern_mentions",
        "primary_concern_severity",
        "primary_concern_score",
        "distinct_concern_types",
        "severity_weighted_issue_rate",
        "skin_reaction_count",
        "shipping_issue_count",
        "packaging_issue_count",
        "product_performance_issue_count",
        "price_value_issue_count",
        "texture_issue_count",
        "color_shade_issue_count",
        "hydration_issue_count",
        "scent_issue_count",
        "other_feedback_count",
    ]
]


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

print("\nSaving product risk summary...")


product_summary.to_csv(
    output_file,
    index=False,
)


print("\n========== COMPLETE ==========")

print(f"Saved:\n{output_file}")

print("\nPreview:")

print(
    product_summary
    .head(20)
    .to_string(index=False)
)