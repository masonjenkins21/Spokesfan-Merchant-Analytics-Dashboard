"""Lightweight checks for the cleaned project structure and dashboard outputs."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METRICS_DIR = PROJECT_ROOT / "data" / "processed" / "dashboard_metrics"

REQUIRED_OUTPUT_COLUMNS = {
    "merchant_dashboard_summary.csv": {
        "merchant",
        "total_reviews",
        "average_rating",
        "positive_percent",
        "negative_percent",
    },
    "product_risk_summary.csv": {
        "merchant",
        "product_name",
        "primary_customer_concern",
    },
    "customer_voice_highlights.csv": {
        "merchant",
        "product_name",
        "customer_feedback",
    },
}


def test_no_local_environment_folders() -> None:
    for name in (".venv", ".idea", "__pycache__"):
        assert not (PROJECT_ROOT / name).exists()


def test_required_dashboard_outputs() -> None:
    for filename, required_columns in REQUIRED_OUTPUT_COLUMNS.items():
        path = METRICS_DIR / filename
        assert path.is_file(), f"Missing dashboard output: {path}"
        columns = set(pd.read_csv(path, nrows=1).columns)
        assert required_columns <= columns
