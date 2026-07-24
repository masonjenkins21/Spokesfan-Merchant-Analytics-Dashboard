from pathlib import Path
import pandas as pd


# The goal is to evaluate how well rule-based, classical ML,
# and transformer-based models align with customer ratings in product reviews.


# Project root (one level up from the src folder)
project_root = Path(__file__).resolve().parent.parent
data_dir = project_root / "data" / "raw"



# Load in data
products = pd.read_csv(data_dir / "products.csv")
reviews = pd.read_csv(data_dir / "reviews.csv")




# Explore products
print("\n--- PRODUCTS ---")
print(products.shape)
print(products.columns)
print(products.head())



# Explore reviews
print("\n--- REVIEWS ---")
print(reviews.shape)
print(reviews.columns)
print(reviews.head())



# Print missing values
print("\n--- MISSING VALUES (PRODUCTS) ---")
print(products.isnull().sum().sort_values(ascending=False).head(10))

print("\n--- MISSING VALUES (REVIEWS) ---")
print(reviews.isnull().sum().sort_values(ascending=False).head(10))



# Check data types
print("\n--- DATA TYPES (PRODUCTS) ---")
print(products.dtypes)

print("\n--- DATA TYPES (REVIEWS) ---")
print(reviews.dtypes)



# Explore ratings
rating_pct = (
    reviews["rating"]
    .value_counts(normalize=True)
    .sort_index() * 100
)

print(rating_pct)



# Explore exisiting sentiment column
print("\n--- EXISTING SENTIMENT VALUES ---")
print(reviews["sentiment"].value_counts(dropna=False))

# Get review lengths
reviews["review_length"] = (
    reviews["review_description"]
    .fillna("")
    .str.len()
)

print("\n--- REVIEW LENGTH ---")
print(reviews["review_length"].describe())



# Find number of ACTUAL unique products
print("\n--- UNIQUE PRODUCT URLS ---")
print(reviews["product_url"].nunique())



# Compare missing sentiment values to missing review descriptions and check for match
missing_sentiment = reviews[reviews["sentiment"].isna()]

print("\n--- REVIEWS WITH MISSING SENTIMENT ---")
print(
    missing_sentiment[
        [
            "rating",
            "review_description"
        ]
    ]
)



# Examine longest review
print("\n--- LONGEST REVIEW ---")
longest_review = reviews.loc[
    reviews["review_length"].idxmax()
]

print(longest_review["review_description"])



# Explore sentiment
print("\n--- SENTIMENT SUMMARY ---")
print(reviews["sentiment"].describe())

print("\n--- SENTIMENT HISTOGRAM ---")
print(reviews["sentiment"].value_counts(bins=10).sort_index())



# Print sentiment BY rating
print("\n--- SENTIMENT BY RATING ---")

print(
    reviews.groupby("rating")["sentiment"].describe()
)



# Examine most positive and negative reviews to compare with our own run of VADER later
print("\n--- MOST POSITIVE REVIEW ---")

most_positive = reviews.loc[reviews["sentiment"].idxmax()]
print(most_positive["sentiment"])
print(most_positive["review_description"])

print("\n--- MOST NEGATIVE REVIEW ---")

most_negative = reviews.loc[reviews["sentiment"].idxmin()]
print(most_negative["sentiment"])
print(most_negative["review_description"])