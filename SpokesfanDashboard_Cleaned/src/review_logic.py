from __future__ import annotations

import re
from typing import Any

import pandas as pd


EXCLUDED_PRODUCTS = [
    "Gift Card",
    "Gift Box",
    "Mug",
    "T-Shirt",
]

POSITIVE_PHRASES = [
    "love",
    "luv",
    "favorite",
    "favourite",
    "amazing",
    "excellent",
    "perfect",
    "best",
    "happy",
    "highly recommend",
    "recommend",
    "wonderful",
    "great",
    "beautiful",
    "works great",
    "works perfectly",
    "gentle",
    "soft",
    "smooth",
    "hydrated",
    "glowing",
    "helped my skin",
    "cleared my skin",
    "buy again",
    "repurchase",
    "stocking up",
    "permanent switch",
    "exceeds expectations",
    "exceeded my expectations",
]

DIRECT_COMPLAINT_PHRASES = [
    "did not work",
    "does not work",
    "doesn't work",
    "didn't work",
    "does not seem to work",
    "doesn't seem to work",
    "doesnt seem to work",
    "did not seem to work",
    "doesn't seemed to work",
    "didn't seemed to work",
    "not effective",
    "no results",
    "not seeing results",
    "did nothing",
    "didn't help",
    "did not help",
    "no improvement",
    "made no difference",
    "not helping",
    "stopped working",
    "haven't noticed any difference",
    "have not noticed any difference",
    "not noticed any difference",
    "not worth",
    "waste of money",
    "horrible",
    "terrible",
    "very disappointed",
    "refund",
    "returned",
    "never received",
    "have not received",
    "haven't received",
    "did not receive",
    "didn't receive",
    "not received",
    "products not received",
    "product not received",
    "order not received",
    "never arrived",
    "did not arrive",
    "didn't arrive",
    "missing package",
    "package missing",
    "lost package",
    "lost in the mail",
    "still waiting",
    "tracking says delayed",
    "stuck in transit",
    "caused a rash",
    "gave me a rash",
    "made me get a rash",
    "made me get a red burning rash",
    "burning rash",
    "red rash",
    "made me break out",
    "broke me out",
    "caused irritation",
    "irritated my skin",
    "burned my skin",
    "burning sensation",
    "allergic reaction",
    "made me itch",
    "made my eyes itch",
    "made me feel itchy",
    "felt itchy",
    "broken bottle",
    "bottle was broken",
    "broken lid",
    "lid cracked",
    "cracked lid",
    "broken container",
    "container cracked",
    "packaging broke",
    "packaging is broken",
    "arrived broken",
    "arrived damaged",
    "damaged product",
]

POSITIVE_REACTION_CONTEXT = [
    "no irritation",
    "without irritation",
    "never irritated",
    "didn't irritate",
    "did not irritate",
    "doesn't irritate",
    "does not irritate",
    "no rash",
    "didn't cause a rash",
    "did not cause a rash",
    "doesn't make my eyes itch",
    "does not make my eyes itch",
    "no itching",
    "reduced irritation",
    "reduces irritation",
    "helped my eczema",
    "helps my eczema",
    "reduced redness",
    "reduces redness",
]

THEME_SEVERITY = {
    "Skin Reaction / Sensitivity": 1.00,
    "Shipping and Handling": 0.80,
    "Product Performance": 0.75,
    "Packaging Quality": 0.65,
    "Price / Value": 0.55,
    "Texture": 0.50,
    "Hydration": 0.50,
    "Scent": 0.45,
    "Color / Shade": 0.40,
    "Other Feedback": 0.30,
}


def contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def normalize_text(value: Any) -> str:
    text = str(value).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def safe_rating(value: Any) -> float | None:
    try:
        rating = float(value)
    except (TypeError, ValueError):
        return None

    if pd.isna(rating):
        return None

    return rating


def correct_sentiment(row: pd.Series) -> str:
    text = str(row["review_text"]).lower()
    original = str(row["roberta_label"]).lower()
    rating = safe_rating(row.get("rating"))

    has_positive_context = contains_any(text, POSITIVE_REACTION_CONTEXT)
    has_direct_complaint = contains_any(text, DIRECT_COMPLAINT_PHRASES)
    positive_score = sum(phrase in text for phrase in POSITIVE_PHRASES)

    if has_positive_context and (rating is None or rating >= 4):
        return "positive"

    if has_direct_complaint and (rating is None or rating <= 3):
        return "negative"

    if (
        positive_score >= 1
        and not has_direct_complaint
        and (rating is None or rating >= 4)
    ):
        return "positive"

    return original


def assign_theme(text: Any, sentiment: str) -> str:
    text = str(text).lower()
    sentiment = str(sentiment).lower()

    reaction_terms = [
        "caused a rash",
        "gave me a rash",
        "made me get a rash",
        "made me get a red burning rash",
        "burning rash",
        "red rash",
        "rash",
        "made me break out",
        "broke me out",
        "caused irritation",
        "irritated my skin",
        "burned my skin",
        "burning sensation",
        "burning",
        "allergic reaction",
        "allergic",
        "hives",
        "swelling",
        "swollen",
        "eczema flare",
        "eczema got worse",
        "dermatitis",
        "made me itch",
        "made my eyes itch",
        "made me feel itchy",
        "felt itchy",
        "itchy",
        "itching",
        "eczema",
    ]

    shipping_terms = [
        "never received",
        "have not received",
        "haven't received",
        "did not receive",
        "didn't receive",
        "not received",
        "products not received",
        "product not received",
        "order not received",
        "missing package",
        "package missing",
        "lost package",
        "lost in the mail",
        "lost in mail",
        "never arrived",
        "did not arrive",
        "didn't arrive",
        "still waiting",
        "tracking says delayed",
        "delayed shipment",
        "shipment delayed",
        "stuck in transit",
    ]

    packaging_terms = [
        "broken bottle",
        "bottle was broken",
        "broken lid",
        "lid cracked",
        "cracked lid",
        "broken container",
        "container cracked",
        "packaging broke",
        "packaging is broken",
        "broken packaging",
        "defective packaging",
        "faulty packaging",
        "cap broke",
        "broken cap",
        "arrived broken",
        "arrived damaged",
        "damaged package",
        "damaged product",
    ]

    performance_terms = [
        "does not work",
        "doesn't work",
        "did not work",
        "didn't work",
        "does not seem to work",
        "doesn't seem to work",
        "doesnt seem to work",
        "did not seem to work",
        "doesn't seemed to work",
        "didn't seemed to work",
        "not effective",
        "no results",
        "not seeing results",
        "did nothing",
        "didn't help",
        "did not help",
        "no improvement",
        "made no difference",
        "not helping",
        "stopped working",
        "haven't noticed any difference",
        "have not noticed any difference",
        "not noticed any difference",
    ]

    price_terms = [
        "too expensive",
        "overpriced",
        "not worth",
        "waste of money",
        "poor value",
        "bad value",
        "small for the price",
        "not enough for the price",
    ]

    color_terms = [
        "wrong colour",
        "wrong color",
        "too dark",
        "too light",
        "shade was too dark",
        "shade was too light",
        "color was too dark",
        "colour was too dark",
        "color was too light",
        "colour was too light",
        "not the right shade",
        "shade did not match",
        "shade didn't match",
        "color did not match",
        "colour did not match",
    ]

    texture_terms = [
        "sticky",
        "greasy",
        "oily",
        "gritty",
        "flaky",
        "pilling",
        "too thick",
        "too thin",
        "goopy",
        "slimy",
        "drying",
        "too dry",
        "very dry",
        "hard to apply",
        "difficult to apply",
        "not smooth",
        "does not go on smoothly",
        "did not go on smoothly",
        "doesn't go on smoothly",
        "does not absorb",
        "doesn't absorb",
        "won't stay",
        "does not stay",
        "doesn't stay",
        "smudges",
        "smudged",
        "fallout",
    ]

    hydration_terms = [
        "not hydrating",
        "not moisturizing",
        "made my skin dry",
        "made my lips dry",
        "dried out my skin",
        "dried out my lips",
    ]

    scent_terms = [
        "bad smell",
        "odd smell",
        "strange smell",
        "terrible smell",
        "odor",
        "too fragrant",
        "strong fragrance",
    ]

    if sentiment != "negative":
        return "Not Applicable"

    if contains_any(text, reaction_terms):
        return "Skin Reaction / Sensitivity"
    if contains_any(text, shipping_terms):
        return "Shipping and Handling"
    if contains_any(text, packaging_terms):
        return "Packaging Quality"
    if contains_any(text, performance_terms):
        return "Product Performance"
    if contains_any(text, price_terms):
        return "Price / Value"
    if contains_any(text, color_terms):
        return "Color / Shade"
    if contains_any(text, texture_terms):
        return "Texture"
    if contains_any(text, hydration_terms):
        return "Hydration"
    if contains_any(text, scent_terms):
        return "Scent"

    return "Other Feedback"


def is_true_negative(row: pd.Series) -> bool:
    text = str(row["review_text"]).lower()
    rating = safe_rating(row.get("rating"))

    if (
        contains_any(text, POSITIVE_REACTION_CONTEXT)
        and rating is not None
        and rating >= 4
    ):
        return False

    if contains_any(text, DIRECT_COMPLAINT_PHRASES):
        return True

    if rating is not None and rating <= 2:
        return True

    if (
        rating == 3
        and str(row.get("roberta_label", "")).lower() == "negative"
    ):
        return True

    return False


def prepare_review_data(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = [
        "merchant",
        "product_name",
        "review_text",
        "roberta_label",
        "roberta_confidence",
        "rating",
    ]

    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    working = df.copy()

    working = working[
        ~working["product_name"].str.contains(
            "|".join(EXCLUDED_PRODUCTS),
            case=False,
            na=False,
        )
    ].copy()

    working = working[
        working["review_text"].notna()
        & working["review_text"].astype(str).str.strip().ne("")
    ].copy()

    working["review_text_clean"] = working["review_text"].apply(normalize_text)

    working = (
        working.sort_values(
            ["merchant", "product_name", "roberta_confidence"],
            ascending=[True, True, False],
        )
        .drop_duplicates(
            subset=["merchant", "product_name", "review_text_clean"],
            keep="first",
        )
        .copy()
    )

    working["original_sentiment"] = (
        working["roberta_label"].astype(str).str.lower()
    )

    working["sentiment"] = working.apply(correct_sentiment, axis=1)

    working["is_valid_negative"] = working.apply(
        lambda row: (
            is_true_negative(row)
            if row["sentiment"] == "negative"
            else False
        ),
        axis=1,
    )

    working["theme"] = working.apply(
        lambda row: (
            assign_theme(row["review_text"], row["sentiment"])
            if row["is_valid_negative"]
            else "Not Applicable"
        ),
        axis=1,
    )

    working["theme_severity"] = (
        working["theme"].map(THEME_SEVERITY).fillna(0.0)
    )

    return working
