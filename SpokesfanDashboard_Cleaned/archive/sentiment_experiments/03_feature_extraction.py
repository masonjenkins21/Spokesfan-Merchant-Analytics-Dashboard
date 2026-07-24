from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import numpy as np


# Load data
project_root = Path(__file__).resolve().parent.parent
data_dir = project_root / "data" / "raw"

reviews = pd.read_csv(
    data_dir / "reviews.csv"
)

# Fill missing text just in case
reviews["review_description"] = reviews["review_description"].fillna("")



# Create cleaned text (same preprocessing as Script 2)
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return " ".join(tokens)

reviews["clean_text"] = reviews["review_description"].apply(preprocess_text)



# Bag of Words (Count Vectorizer)
count_vect = CountVectorizer(
    max_features=5000,
    stop_words="english",
    token_pattern=r"(?u)\b[a-zA-Z]+\b"
)

X_bow = count_vect.fit_transform(reviews["clean_text"])

print("\n--- BAG OF WORDS ---")
print("Shape:", X_bow.shape)



# TF-IDF (Weighted representation)
tfidf_vect = TfidfVectorizer(
    max_features=5000,
    stop_words="english",
    token_pattern=r"(?u)\b[a-zA-Z]+\b"
)

X_tfidf = tfidf_vect.fit_transform(reviews["clean_text"])

print("\n--- TF-IDF ---")
print("Shape:", X_tfidf.shape)



# Feature name mapping
feature_names = count_vect.get_feature_names_out()



# Sample review inspection
sample_index = 0

print("\n--- SAMPLE REVIEW ---")
print(reviews["clean_text"].iloc[sample_index])

# Get indices of non-zero features
bow_indices = X_bow[sample_index].nonzero()[1]
tfidf_indices = X_tfidf[sample_index].nonzero()[1]

print("\n--- BAG OF WORDS (word : count) ---")
for i in bow_indices[:10]:
    print(feature_names[i], ":", X_bow[sample_index, i])

print("\n--- TF-IDF (word : weight) ---")
for i in tfidf_indices[:10]:
    print(feature_names[i], ":", round(X_tfidf[sample_index, i], 4))



# Top TF-IDF words
print("\n--- TOP TF-IDF WORDS OVERALL ---")

tfidf_sums = np.asarray(X_tfidf.sum(axis=0)).flatten()
top_indices = tfidf_sums.argsort()[-20:][::-1]

for i in top_indices:
    print(feature_names[i], ":", round(tfidf_sums[i], 4))