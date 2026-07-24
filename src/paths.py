"""Central project paths used by the dashboard pipeline."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DASHBOARD_METRICS_DIR = PROCESSED_DATA_DIR / "dashboard_metrics"
SCORED_REVIEWS_FILE = PROCESSED_DATA_DIR / "reviews_with_roberta_sentiment.csv"


def ensure_output_directories() -> None:
    """Create output directories required by the pipeline."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_METRICS_DIR.mkdir(parents=True, exist_ok=True)
