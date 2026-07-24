# Cleanup changelog

## Removed from the production path

- `.venv/`
- `.idea/`
- `.git/` from the shared ZIP copy
- Python cache folders
- duplicate model files stored beside scripts
- early experimental scripts from the active scripts folder
- inspection and relationship-debugging scripts from the active scripts folder
- four manual `Customer Feedback Requiring Action*.csv` exports
- `transformer_comparison_results.csv` from active processed data
- optional `customer_theme_summary.csv` from active dashboard data

Nothing was deleted from the user's original uploaded files. Historical material was moved into `archive/` in the cleaned copy.

## Production changes

- Renamed active scripts by purpose rather than development sequence number.
- Normalized scripts that depended on the current working directory so they use the project root.
- Moved shared customer-review rules into `src/review_logic.py`.
- Added `scripts/run_dashboard_pipeline.py` to run all build steps in dependency order.
- Added output validation to the pipeline runner.
- Split production, experiment, and development dependencies.
- Replaced the old README with documentation for the final RoBERTa dashboard workflow.
- Added lightweight tests for structure and critical output columns.

## Validation results

- Downstream pipeline completed successfully.
- All 15 retained dashboard CSVs were compared with the originals.
- Every retained CSV was data-identical; some differed only in CSV serialization formatting.
- Test suite result: `2 passed`.

## Power BI change

- Removed one duplicate hidden `Dim Merchant[Merchant Display]` slicer from the Product Performance page.
- Preserved the original DataModel byte-for-byte.
- Removed stale `SecurityBindings` from the modified PBIX package, as required after changing report layout contents.
- Validated the resulting PBIX ZIP package and report-layout JSON.
- Power BI Desktop is not available in this environment, so the modified PBIX should be opened once in Desktop and saved normally before replacing the user's working copy.
