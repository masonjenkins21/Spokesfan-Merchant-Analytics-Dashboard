import joblib
from transformers import pipeline


def train_logreg(X, y):
    from sklearn.linear_model import LogisticRegression

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    )

    model.fit(X, y)

    return model


def save_model(model, path):
    joblib.dump(model, path)


def load_model(path):
    return joblib.load(path)


def load_transformer_model(model_name):
    """
    Loads a transformer sentiment analysis pipeline.

    Parameters:
        model_name: HuggingFace model identifier

    Returns:
        sentiment pipeline
    """

    return pipeline(
        "sentiment-analysis",
        model=model_name
    )


def transformer_score(model, text):

    result = model(text[:512])[0]

    label = result["label"].upper()
    score = result["score"]

    positive = {"POSITIVE", "POS", "LABEL_2"}
    negative = {"NEGATIVE", "NEG", "LABEL_0"}
    neutral = {"NEUTRAL", "NEU", "LABEL_1"}

    if label in positive:
        return score

    if label in negative:
        return -score

    if label in neutral:
        return 0.0

    raise ValueError(f"Unknown label: {label}")