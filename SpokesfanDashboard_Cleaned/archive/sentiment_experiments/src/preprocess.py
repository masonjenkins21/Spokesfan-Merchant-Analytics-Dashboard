import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# Preprocess data
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


def preprocess_text(text):
    if pd.isna(text):
        return ""

    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)

    tokens = text.split()
    tokens = [w for w in tokens if w not in stop_words]
    tokens = [lemmatizer.lemmatize(w) for w in tokens]

    return " ".join(tokens)


def apply_preprocessing(df, col="review_description"):
    df = df.copy()
    df["clean_text"] = df[col].apply(preprocess_text)
    return df