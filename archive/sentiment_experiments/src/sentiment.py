# Run VADER
def run_vader(reviews):

    sia = SentimentIntensityAnalyzer()

    reviews["vader_score"] = reviews[
        "clean_text"
    ].apply(
        lambda x: sia.polarity_scores(x)["compound"]
    )

    return reviews

# Run transformer
def run_transformer(
        reviews,
        pipeline,
        column_name
):

    reviews[column_name] = reviews[
        "clean_text"
    ].apply(
        lambda x: bert_score(
            pipeline,
            x
        )
    )

    return reviews