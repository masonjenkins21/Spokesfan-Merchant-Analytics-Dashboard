"""Run the complete Spokesfan dashboard-data build in dependency order."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SCORED_REVIEWS = (
    PROJECT_ROOT / "data" / "processed" / "reviews_with_roberta_sentiment.csv"
)

DOWNSTREAM_STEPS = [
    "build_core_metrics.py",
    "build_theme_metrics.py",
    "build_product_risk_analysis.py",
    "build_review_quality.py",
    "build_merchant_summary.py",
    "build_product_catalog.py",
    "build_sentiment_distribution.py",
    "enrich_theme_metrics.py",
    "build_customer_voice.py",
    "build_product_risk_summary.py",
]

EXPECTED_OUTPUTS = [
    "merchant_sentiment_summary.csv",
    "product_sentiment_summary.csv",
    "rating_sentiment_analysis.csv",
    "monthly_sentiment_trends.csv",
    "recent_product_performance.csv",
    "product_negative_themes.csv",
    "negative_sentiment_themes.csv",
    "product_risk_analysis.csv",
    "review_quality_metrics.csv",
    "merchant_dashboard_summary.csv",
    "product_catalog.csv",
    "merchant_sentiment_distribution.csv",
    "customer_voice_highlights.csv",
    "product_risk_summary.csv",
]


def run_script(filename: str) -> None:
    """Run one pipeline script and stop immediately if it fails."""
    script_path = SCRIPTS_DIR / filename
    if not script_path.is_file():
        raise FileNotFoundError(f"Pipeline script not found: {script_path}")

    print(f"\n{'=' * 72}\nRunning {filename}\n{'=' * 72}", flush=True)

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{PROJECT_ROOT}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath
        else str(PROJECT_ROOT)
    )

    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
    )


def validate_outputs() -> None:
    """Confirm that every report-facing output was generated."""
    output_dir = PROJECT_ROOT / "data" / "processed" / "dashboard_metrics"
    missing = [name for name in EXPECTED_OUTPUTS if not (output_dir / name).is_file()]
    if missing:
        raise RuntimeError(
            "Pipeline completed, but expected outputs are missing: "
            + ", ".join(missing)
        )

    print("\nPipeline validation passed. Generated files:")
    for name in EXPECTED_OUTPUTS:
        print(f"  - {output_dir / name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build all CSV tables used by the Spokesfan Power BI dashboard."
    )
    parser.add_argument(
        "--score-reviews",
        action="store_true",
        help=(
            "Run RoBERTa scoring first. This downloads/loads the transformer model "
            "and can take substantially longer than the downstream build."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.score_reviews:
        run_script("score_reviews_roberta.py")
    elif not SCORED_REVIEWS.is_file():
        raise FileNotFoundError(
            f"Scored review file is missing: {SCORED_REVIEWS}. "
            "Run again with --score-reviews."
        )

    for step in DOWNSTREAM_STEPS:
        run_script(step)

    validate_outputs()
    print("\nSpokesfan dashboard pipeline completed successfully.")


if __name__ == "__main__":
    main()
