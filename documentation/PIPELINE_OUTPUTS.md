# Pipeline outputs

The runner validates these report-facing or report-supporting CSV files:

| File | Purpose |
|---|---|
| `merchant_sentiment_summary.csv` | Merchant-level sentiment totals and percentages |
| `product_sentiment_summary.csv` | Product-level sentiment and rating summary |
| `rating_sentiment_analysis.csv` | Sentiment distribution by star rating |
| `monthly_sentiment_trends.csv` | Monthly merchant sentiment trends |
| `recent_product_performance.csv` | Recent 90-day product metrics |
| `product_negative_themes.csv` | Product concern themes and impact metrics |
| `negative_sentiment_themes.csv` | Merchant-level concern-theme totals |
| `product_risk_analysis.csv` | Product risk calculation and category |
| `review_quality_metrics.csv` | Merchant review-quality metrics |
| `merchant_dashboard_summary.csv` | Consolidated merchant KPI table |
| `product_catalog.csv` | Product catalog and merchant mapping |
| `merchant_sentiment_distribution.csv` | Long-form sentiment counts for visuals |
| `customer_voice_highlights.csv` | Curated positive and negative customer excerpts |
| `product_risk_summary.csv` | Product priority, primary concern, and family risk metrics |

`negative_sentiment_keywords.csv` is retained for compatibility with the existing project, although the current production runner does not regenerate it.
