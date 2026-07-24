from pathlib import Path
import pandas as pd

# Load Data
project_root = Path(__file__).resolve().parent.parent
data_dir = project_root / "data" / "raw"

reviews = pd.read_csv(
    data_dir / "reviews.csv"
)

# Fill missing text
reviews["review_description"] = reviews["review_description"].fillna("")



# VADER model (Script 4)
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()

reviews["vader_score"] = reviews["review_description"].apply(
    lambda x: sia.polarity_scores(x)["compound"]
)



# TF-IDF + Logistic Regression model (Script 5)
import joblib

tfidf_vectorizer = joblib.load(
    project_root / "models" / "tfidf_vectorizer.pkl"
)

logreg_model = joblib.load(
    project_root / "models" / "logreg_model.pkl"
)

tfidf_features = tfidf_vectorizer.transform(reviews["review_description"])

reviews["ml_pred_class"] = logreg_model.predict(tfidf_features)



# DistilBERT sentiment (Script 6 model)
from transformers import pipeline

bert_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

def get_bert_score(text):
    result = bert_pipeline(text[:512])[0]
    return result["score"] if result["label"] == "POSITIVE" else -result["score"]

# Sample for speed
reviews_sample = reviews.copy()
reviews_sample = reviews_sample.sample(500, random_state=42)

reviews_sample["bert_score"] = reviews_sample["review_description"].apply(get_bert_score)



# Final consolidated daatset
final_df = reviews_sample[[
    "review_description",
    "rating",
    "vader_score",
    "ml_pred_class",
    "bert_score"
]].copy()



# Create simple unified sentiment label
def final_sentiment(row):
    if row["bert_score"] > 0.3:
        return "positive"
    elif row["bert_score"] < -0.3:
        return "negative"
    else:
        return "neutral"

final_df["final_sentiment"] = final_df["bert_score"].apply(
    lambda x: "positive" if x >= 0.3 else "negative" if x <= -0.3 else "neutral"
)

# Output checks

print("\n--- FINAL DATAFRAME PREVIEW ---")
print(final_df.head())

print("\n--- DATAFRAME INFO ---")
print(final_df.info())

print("\n--- FINAL SENTIMENT DISTRIBUTION ---")
print(final_df["final_sentiment"].value_counts())

print("\n--- SAMPLE COMPARISON ---")
print(final_df[[
    "rating",
    "ml_pred_class",
    "bert_score",
    "vader_score",
    "final_sentiment"
]].head(10))



# Model Agreement
agreement = (final_df["rating"] == final_df["ml_pred_class"]).mean()

print("\n--- MODEL AGREEMENT RATE ---")
print(f"TF-IDF vs Actual Rating Agreement: {agreement:.2%}")



# Error Analysis
errors = final_df[final_df["rating"] != final_df["ml_pred_class"]]

print("\n--- ERROR SAMPLE ---")
print(errors[[
    "review_description",
    "rating",
    "ml_pred_class",
    "bert_score"
]].head(10))

# Export for dashboard

#output_path = project_root / "data" / "processed" / "sentiment_output.csv"
#final_df.to_csv(output_path, index=False)

#print("\n--- FINAL DATASET CREATED ---")
#print("Saved to:", output_path)
#print(final_df.head())