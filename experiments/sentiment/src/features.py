from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


def get_bow_features(text_series):
    vectorizer = CountVectorizer(
        max_features=5000
    )
    X = vectorizer.fit_transform(text_series)
    return X, vectorizer


def get_tfidf_features(text_series):
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english"
    )

    X = vectorizer.fit_transform(text_series)

    return X, vectorizer