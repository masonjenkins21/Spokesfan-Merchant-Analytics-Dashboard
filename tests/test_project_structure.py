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

LOCAL_ONLY_FOLDERS = {
    ".venv",
    ".idea",
    "__pycache__",
}


def test_local_environment_folders_are_gitignored() -> None:
    """Confirm local environment folders are excluded from Git."""

    gitignore_path = PROJECT_ROOT / ".gitignore"

    assert gitignore_path.is_file(), "The project is missing a .gitignore file."

    ignored_entries = {
        line.strip().rstrip("/")
        for line in gitignore_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }

    missing_entries = LOCAL_ONLY_FOLDERS - ignored_entries

    assert not missing_entries, (
        "These local folders are missing from .gitignore: "
        f"{sorted(missing_entries)}"
    )


def test_required_dashboard_outputs() -> None:
    """Confirm required Power BI output files and columns exist."""

    for filename, required_columns in REQUIRED_OUTPUT_COLUMNS.items():
        path = METRICS_DIR / filename

        assert path.is_file(), f"Missing dashboard output: {path}"

        columns = set(pd.read_csv(path, nrows=1).columns)
        missing_columns = required_columns - columns

        assert not missing_columns, (
            f"{filename} is missing required columns: "
            f"{sorted(missing_columns)}"
        )