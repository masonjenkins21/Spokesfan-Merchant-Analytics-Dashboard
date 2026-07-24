# Spokesfan Merchant Analytics Dashboard

This project builds the CSV datasets used by a merchant-facing Power BI dashboard for product reviews, sentiment, customer concerns, and product risk.

The production workflow uses a RoBERTa sentiment model and a series of deterministic pandas transformations. Earlier TF-IDF, logistic-regression, VADER, and DistilBERT experiments are retained under `archive/` so they do not obscure the final dashboard pipeline.

## Project structure

```text
SpokesfanDashboard_Cleaned/
├── dashboard/                  # Cleaned Power BI report copy
├── data/
│   ├── raw/                    # Merchant product and review exports
│   └── processed/
│       ├── reviews_with_roberta_sentiment.csv
│       └── dashboard_metrics/  # Power BI input tables
├── scripts/                    # Active production scripts
├── src/                        # Shared review classification logic
├── tests/                      # Lightweight structure/output tests
├── archive/                    # Experiments, debug scripts, and old exports
├── documentation/
├── requirements.txt
└── requirements-experiments.txt
```

## Run the dashboard pipeline

Create and activate a virtual environment, then install the production dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Build all dashboard tables from the included scored-review file:

```bash
python scripts/run_dashboard_pipeline.py
```

To rerun RoBERTa sentiment scoring from the raw review files first:

```bash
python scripts/run_dashboard_pipeline.py --score-reviews
```

The scoring step loads `cardiffnlp/twitter-roberta-base-sentiment-latest` and therefore takes longer than the downstream CSV build.

## Production script order

The runner executes these scripts in dependency order:

1. `build_core_metrics.py`
2. `build_theme_metrics.py`
3. `build_product_risk_analysis.py`
4. `build_review_quality.py`
5. `build_merchant_summary.py`
6. `build_product_catalog.py`
7. `build_sentiment_distribution.py`
8. `enrich_theme_metrics.py`
9. `build_customer_voice.py`
10. `build_product_risk_summary.py`

`score_reviews_roberta.py` is optional when `reviews_with_roberta_sentiment.csv` already exists.

## Validate the cleaned project

Install the development requirements and run the tests:

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

The cleaned pipeline was run successfully against the included data. Its generated dashboard tables were compared with the original project and found to be data-identical.

## Archive policy

The `archive/` folder contains material worth retaining for learning or historical context but not required by the final dashboard:

- early sentiment-analysis experiments
- TF-IDF and logistic-regression model artifacts
- inspection/debug scripts
- relationship troubleshooting scripts
- optional analysis not used by the current report
- manual Power BI exports

Do not import archived modules into the production pipeline without first updating their paths and dependencies.

## Power BI report

The cleaned report copy is located at:

```text
dashboard/Spokesfan_Merchant_Analytics_Dashboard_Cleaned.pbix
