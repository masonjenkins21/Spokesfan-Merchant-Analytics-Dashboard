from src.data import get_merchant_files, load_data
from src.preprocess import apply_preprocessing
from src.models import load_transformer_model, transformer_score
from src.models_config import TRANSFORMER_MODELS

import pandas as pd
from pathlib import Path
import time

project_root = Path(__file__).resolve().parent.parent

processed_dir = project_root / "data" / "processed"

processed_dir.mkdir(
    parents=True,
    exist_ok=True
)


# Development settings
TEST_MODE = True
MAX_REVIEWS = 500

def evaluate_transformer(model_name, model_path, reviews):

    print(f"\nRunning {model_name}...")

    start_time = time.time()

    try:
        transformer = load_transformer_model(model_path)

    except Exception as e:
        print(
            f"Failed to load {model_name}: {e}"
        )

        return {
            "model": model_name,
            "error": str(e)
        }

    scores = []

    for text in reviews["clean_text"]:

        score = transformer_score(
            transformer,
            text
        )

        scores.append(score)

    runtime = time.time() - start_time

    results = pd.DataFrame({
        "score": scores
    })


    summary = {
        "model": model_name,

        "positive_percent": (
                (results["score"] > 0).mean() * 100
        ),

        "neutral_percent": (
                (results["score"] == 0).mean() * 100
        ),

        "negative_percent": (
                (results["score"] < 0).mean() * 100
        ),

        "strong_positive_percent": (
                (results["score"] >= 0.90).mean() * 100
        ),

        "strong_negative_percent": (
                (results["score"] <= -0.90).mean() * 100
        ),

        "average_sentiment_score": (
            results["score"].mean()
        ),

        "sentiment_std": (
            results["score"].std()
        ),

        "average_confidence": (
            results["score"].abs().mean()
        ),

        "runtime_seconds": runtime,

        "reviews_per_second": (
                len(results) / runtime if runtime else 0
        ),

        "net_sentiment": (
                ((results["score"] > 0).mean()
                 - (results["score"] < 0).mean()) * 100
        )
    }

    return summary


all_results = []


merchants = get_merchant_files()

if TEST_MODE:
    merchants = merchants[:1]


for merchant in merchants:

    print(
        f"\n========== {merchant['merchant']} =========="
    )

    _, reviews = load_data(
        merchant["products"],
        merchant["reviews"]
    )

    reviews = apply_preprocessing(
        reviews
    )

    # Limit reviews during testing
    if TEST_MODE:
        reviews = reviews.head(MAX_REVIEWS)

    for model_name, model_info in TRANSFORMER_MODELS.items():

        result = evaluate_transformer(
            model_name,
            model_info["name"],
            reviews
        )

        result["merchant"] = merchant["merchant"]

        all_results.append(result)


results_df = pd.DataFrame(all_results)

# Remove failed models if an error column exists
if "error" in results_df.columns:
    results_df = results_df[
        results_df["error"].isna()
    ]

print("\n--- TRANSFORMER RESULTS ---")

print(
    results_df.to_string(
        index=False
    )
)


results_df.to_csv(
    processed_dir / "transformer_comparison_results.csv",
    index=False
)