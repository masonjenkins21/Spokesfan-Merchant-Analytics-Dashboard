from src.data import load_data, get_merchant_files
from src.preprocess import apply_preprocessing
from src.models import (
    load_model,
    load_transformer_model,
    transformer_score
)
from sklearn.metrics import classification_report

from nltk.sentiment import SentimentIntensityAnalyzer
from pathlib import Path
import joblib
import pandas as pd



# Load data
project_root = Path(__file__).resolve().parent.parent

merchant_files = get_merchant_files()

all_reviews = []

for merchant in merchant_files:

    print(f"\nProcessing {merchant['merchant']}")

    _, reviews = load_data(
        merchant["products"],
        merchant["reviews"]
    )

    reviews["merchant"] = merchant["merchant"]

    all_reviews.append(reviews)


reviews = pd.concat(
    all_reviews,
    ignore_index=True
)

reviews = apply_preprocessing(reviews)



# Load trained TF-IDF + Logistic Regression
tfidf = joblib.load(
    project_root / "models" / "tfidf_vectorizer.pkl"
)

model = load_model(
    project_root / "models" / "logreg_model.pkl"
)

X = tfidf.transform(
    reviews["clean_text"]
)

reviews["ml_pred_class"] = model.predict(X)


# Convert numeric prediction to sentiment label
reviews["ml_sentiment"] = reviews["ml_pred_class"].apply(
    lambda r:
        "positive"
        if r >= 4
        else "negative"
        if r <= 2
        else "neutral"
)



# VADER
sia = SentimentIntensityAnalyzer()

reviews["vader_score"] = reviews["clean_text"].apply(
    lambda x: sia.polarity_scores(x)["compound"]
)




# DistilBERT
transformer = load_transformer_model(
    "distilbert-base-uncased-finetuned-sst-2-english"
)

sample = reviews.sample(
    500,
    random_state=42
).copy()

sample["bert_score"] = sample["clean_text"].apply(
    lambda x: transformer_score(
        transformer,
        x
    )
)



# Final sentiment
sample["final_sentiment"] = sample["bert_score"].apply(
    lambda x:
        "positive"
        if x >= 0.3
        else "negative"
        if x <= -0.3
        else "neutral"
)

final_df = sample.copy()



# Convert star ratings to sentiment
reviews["rating_sentiment"] = reviews["rating"].apply(
    lambda r:
        "positive"
        if r >= 4
        else "negative"
        if r <= 2
        else "neutral"
)



# Agreement
agreement = (
    reviews["rating_sentiment"]
    ==
    reviews["ml_sentiment"]
).mean()

print("\n--- MODEL AGREEMENT RATE ---")

print(
    f"TF-IDF vs Rating Sentiment Agreement: {agreement:.2%}"
)



# Error analysis
errors = reviews[
    reviews["rating_sentiment"]
    !=
    reviews["ml_sentiment"]
]

print("\n--- ERROR SAMPLE ---")

print(
    errors[
        [
            "review_description",
            "clean_text",
            "rating",
            "rating_sentiment",
            "ml_sentiment"
        ]
    ].head(10)
)



# Outputs
print("\n--- FINAL DATAFRAME PREVIEW ---")

print(
    final_df.head()
)

print("\n--- DATAFRAME INFO ---")

print(
    final_df.info()
)

print("\n--- FINAL SENTIMENT DISTRIBUTION ---")

print(
    final_df["final_sentiment"].value_counts()
)

print("\n--- SAMPLE COMPARISON ---")

print(
    final_df[
        [
            "rating",
            "ml_pred_class",
            "bert_score",
            "vader_score",
            "final_sentiment"
        ]
    ].head(10)
)


print("\n--- CLASSIFICATION REPORT ---")

print(
    classification_report(
        reviews["rating_sentiment"],
        reviews["ml_sentiment"]
    )
)



# Optional export

# final_df.to_csv(
#     "data/processed/sentiment_output.csv",
#     index=False
# )