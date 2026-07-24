# Power BI model cleanup notes

## Completed automatically

The cleaned PBIX removes the duplicate hidden merchant slicer from the Product Performance page. The visible merchant slicer and its synchronization group remain intact.

## Semantic-model items intentionally preserved

The PBIX still contains the original semantic model. Automated deletion was not performed for these candidate tables because a table can support relationships, calculated tables, or DAX even when no current visual directly references it:

- Product Catalog
- Product Themes
- Merchant Sentiment
- Review Quality
- Product Family Lookup
- Dim Product Family Lookup
- Unmatched Product Keys
- Unmatched Product Details

The report also contains both `Dim Product Old` and `Dim Product`. Visual metadata contains mixed historical references, so replacing one with the other directly inside the PBIX package would risk broken relationships or fields.

## Recommended Power BI Desktop verification

1. Open the cleaned PBIX and confirm all three pages render.
2. Refresh the report and confirm all data sources resolve to the cleaned project's `data/processed/dashboard_metrics` folder.
3. Use Model view and Power Query query dependencies to verify whether the two `Unmatched` tables have downstream dependencies.
4. Migrate visuals and relationships from `Dim Product Old` to `Dim Product` one at a time.
5. Delete the old dimension only after no visuals, measures, relationships, or calculated tables reference it.
6. Disable load for staging queries that are needed for transformations but should not appear as semantic-model tables.
7. Hide technical keys and intermediate fields from Report view.
8. Save the file in Power BI Desktop after verification. This recreates Power BI's internal security metadata.
