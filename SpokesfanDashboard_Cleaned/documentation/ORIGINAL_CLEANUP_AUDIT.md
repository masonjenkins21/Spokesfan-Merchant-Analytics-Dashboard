# Spokesfan Dashboard Project Cleanup Audit

## Executive summary

The project is in better shape than it first appears. The main problem is not that the final workflow is broken; it is that experimental work, final production scripts, generated data, model artifacts, debug files, and IDE/environment files are all mixed together.

I tested the likely final dashboard build sequence using the uploaded processed review file. All 11 dashboard-generation scripts completed successfully, and every regenerated CSV was data-for-data identical to the uploaded version. This means the cleanup can be conservative: preserve the working final sequence, move experiments out of the way, remove duplicates and orphans, and then simplify the Power BI model.

## What was inspected

- Full PyCharm ZIP
- Python source and experiment scripts
- Raw and processed CSV inventory
- Saved TF-IDF and logistic-regression artifacts
- README, requirements, and `.gitignore`
- Power BI report pages, visual definitions, field references, and model table names

## Size and packaging findings

The uploaded ZIP is approximately 367 MB. Its uncompressed contents are approximately 1.2 GB.

Most of that is not project code:

| Item | Approximate uncompressed size | Recommendation |
|---|---:|---|
| `.venv/` | 1,138 MB | Keep locally if desired, but never include in a shared ZIP or Git repository |
| `data/` | 31.9 MB | Keep locally; choose intentionally what to share |
| `scripts_experiments/` | 0.5 MB | Split into final scripts and archive |
| `.git/` | 0.4 MB | Keep in the working repository, but normally omit from a manually shared ZIP |
| `.idea/` | very small | Keep locally or omit from shared project |

The actual project outside `.venv`, `.git`, and `.idea` is only about 33 MB, including the data.

## Verified final Python workflow

The following sequence ran successfully and regenerated the existing outputs exactly:

1. `10_sentiment_analysis_roberta.py` — creates the scored review dataset. This step was not rerun because the existing scored file was used as the pipeline input.
2. `12_create_dashboard_metrics.py`
3. `14_extract_sentiment_themes.py`
4. `15_create_product_risk_metrics.py`
5. `16_create_review_quality_metrics.py`
6. `17_create_dashboard_summary.py`
7. `18_create_product_catalog.py`
8. `20_create_sentiment_distribution.py`
9. `21_create_dashboard_metrics.py`
10. `22_create_customer_theme_summary.py`
11. `23_create_customer_voice_highlights.py`
12. `24_create_product_risk_summary.py`

Scripts 12 through 24 listed above were rerun. All completed without errors, and their regenerated DataFrames matched the uploaded CSVs exactly.

## Recommended script decisions

### Keep as the production dashboard workflow

Keep and rename these into a normal `scripts/` folder:

- `10_sentiment_analysis_roberta.py`
- `12_create_dashboard_metrics.py`
- `14_extract_sentiment_themes.py`
- `15_create_product_risk_metrics.py`
- `16_create_review_quality_metrics.py`
- `17_create_dashboard_summary.py`
- `18_create_product_catalog.py`
- `20_create_sentiment_distribution.py`
- `21_create_dashboard_metrics.py`
- `23_create_customer_voice_highlights.py`
- `24_create_product_risk_summary.py`
- `dashboard_review_logic.py`

`22_create_customer_theme_summary.py` works, but its output does not appear as a table used by the uploaded Power BI report. Keep it only if the customer-theme summary is a desired future feature; otherwise move it to the archive.

### Move to an archive folder

These are useful development history but are not part of the final RoBERTa dashboard build:

- `00_legacy_pipeline.py`
- `01_data_exploration.py`
- `02_text_preprocessing.py`
- `03_feature_extraction.py`
- `04_sentiment analysis.py`
- `05_tf-idf_logistic_regression_model.py`
- `06_distilbert_sentiment_analysis.py`
- `07_sentiment_analysis_consolidation.py`
- `08_test_multi_merchant_loading.py`
- `09_transformer_comparison.py`
- `11_inspect_roberta_output.py`
- `13_inspect_dashboard_metrics.py`
- `19_check_product_relationship.py`

Suggested archive categories:

```text
archive/
├── sentiment_experiments/
├── inspection_scripts/
└── relationship_debugging/
```

### Current `src/` finding

The present `src/` package supports the older sentiment-model experiments. It is not the module layer used by the final dashboard scripts. The final scripts mostly run as standalone files and import only `dashboard_review_logic.py`.

Recommended approach:

- Move `dashboard_review_logic.py` into `src/review_logic.py`.
- Gradually move reusable path, loading, validation, and metric functions into `src/`.
- Move the current experiment-only modules to `archive/sentiment_experiments/src/` if the TF-IDF/DistilBERT comparison is no longer part of the product.

### Broken or stale module

`src/sentiment.py` should not remain as-is. It uses `SentimentIntensityAnalyzer` without importing it and calls `bert_score`, which is not defined or imported in that file. It also reflects an older API than the current `load_transformer_model` / `transformer_score` code.

Either delete/archive it or rewrite it before presenting the repository as a clean final project.

## Model artifact cleanup

There are two copies of each model artifact:

```text
models/logreg_model.pkl
models/tfidf_vectorizer.pkl
scripts_experiments/logreg_model.pkl
scripts_experiments/tfidf_vectorizer.pkl
```

Findings:

- The two logistic-regression files are byte-for-byte identical.
- The two vectorizer files have different serialized hashes, but they contain the same vocabulary and identical IDF values.
- The final RoBERTa dashboard workflow does not use either the logistic-regression model or TF-IDF vectorizer.

Recommendation:

- If retaining the model comparison, keep one canonical pair in `models/experimental/`.
- Remove both copies from `scripts_experiments/`.
- If the final repository is strictly the production dashboard, archive the entire TF-IDF/logistic-regression artifact pair.

The duplicate files were likely created because `05_tf-idf_logistic_regression_model.py` saves to the current working directory:

```python
joblib.dump(tfidf, "tfidf_vectorizer.pkl")
joblib.dump(model, "logreg_model.pkl")
```

That should use an explicit project-root path if the script is retained.

## Generated data cleanup

### Keep as final or required intermediate outputs

- `reviews_with_roberta_sentiment.csv`
- `merchant_dashboard_summary.csv`
- `merchant_sentiment_distribution.csv`
- `merchant_sentiment_summary.csv`
- `monthly_sentiment_trends.csv`
- `product_catalog.csv`
- `product_negative_themes.csv`
- `product_risk_analysis.csv`
- `product_risk_summary.csv`
- `product_sentiment_summary.csv`
- `recent_product_performance.csv`
- `review_quality_metrics.csv`
- `customer_voice_highlights.csv`

Some of these are intermediate build outputs rather than report-facing tables. Keep them in the pipeline even if their Power BI load is disabled.

### Archive or remove after confirmation

These files have no producing script, no consuming script, and no direct visual reference in the uploaded report:

- `Customer Feedback Requiring Action.csv`
- `Customer Feedback Requiring ActionC.csv`
- `Customer Feedback Requiring ActionP.csv`
- `Customer Feedback Requiring ActionT.csv`

They appear to be manual exports or development snapshots.

Additional likely cleanup candidates:

- `negative_sentiment_keywords.csv` — no current producer and no direct visual reference
- `transformer_comparison_results.csv` — experimental model-comparison output
- `rating_sentiment_analysis.csv` — generated but not represented in the current report model/visuals
- `customer_theme_summary.csv` — generated but not represented in the current report model/visuals
- `negative_sentiment_themes.csv` — generated but not consumed by another Python script and not directly referenced by visuals

Do not delete the last three until checking whether they are intentionally retained for future pages or external analysis.

## Code-quality cleanup items

1. **Normalize paths.** Several scripts use paths relative to the current working directory, while others use `Path(__file__)`. Use one project-root helper everywhere.
2. **Add a runner.** Create one `run_dashboard_pipeline.py` that calls the build steps in order.
3. **Stop overwriting an intermediate file in place.** Script 21 reads and overwrites `product_negative_themes.csv`. Either merge its calculations into script 14 or write a clearly named enriched output.
4. **Fix numbering references.** Script 14 identifies itself as “Script 20,” and script 21 says to run Script 20 first even though its dependency is the theme-extraction step.
5. **Remove duplicated logic.** `23_create_customer_voice_highlights.py` contains logic overlapping `dashboard_review_logic.py`. Put shared sentiment correction, theme assignment, and validation in one module.
6. **Add input validation.** Each production script should verify required files and columns before performing work.
7. **Add a `main()` guard.** Wrap executable code in `main()` and use `if __name__ == "__main__": main()`.
8. **Update the README.** The current README is incomplete and still presents TF-IDF/DistilBERT as though they are the final production workflow. The dashboard data is built with RoBERTa.
9. **Split requirements.** The production dashboard needs a much smaller direct dependency set than the experiment environment.

Suggested split:

```text
requirements.txt                 # production dashboard
requirements-experiments.txt     # sklearn, nltk, joblib, comparison models
```

The production scripts directly rely mainly on `pandas`, `transformers`, and `torch`. Scikit-learn, NLTK, and joblib are used by the archived experiments.

## Power BI report findings

### Report inventory

- 3 pages:
  - Merchant Overview
  - Product Performance
  - Customer Insights
- 20 model tables
- 12 tables are referenced directly by report visuals

### Tables directly referenced by visuals

- `Merchant Summary`
- `Product Sentiment`
- `Monthly Trends`
- `Merchant Sentiment Distribution`
- `Product Performance Metrics`
- `Recent Product Performance`
- `Review Details`
- `Product Risk Summary`
- `Customer Voice Highlights`
- `Dim Merchant`
- `Dim Product Old`
- `Dim Product`

### Tables not directly referenced by visuals

These are cleanup candidates, not automatic deletions:

- `Product Catalog`
- `Product Themes`
- `Merchant Sentiment`
- `Review Quality`
- `Product Family Lookup`
- `Dim Product Family Lookup`
- `Unmatched Product Keys`
- `Unmatched Product Details`

A table can still be required by a relationship, calculated table, or DAX measure even when no visual directly references it. Verify dependencies before deleting.

### Strong Power BI cleanup candidates

1. **`Unmatched Product Keys` and `Unmatched Product Details`** look like debugging tables. They have no direct visual references. Remove them after confirming they do not feed calculated tables or measures.
2. **Two product dimensions are active in the report.** `Dim Product Old` is referenced by four visuals, while `Dim Product` is referenced by one. The top-products bar references both dimensions. This is the clearest model cleanup priority: migrate all visuals and relationships to one product dimension, then delete the old one.
3. **Duplicate merchant slicer on Product Performance.** The page contains two nearly overlapping slicers using `Dim Merchant[Merchant Display]` and the same sync group. Retain one after checking visual interactions.
4. **Helper/source tables should usually be hidden or have load disabled rather than duplicated in the visible report model.** This likely applies to some combination of Product Catalog, Product Themes, Merchant Sentiment, Review Quality, and the lookup tables.

## Safe Power BI cleanup sequence

1. Save a backup copy of the PBIX.
2. Remove the duplicate merchant slicer and test page interactions.
3. Open Power Query and review query dependencies.
4. In Model view, trace relationships from every candidate table.
5. Check whether measures or calculated tables reference the candidate table.
6. Consolidate `Dim Product Old` into `Dim Product` one visual at a time.
7. Refresh the report and verify all three pages after each model change.
8. Delete debug tables only after the model refreshes without errors.
9. Disable load for staging/helper queries that are required for transformations but do not need their own model table.
10. Hide technical keys and intermediate columns from report view.

## Proposed cleaned structure

```text
SpokesfanDashboard/
├── src/
│   ├── __init__.py
│   ├── paths.py
│   ├── data.py
│   ├── review_logic.py
│   └── validation.py
├── scripts/
│   ├── 01_score_reviews_roberta.py
│   ├── 02_build_core_metrics.py
│   ├── 03_build_theme_metrics.py
│   ├── 04_build_customer_highlights.py
│   ├── 05_build_product_risk_summary.py
│   └── run_dashboard_pipeline.py
├── archive/
│   ├── sentiment_experiments/
│   ├── inspection_scripts/
│   ├── relationship_debugging/
│   └── manual_exports/
├── data/
│   ├── raw/
│   └── processed/
│       └── dashboard_metrics/
├── models/
│   └── experimental/
├── documentation/
├── tests/
├── .gitignore
├── README.md
├── requirements.txt
└── requirements-experiments.txt
```

## Recommended immediate action

Do not delete the final scripts yet. First create the cleaned folder structure, move experiments to `archive/`, add the pipeline runner, and rerun the same verified sequence. Once the regenerated outputs still match and Power BI refreshes correctly, remove orphan CSVs and simplify the semantic model.
