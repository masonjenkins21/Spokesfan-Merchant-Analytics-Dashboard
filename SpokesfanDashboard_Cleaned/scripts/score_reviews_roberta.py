import pandas as pd
from pathlib import Path
from transformers import pipeline
import time



# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed"

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)



# Load RoBERTa Model
print("Loading RoBERTa sentiment model...")

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    truncation=True,
    max_length=512
)



# Find Merchant Review Files
merchant_files = {}

for merchant_folder in RAW_DATA_PATH.iterdir():

    if merchant_folder.is_dir():

        review_file = merchant_folder / "reviews.csv"

        if review_file.exists():
            merchant_files[merchant_folder.name] = review_file


print("\nMerchant review files found:")

for merchant, file in merchant_files.items():
    print(f"{merchant}: {file.name}")



# Sentiment Mapping
sentiment_mapping = {
    "LABEL_0": -1,
    "LABEL_1": 0,
    "LABEL_2": 1,
    "NEG": -1,
    "NEU": 0,
    "POS": 1
}



# Review Text Detection
possible_review_columns = [
    "review_description"
]



# Run Sentiment Analysis
all_reviews = []


for merchant, file_path in merchant_files.items():

    print("\n============================")
    print(f"Processing {merchant}")
    print("============================")

    start_time = time.time()


    reviews = pd.read_csv(file_path)


    print(f"Loaded {len(reviews)} reviews")


    # Create/Fill Product Name
    if "product_name" not in reviews.columns:
        reviews["product_name"] = pd.NA

    if "product_url" in reviews.columns:
        extracted_names = (
            reviews["product_url"]
            .astype(str)
            .str.extract(r"/products/([^/?]+)", expand=False)
            .str.replace("-", " ", regex=False)
            .str.title()
        )

        reviews["product_name"] = (
            reviews["product_name"]
            .fillna(extracted_names)
        )

    # Find review text column
    review_column = None

    for column in possible_review_columns:

        if column in reviews.columns:
            review_column = column
            break


    if review_column is None:

        raise ValueError(
            f"No review text column found for {merchant}. "
            f"Available columns: {reviews.columns.tolist()}"
        )


    print(f"Using review column: {review_column}")

    reviews["review_text"] = (
            reviews["review_title"]
            .fillna("")
            .astype(str)
            + ". "
            +
            reviews["review_description"]
            .fillna("")
            .astype(str)
    )


    # Run RoBERTa
    predictions = sentiment_pipeline(
        reviews["review_text"].tolist(),
        batch_size=16
    )


    reviews["roberta_label"] = [
        prediction["label"]
        for prediction in predictions
    ]


    reviews["roberta_confidence"] = [
        prediction["score"]
        for prediction in predictions
    ]


    reviews["sentiment_score"] = (
        reviews["roberta_label"]
        .map(sentiment_mapping)
    )


    reviews["merchant"] = merchant


    runtime = time.time() - start_time


    print(
        f"Completed {merchant} in {runtime:.2f} seconds"
    )


    all_reviews.append(reviews)




# Combine Merchant Results
final_reviews = pd.concat(
    all_reviews,
    ignore_index=True
)


print("\n========== FINAL DATASET ==========")

print(final_reviews.head())

print("\nSentiment distribution:")

print(
    final_reviews["roberta_label"]
    .value_counts()
)




# Save Output
output_file = (
    OUTPUT_PATH /
    "reviews_with_roberta_sentiment.csv"
)


final_reviews.to_csv(
    output_file,
    index=False
)


print("\nSaved file:")

print(output_file)