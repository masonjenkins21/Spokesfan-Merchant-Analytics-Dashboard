# Spokesfan Merchant Analytics — Project Decisions and Rationale

## Purpose

This project was built to turn merchant product and review exports into a repeatable set of business-facing metrics and Power BI views. The report is intended to help a merchant quickly answer four questions:

1. How are products and merchants performing overall?
2. Where is negative customer sentiment concentrated?
3. Which products deserve attention first?
4. What are customers actually saying about those products?

The design therefore favors interpretable metrics, repeatable transformations, and report-ready tables over a single large all-purpose dataset.

---

## 1. Project architecture

### Decision: keep raw data, processed data, transformation scripts, and the Power BI report separate

The project is organized into four functional layers:

- `data/raw/` — original merchant product and review exports
- `data/processed/` — sentiment-scored reviews and generated dashboard tables
- `scripts/` and `src/` — repeatable transformation and classification logic
- `dashboard/` — the Power BI report and report previews

### Why

Keeping these layers separate makes it easier to understand where a value came from and prevents report-specific formatting from becoming mixed with source-data preparation. Raw exports can remain unchanged while the processed layer can be rebuilt as business rules evolve.

---

## 2. Use CSV outputs as the interface between Python and Power BI

### Decision

The Python pipeline produces a set of focused CSV tables under `data/processed/dashboard_metrics/`, and Power BI consumes those tables rather than reproducing all of the transformation logic in DAX or Power Query.

### Why

This approach was chosen because the project contains several text-heavy operations — sentiment scoring, review validation, issue classification, product-risk calculations, and customer-feedback selection — that are easier to express and test in Python. Precomputing those results also keeps the Power BI model simpler and makes report refresh behavior more predictable.

The output tables are intentionally specialized. For example, merchant KPIs, product sentiment, recent product performance, customer voice, and product risk each have their own table instead of being forced into one denormalized export.

A complete list of generated tables and their report purposes is maintained in `PIPELINE_OUTPUTS.md`.

---

## 3. Sentiment scoring

### Decision: use a pretrained RoBERTa sentiment model for review text

The optional scoring stage uses `cardiffnlp/twitter-roberta-base-sentiment-latest`. The review title and review description are combined into one text field before scoring.

### Why

Customer reviews are unstructured and often contain mixed language that cannot be summarized reliably from star rating alone. A pretrained language model provides a consistent positive / neutral / negative classification across all merchants without requiring a manually labeled training set for this project.

Combining the review title and body preserves more context than scoring either field separately. The model confidence is also retained so downstream steps can distinguish stronger classifications from weaker ones.

### Tradeoff

Model sentiment is not treated as infallible. Ratings and explicit review language are used later to validate edge cases, particularly for negative-review analysis.

---

## 4. Preserve star rating as a separate signal

### Decision

Sentiment and rating are retained as separate fields rather than converting one directly into the other.

### Why

A rating and the tone of a written review do not always agree. A customer can leave a high rating while mentioning a minor drawback, or a middling rating while describing a legitimate product problem. Keeping both signals allows the project to use sentiment for text interpretation while still using rating as evidence when validating complaints and calculating risk.

---

## 5. Validate negative reviews before using them for issue analysis

### Decision

Negative-theme analysis does not blindly use every review labeled negative. The shared review logic checks the written review and rating before a review is allowed into the concern datasets.

A review is treated as a supported negative concern when there is evidence such as:

- explicit complaint language,
- a rating of 1 or 2 stars, or
- a 3-star review that is also classified as negative.

High-rating reviews with clearly positive context are prevented from entering the concern tables.

### Why

Issue dashboards are more sensitive to false negatives than a general sentiment summary. A positive testimonial incorrectly placed into a "customer concern" table would be misleading to a merchant. The validation layer therefore favors business interpretability over using the model label alone.

---

## 6. Correct a small number of obvious sentiment edge cases

### Decision

Rule-based corrections are applied when review language and rating provide strong evidence that the original sentiment label is wrong. Examples include explicit complaints paired with low ratings and clearly positive language paired with high ratings.

### Why

The goal is not to replace the model with keyword matching. The rules are used only as guardrails for recognizable errors that materially affect merchant-facing metrics. This keeps the system mostly model-driven while preventing obvious contradictions from flowing into risk and concern calculations.

---

## 7. Remove duplicate review text from concern preparation

### Decision

Within the theme-analysis preparation step, reviews are normalized and duplicate review text for the same merchant/product is removed, keeping the record with the strongest sentiment confidence.

### Why

Duplicate review records can overstate the frequency of a problem. Deduplicating normalized review text prevents the same customer statement from being counted multiple times while retaining the strongest available classification.

For customer highlights, duplicate review text is also removed across products within a merchant before representative excerpts are selected. This prevents the same review from appearing repeatedly for bundles, kits, and related products.

---

## 8. Exclude non-product merchandise from product-issue analysis

### Decision

Gift cards, gift boxes, mugs, and T-shirts are excluded from the shared review preparation used for product concern and theme analysis.

### Why

The merchant dashboard is focused on product performance and customer experience for the core catalog. Non-product or promotional merchandise can introduce issue patterns that are not useful when prioritizing the performance of the primary product assortment.

This exclusion is intentionally scoped to the concern/theme preparation logic rather than rewriting the raw data.

---

## 9. Use actionable customer-concern categories

### Decision

Negative reviews are grouped into a compact theme taxonomy:

| Theme | Severity weight |
|---|---:|
| Skin Reaction / Sensitivity | 1.00 |
| Shipping and Handling | 0.80 |
| Product Performance | 0.75 |
| Packaging Quality | 0.65 |
| Price / Value | 0.55 |
| Texture | 0.50 |
| Hydration | 0.50 |
| Scent | 0.45 |
| Color / Shade | 0.40 |
| Other Feedback | 0.30 |

### Why

The categories were selected to be specific enough to support action while remaining broad enough to work across different merchants and product types. For example, "Skin Reaction / Sensitivity" is more useful to a merchant than a generic negative-sentiment count because it points to a specific type of customer experience.

Severity weights allow a frequent but relatively minor issue and a smaller number of potentially serious issues to be distinguished when risk is calculated.

`Other Feedback` is retained as a fallback so negative reviews are not discarded simply because they do not match a predefined category.

---

## 10. Measure themes in more than one way

### Decision

Theme outputs include:

- number of theme mentions,
- overall negative-review rate,
- theme prevalence among negative reviews,
- theme impact as a share of all product reviews, and
- severity-weighted theme mentions.

### Why

Raw counts alone favor products with large review volume. Percentages alone can overemphasize very small products. Providing both count and rate measures gives Power BI enough context to distinguish a widespread issue from a high-percentage issue based on only a few reviews.

---

## 11. Use a 90-day window for recent product performance

### Decision

Recent product performance is calculated over the 90 days preceding the latest review date in the dataset.

### Why

The dashboard needs both long-term context and a view of current conditions. Ninety days is long enough to provide a usable sample for many products while still responding to recent changes in sentiment, ratings, or review activity.

The window is anchored to the latest review in the data rather than the computer's current date. This keeps a static project extract internally consistent even when the report is opened later.

---

## 12. Use two complementary product-risk calculations

The project contains two risk outputs because they serve different report needs.

### A. Baseline product risk (`product_risk_analysis.csv`)

This table provides a straightforward product-level risk view and supplies risk-category counts used in merchant-level summary metrics.

The score combines:

- 40% negative-review percentage,
- 30% low-rating percentage (1–2 stars),
- 20% normalized review volume, and
- 10% review-volume confidence.

For the categorical flag, a product requires at least 25 reviews before it can be classified Medium or High:

- **High:** negative review rate at least 15% and at least 25 reviews
- **Medium:** negative review rate at least 5% and at least 25 reviews
- **Low:** otherwise

#### Why

The minimum review count prevents a handful of reviews from creating an outsized merchant-level risk count. Negative sentiment and low star ratings carry most of the weight, while review volume adds context about how well-supported the signal is.

### B. Action-oriented product risk (`product_risk_summary.csv`)

This table is designed for the "products requiring attention" style visuals. Its base score combines:

- 55% negative-review rate,
- 30% severity-weighted issue rate, and
- 15% rating penalty.

The score is then moderated by review-volume confidence. Low-volume products remain visible, but their score is reduced until the evidence base becomes stronger. Volume confidence gradually increases and reaches its maximum at 50 reviews.

Risk levels are:

- **High:** score >= 8
- **Medium:** score >= 3 and < 8
- **Low:** score < 3

Products are then ranked within each merchant by risk score, with review volume used as a secondary ordering signal.

#### Why

For product prioritization, the dashboard needs more than a negative percentage. The richer score incorporates issue severity, overall rating, and evidence strength so the report can emphasize products that are both problematic and well-supported by customer feedback.

---

## 13. Prefer a specific primary concern over generic feedback

### Decision

The product-risk summary selects the primary customer concern using both frequency and severity. A specific actionable theme is preferred over `Other Feedback` when a product has at least one more specific concern.

### Why

A dashboard card such as "Primary Customer Concern" should tell the merchant what kind of problem to investigate. Showing `Other Feedback` when a meaningful specific issue is available would reduce the usefulness of the visual.

---

## 14. Select representative customer feedback instead of exposing every review

### Decision

The customer-voice output selects representative positive and negative reviews rather than sending the full review corpus directly to report visuals.

Key rules include:

- minimum model confidence of 0.50,
- confidence labels of Medium at 0.60+ and High at 0.85+,
- up to three positive and three negative highlights per merchant/product,
- recent negative concerns limited to the latest 90-day window,
- issue priority used when ordering negative candidates, and
- customer-caused damage excluded from product concern highlights.

### Why

Displaying every review would make the report noisy and difficult to scan. A small set of ranked examples provides evidence behind the quantitative metrics without turning the dashboard into a review browser.

Negative examples are kept recent because they are most useful when they point to problems a merchant may need to address now.

---

## 15. Redact obvious personal information from dashboard excerpts

### Decision

Before customer feedback is written to the dashboard output, common personal-information patterns are redacted, including email addresses, phone numbers, postal codes, ZIP codes, and explicit street addresses.

### Why

The report needs the substance of customer feedback, not personally identifying details. Redaction reduces unnecessary exposure while preserving the business meaning of the review.

The patterns are intentionally conservative to avoid stripping ordinary review language.

---

## 16. Build summary tables specifically for Power BI visuals

### Decision

Several outputs reshape or consolidate data specifically for reporting. Examples include:

- `merchant_dashboard_summary.csv` for top-level merchant KPI cards,
- `merchant_sentiment_distribution.csv` in long format for sentiment charts,
- `product_catalog.csv` for product/merchant mapping,
- `recent_product_performance.csv` for 90-day product tables, and
- `product_risk_summary.csv` for ranked product-attention visuals.

### Why

Power BI visuals are easier to build and maintain when each table has a clear grain and purpose. For example, sentiment counts are converted from a wide merchant summary into a long table with one row per merchant/sentiment category because that structure works naturally with legends and category axes.

---

## 17. Use shared merchant and product dimensions in Power BI

### Decision

The semantic model includes shared merchant and product dimensions and uses a product key for product-level relationships.

### Why

The same merchant or product appears in several fact/summary tables. Shared dimensions provide a consistent source for slicers and reduce the risk of inconsistent filtering across visuals.

A product key is preferable to product name alone because product names are not guaranteed to be globally unique across merchants. The merchant dimension also provides clean display names such as `Cheekbone Beauty`, `Province Apothecary`, and `Three Ships Beauty` while retaining the source merchant key used by the pipeline.

---

## 18. Separate the report into three decision levels

### Decision

The Power BI report is organized into three main pages:

1. **Merchant Overview** — top-level health, merchant comparison, product highlights, sentiment distribution, and trends
2. **Product Performance** — product rankings, recent performance, negative-review concentration, and products to monitor
3. **Customer Insights** — concern themes, customer feedback, sentiment distribution, and trend context

### Why

The pages follow a drill-down pattern:

**What is happening? → Which products are driving it? → What are customers saying?**

This reduces visual overload and gives each page a clear purpose while allowing merchant and product filters to connect the analysis.

---

## 19. Use consistent visual meaning for color

### Decision

The dashboard uses a consistent visual language:

- green for positive sentiment / favorable performance,
- red for negative sentiment / warnings / products needing attention,
- blue for general informational or comparison elements, and
- muted neutral colors for secondary labels and context.

### Why

Consistent semantic color reduces the amount of explanation required on each page. Users can quickly distinguish favorable metrics from risk signals without relearning the meaning of colors from visual to visual.

---

## 20. Keep the pipeline modular but provide one runner

### Decision

Each transformation has its own script, while `run_dashboard_pipeline.py` executes the downstream steps in dependency order and verifies that the expected report-facing outputs exist.

### Why

Separate scripts make individual transformations easier to troubleshoot and revise. The runner provides a single reproducible entry point for rebuilding the complete dashboard dataset.

Sentiment scoring is optional because the scored review dataset is included. This avoids repeatedly running the most computationally expensive stage when only dashboard metrics need to be refreshed.

---

## 21. Current project scope and limitations

The current project should be interpreted with the following boundaries in mind:

- Sentiment labels are model-based and can still contain classification errors despite validation rules.
- Theme assignment is intentionally interpretable and rule-based; reviews with language outside the defined patterns can fall into `Other Feedback`.
- Risk scores are prioritization heuristics for dashboard use, not predictions of future product failure or customer behavior.
- The 90-day metrics are relative to the latest review date in the included dataset.
- Merchant datasets are not equal in review volume, so direct comparisons should consider both rates and underlying review counts.
- Dashboard results represent the supplied review/product exports and should not be interpreted as a complete measure of merchant financial performance.

These limitations are why the report presents review counts, rates, ratings, sentiment, concern themes, and customer examples together rather than relying on a single score.

---

## Rebuild workflow

The standard workflow is:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\run_dashboard_pipeline.py
```

To recreate sentiment scores from the raw review exports before rebuilding the dashboard tables:

```powershell
python scripts\run_dashboard_pipeline.py --score-reviews
```

The report project is located at:

```text
dashboard\MerchantDashboard\Spokesfan_Merchant_Analytics.pbip
```
