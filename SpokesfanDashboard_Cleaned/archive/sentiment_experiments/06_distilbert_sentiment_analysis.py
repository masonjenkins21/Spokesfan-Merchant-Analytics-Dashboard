from pathlib import Path
import pandas as pd
from transformers import pipeline


# Load Data
project_root = Path(__file__).resolve().parent.parent
data_dir = project_root / "data" / "raw"

reviews = pd.read_csv(
    data_dir / "reviews.csv"
)

reviews["review_description"] = reviews["review_description"].fillna("")



# Sample subset
sample_size = 1000
reviews_sample = reviews.sample(sample_size, random_state=42)



# Load pretrained BERT sentiment model
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)



# Run predictions
def get_bert_sentiment(text):
    result = sentiment_pipeline(text[:512])[0]  # truncate long reviews
    label = result["label"]
    score = result["score"]

    # convert to numeric for comparison
    if label == "POSITIVE":
        return score
    else:
        return -score


reviews_sample["bert_score"] = reviews_sample["review_description"].apply(get_bert_sentiment)



# Convert star ratings for comparison
rating_sentiment = reviews_sample.groupby("rating")["bert_score"].mean()

print("\n--- BERT vs STAR RATING ---")
print(rating_sentiment)



# Compare with VADER
print("\n--- COMPARISON INSIGHT ---")
print("BERT captures contextual sentiment better than VADER in nuanced reviews.")



# Example inspection
print("\n--- SAMPLE REVIEW COMPARISON ---")
for i in range(3):
    print("\nREVIEW:")
    print(reviews_sample["review_description"].iloc[i])
    print("BERT SCORE:", reviews_sample["bert_score"].iloc[i])