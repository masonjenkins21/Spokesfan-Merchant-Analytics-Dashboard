from pathlib import Path
import re

import pandas as pd
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
nltk.download("wordnet")



# Load data
project_root = Path(__file__).resolve().parent.parent

data_dir = project_root / "data" / "raw"

reviews = pd.read_csv(
    data_dir / "reviews.csv"
)



#Useful column used in first script
reviews["review_length"] = (
    reviews["review_description"]
    .fillna("")
    .str.len()
)



# Create preprocessing objects
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()



# Build preprocessing function
def preprocess_text(text):

    # Handle missing values
    if pd.isna(text):
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove punctuation (keep letters, numbers, and spaces)
    text = re.sub(r"[^\w\s]", " ", text)

    # Tokenize
    tokens = word_tokenize(text)

    # Remove stop words
    tokens = [
        word
        for word in tokens
        if word not in stop_words
    ]

    # Lemmatize
    tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
    ]

    # Join back into one string
    return " ".join(tokens)



# Test reviews of different ratings/length
five_star = reviews[reviews["rating"] == 5].iloc[0]["review_description"]

print("\n--- 5-STAR REVIEW ---")
print("ORIGINAL")
print(five_star)


print("\nCLEANED:")
print(preprocess_text(five_star))


one_star = reviews[reviews["rating"] == 1].iloc[0]["review_description"]

print("\n--- 1-STAR REVIEW ---")
print("ORIGINAL")
print(one_star)

print("\nCLEANED:")
print(preprocess_text(one_star))


long_review = reviews.loc[
    reviews["review_length"].idxmax(),
    "review_description"
]

print("\n--- LONGEST REVIEW ---")
print("ORIGINAL")
print(long_review)

print("\nCLEANED:")
print(preprocess_text(long_review))