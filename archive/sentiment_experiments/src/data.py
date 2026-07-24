from pathlib import Path
import pandas as pd


# Project directories
project_root = Path(__file__).resolve().parent.parent
data_dir = project_root / "data" / "raw"


# Load a merchant's datasets
def load_data(products_file, reviews_file):
    products = pd.read_csv(products_file)
    reviews = pd.read_csv(reviews_file)

    reviews["review_description"] = (
        reviews["review_description"]
        .fillna("")
    )

    return products, reviews


# Find every merchant folder and its datasets
def get_merchant_files():
    merchants = []

    # Loop through every folder inside data/raw
    for merchant_folder in sorted(data_dir.iterdir()):

        # Skip anything that isn't a folder
        if not merchant_folder.is_dir():
            continue

        merchants.append({
            "merchant": merchant_folder.name,
            "products": merchant_folder / "products.csv",
            "reviews": merchant_folder / "reviews.csv"
        })

    return merchants



# Retrieve one specific merchant
def get_merchant(name):
    merchants = get_merchant_files()

    for merchant in merchants:
        if merchant["merchant"] == name:
            return merchant

    available = [
        merchant["merchant"]
        for merchant in merchants
    ]

    raise ValueError(
        f"Merchant '{name}' not found. Available merchants: {available}"
    )