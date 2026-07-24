from pathlib import Path
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score


# Load data
project_root = Path(__file__).resolve().parent.parent
data_dir = project_root / "data" / "raw"

reviews = pd.read_csv(
    data_dir / "reviews.csv"
)

reviews["review_description"] = reviews["review_description"].fillna("")



# Preprocess (reuse prev version)
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = text.split()
    tokens = [w for w in tokens if w not in stop_words]
    tokens = [lemmatizer.lemmatize(w) for w in tokens]
    return " ".join(tokens)

reviews["clean_text"] = reviews["review_description"].apply(preprocess_text)



# Features and labels
X = reviews["clean_text"]
y = reviews["rating"]



# TF-IDF Vectorization
tfidf = TfidfVectorizer(
    max_features=5000,
    stop_words="english"
)

X_tfidf = tfidf.fit_transform(X)



# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X_tfidf,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)



# Model training
model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

model.fit(X_train, y_train)



# Predictions
y_pred = model.predict(X_test)



# Evaluation
print("\n--- LOGISTIC REGRESSION RESULTS ---")
print("Accuracy:", accuracy_score(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))



# Top predictive words per class
feature_names = tfidf.get_feature_names_out()
coefficients = model.coef_

print("\n--- TOP WORDS PER SENTIMENT CLASS ---")

for i, class_label in enumerate(model.classes_):
    top_indices = coefficients[i].argsort()[-10:]
    top_words = [feature_names[j] for j in top_indices]
    print(f"\nRating {class_label}: {top_words}")



# Save artifacts
import joblib

joblib.dump(tfidf, "tfidf_vectorizer.pkl")
joblib.dump(model, "logreg_model.pkl")