from pathlib import Path
import pandas as pd

from nltk.sentiment import SentimentIntensityAnalyzer
import nltk


# Download VADER lexicon (only needed once)
nltk.download("vader_lexicon")



# Load data
project_root = Path(__file__).resolve().parent.parent
data_dir = project_root / "data" / "raw"

reviews = pd.read_csv(
    data_dir / "reviews.csv"
)

reviews["review_description"] = reviews["review_description"].fillna("")



# Initialize VADER
sia = SentimentIntensityAnalyzer()



# Compute sentiment scores
reviews["vader_score"] = reviews["review_description"].apply(
    lambda x: sia.polarity_scores(x)["compound"]
)



# Convert to sentiment labels
def label_sentiment(score):
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    return "neutral"

reviews["vader_label"] = reviews["vader_score"].apply(label_sentiment)



# Compare with star ratings
print("\n--- VADER vs STAR RATING ---")

rating_sentiment = reviews.groupby("rating")["vader_score"].describe()
print(rating_sentiment)



# Average sentiment by rating
avg_by_rating = reviews.groupby("rating")["vader_score"].mean()

print("\n--- AVERAGE VADER SCORE BY RATING ---")
print(avg_by_rating)



# Most positive / negative reviews
most_positive = reviews.loc[reviews["vader_score"].idxmax()]
most_negative = reviews.loc[reviews["vader_score"].idxmin()]

print("\n--- MOST POSITIVE REVIEW ---")
print(most_positive["vader_score"])
print(most_positive["review_description"])

print("\n--- MOST NEGATIVE REVIEW ---")
print(most_negative["vader_score"])
print(most_negative["review_description"])



# Correlation with rating
corr = reviews["rating"].corr(reviews["vader_score"])

print("\n--- CORRELATION (rating vs VADER) ---")
print(corr)



# Existing sentiment vs VADER comparison
print("\n--- EXISTING SENTIMENT vs VADER ---")

comparison = reviews[["sentiment", "vader_score"]].dropna()

print("\nCorrelation (existing sentiment vs VADER):")
print(comparison.corr())

print("\nSummary stats (existing sentiment):")
print(comparison["sentiment"].describe())

print("\nSummary stats (VADER sentiment):")
print(comparison["vader_score"].describe())



# Find biggest disagreements
reviews["sentiment_diff"] = reviews["sentiment"] - reviews["vader_score"]

print("\n--- TOP DISAGREEMENTS ---")

top_diff = reviews.reindex(
    reviews["sentiment_diff"].abs().sort_values(ascending=False).head(5).index
)[
    ["sentiment", "vader_score", "rating", "review_description"]
]

print(top_diff)



# Check direction agreement (positive/negative alignment)
reviews["sentiment_direction"] = reviews["sentiment"].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
reviews["vader_direction"] = reviews["vader_score"].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

agreement = (reviews["sentiment_direction"] == reviews["vader_direction"]).mean()

print("\n--- DIRECTIONAL AGREEMENT ---")
print(agreement)