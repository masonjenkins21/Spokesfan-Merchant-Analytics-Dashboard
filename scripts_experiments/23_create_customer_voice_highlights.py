"""
Script 23 - Create Customer Voice Highlights

Purpose:
    Create representative positive and negative customer feedback examples
    for Power BI customer insights dashboards.

Creates:
    - customer_voice_highlights.csv

Output includes:
    - merchant
    - product_name
    - highlight_type
    - sentiment
    - theme
    - customer_star_rating
    - feedback_excerpt
    - customer_feedback
    - sentiment_confidence
    - confidence_level
    - feedback_priority
    - feedback_rank
    - pii_redacted
"""

from pathlib import Path
import re

import pandas as pd


# ---------------------------------------------------------
# Configuration and paths
# ---------------------------------------------------------

HIGHLIGHTS_PER_SENTIMENT = 3
MIN_CONFIDENCE = 0.50

project_root = Path(__file__).resolve().parent.parent
processed_path = project_root / "data" / "processed"
dashboard_path = processed_path / "dashboard_metrics"

sentiment_file = processed_path / "reviews_with_roberta_sentiment.csv"
output_file = dashboard_path / "customer_voice_highlights.csv"


# ---------------------------------------------------------
# Shared phrase lists
# ---------------------------------------------------------

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
    "would highly recommend",
    "would recommend",
    "recommend",
    "amazing product",
    "drastic change",
    "scars are fading",
    "have not had a new pimple",
    "excited to see",
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

STRONG_POSITIVE_OUTCOME_PHRASES = [
    "amazing product",
    "would recommend",
    "would highly recommend",
    "drastic change",
    "scars are fading",
    "have not had a new pimple",
    "cleared up my acne",
    "helped improve my skin",
    "works wonders",
]


DIRECT_COMPLAINT_PHRASES = [
    "did not work",
    "does not work",
    "doesn't work",
    "didn't work",
    "not effective",
    "no results",
    "did nothing",
    "didn't help",
    "did not help",
    "no improvement",
    "made no difference",
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
    "never arrived",
    "did not arrive",
    "missing package",
    "package missing",
    "lost package",
    "lost in the mail",
    "caused a rash",
    "gave me a rash",
    "made me break out",
    "broke me out",
    "caused irritation",
    "irritated my skin",
    "burned my skin",
    "burning sensation",
    "allergic reaction",
    "made me itch",
    "made my eyes itch",
    "not received",
    "products not received",
    "product not received",
    "order not received",
    "didn't receive",
    "didn't arrive",
    "still waiting",
    "tracking says delayed",
    "stuck in transit",
    "does not seem to work",
    "doesn't seem to work",
    "doesnt seem to work",
    "did not seem to work",
    "not seeing results",
    "not helping",
    "stopped working",
    "doesn't seemed to work",
    "didn't seemed to work",
    "burning rash",
    "red rash",
    "made me get a rash",
    "made me get a red burning rash",
    "broken bottle",
    "broken lid",
    "broken container",
    "cracked lid",
    "arrived broken",
    "arrived damaged",
    "damaged product",
    "bottle was broken",
    "packaging broke",
    "packaging is broken",
    "lid cracked",
    "container cracked",
    "made me feel itchy",
    "felt itchy",
    "haven't noticed any difference",
    "have not noticed any difference",
    "not noticed any difference",
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


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def normalize_text(value) -> str:
    text = str(value).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def safe_rating(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def correct_sentiment(row) -> str:
    """
    Apply only conservative corrections to the RoBERTa label.

    Rating and explicit phrases are used as supporting evidence. Broad words
    such as "rash", "itch", or "burn" do not automatically make a review
    negative because they may occur in positive statements such as
    "no irritation" or "doesn't make my eyes itch."
    """

    text = str(row["review_text"]).lower()
    original = str(row["roberta_label"]).lower()
    rating = safe_rating(row["rating"])

    has_positive_context = contains_any(text, POSITIVE_REACTION_CONTEXT)
    has_direct_complaint = contains_any(text, DIRECT_COMPLAINT_PHRASES)
    positive_score = sum(phrase in text for phrase in POSITIVE_PHRASES)

    # Clear complaint supported by a low rating.
    if has_direct_complaint and (rating is None or rating <= 3):
        return "negative"

    # Strong positive evidence supported by a high rating.
    if (
        positive_score >= 1
        and not has_direct_complaint
        and (rating is None or rating >= 4)
    ):
        return "positive"

    strong_positive_outcome = contains_any(
        text,
        STRONG_POSITIVE_OUTCOME_PHRASES,
    )

    # A clearly successful 5-star product outcome should override generic
    # negative language describing the customer's condition or prior products.
    if (
        rating is not None
        and rating == 5
        and strong_positive_outcome
        and positive_score >= 1
    ):
        return "positive"

    # Strongly positive 4- or 5-star reviews should not remain negative
    # simply because the model produced a false-negative label.
    if (
        rating is not None
        and rating >= 4
        and positive_score >= 2
        and not has_direct_complaint
    ):
        return "positive"

    # Explicitly positive reaction language should not be treated as a complaint.
    if has_positive_context and (rating is None or rating >= 4):
        return "positive"

    return original


def has_explicit_texture_complaint(text):
    """
    Require an explicit texture/application phrase before assigning Texture.
    """

    text = str(text).lower()

    texture_evidence = [
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
        "too heavy",
        "feels heavy",
        "products were too heavy",
        "slide down",
        "slides down",
    ]

    return contains_any(text, texture_evidence)


def assign_theme(text, sentiment):
    """
    Assign one dashboard theme using the corrected sentiment.

    Negative categories are evaluated only for negative reviews, preventing
    positive testimonials that mention past sensitivity from becoming issues.
    """

    text = str(text).lower()
    sentiment = str(sentiment).lower()

    reaction_terms = [
        "caused a rash",
        "gave me a rash",
        "made me break out",
        "broke me out",
        "caused irritation",
        "irritated my skin",
        "burned my skin",
        "burning sensation",
        "allergic reaction",
        "hives",
        "swelling",
        "swollen",
        "eczema flare",
        "eczema got worse",
        "dermatitis",
        "made me itch",
        "made my eyes itch",
        "burning rash",
        "red rash",
        "made me get a rash",
        "made me get a red burning rash",
        "rash",
        "burning",
        "itchy",
        "itching",
        "made me feel itchy",
        "felt itchy",
        "eczema",
        "eyes started burning",
        "eyes started to burn",
        "eyes started itching",
        "eyes started to itch",
        "eyes itch",
        "eyes water",
        "eyes watering",
        "itch and water",
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
        "damaged package",
        "broken package",
        "broken packaging",
        "delayed shipment",
        "shipment delayed",
        "stuck in transit",
        "arrived broken",
        "arrived damaged",
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
        "defective packaging",
        "faulty packaging",
        "cap broke",
        "broken cap",
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
        "doesn't seemed to work",
        "didn't seemed to work",
        "haven't noticed any difference",
        "have not noticed any difference",
        "not noticed any difference",
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
        "fallout"
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
        "colour did not match"
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

    hydration_complaint_terms = [
        "not hydrating",
        "not moisturizing",
        "made my skin dry",
        "made my lips dry",
        "dried out my skin",
        "dried out my lips",
        "drying",
    ]

    skin_benefit_terms = [
        "helped my skin",
        "helps my skin",
        "cleared my skin",
        "cleared my acne",
        "reduced redness",
        "reduces redness",
        "no irritation",
        "without irritation",
        "never irritated",
        "didn't irritate",
        "did not irritate",
        "doesn't irritate",
        "does not irritate",
        "doesn't make my eyes itch",
        "does not make my eyes itch",
        "sensitive skin approved",
        "helped my eczema",
        "helps my eczema",
        "hydrated",
        "glowing",
        "soft skin",
    ]

    if sentiment == "negative":
        if contains_any(text, reaction_terms):
            return "Skin Reaction / Sensitivity"
        if contains_any(text, shipping_terms):
            return "Shipping and Handling"
        if contains_any(text, packaging_terms):
            return "Packaging Quality"
        if contains_any(text, hydration_complaint_terms):
            return "Hydration"
        if (
            contains_any(text, texture_terms)
            and has_explicit_texture_complaint(text)
        ):
            return "Texture"
        if contains_any(text, performance_terms):
            return "Product Performance"
        if contains_any(text, price_terms):
            return "Price / Value"
        if contains_any(text, color_terms):
            return "Color / Shade"
        if contains_any(text, scent_terms):
            return "Scent"
        return "Other Feedback"

    if contains_any(text, skin_benefit_terms):
        return "Skin Benefits / Improvement"

    return "Positive Experience"



def refine_theme(row):
    """
    Apply a final targeted theme correction using the complete review text.

    This runs after the general rule-based assignment and handles a small
    number of high-value phrases that should always map to a specific theme.
    """

    text = str(row["review_text"]).lower()
    sentiment = str(row["sentiment"]).lower()
    current_theme = str(row["theme"])

    if sentiment != "negative":
        return current_theme

    packaging_phrases = [
        "broken pump",
        "but broken pump",
        "pump broke",
        "pump was broken",
        "dropper got stuck",
        "dropper gets stuck",
        "dropper is stuck",
        "stuck with product",
        "faulty packaging",
    ]

    hydration_phrases = [
        "does not hydrate my lips long enough",
        "doesn't hydrate my lips long enough",
        "hydrate my lips long enough",
        "not hydrating enough",
        "dry lips",
        "keep my lips hydrated",
        "lips hydrated",
    ]

    explicit_texture_phrases = [
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
        "too heavy",
        "feels heavy",
        "slide down",
        "slides down",
    ]

    if contains_any(text, packaging_phrases):
        return "Packaging Quality"

    if contains_any(text, hydration_phrases):
        return "Hydration"

    if (
        current_theme == "Texture"
        and not contains_any(text, explicit_texture_phrases)
    ):
        return "Other Feedback"

    return current_theme

def is_true_negative(row) -> bool:
    """
    Keep a negative review when the label is supported by rating or explicit
    complaint language. This blocks positive testimonials that RoBERTa
    incorrectly labeled negative.
    """

    text = str(row["review_text"]).lower()
    rating = safe_rating(row["rating"])

    positive_score = sum(
        phrase in text
        for phrase in POSITIVE_PHRASES
    )

    has_direct_complaint = contains_any(
        text,
        DIRECT_COMPLAINT_PHRASES,
    )

    if (
        contains_any(text, POSITIVE_REACTION_CONTEXT)
        and rating is not None
        and rating >= 4
    ):
        return False

    strong_positive_outcome = contains_any(
        text,
        STRONG_POSITIVE_OUTCOME_PHRASES,
    )

    # Prevent successful 5-star testimonials from entering the concern table,
    # even when they mention prior acne, scars, or products that did not work.
    if (
        rating is not None
        and rating == 5
        and strong_positive_outcome
        and positive_score >= 1
    ):
        return False

    # Do not allow strongly positive high-rating reviews into the concern table.
    if (
        rating is not None
        and rating >= 4
        and positive_score >= 2
        and not has_direct_complaint
    ):
        return False

    if has_direct_complaint:
        return True

    if rating is not None and rating <= 2:
        return True

    # A 3-star review may represent a legitimate mixed concern.
    if rating == 3 and str(row["roberta_label"]).lower() == "negative":
        return True

    return False


def redact_personal_information(value):
    """
    Remove clear personally identifiable information from dashboard text.

    Redacts:
        - email addresses
        - phone numbers
        - Canadian postal codes
        - US ZIP codes
        - explicit street addresses

    The patterns are intentionally conservative to avoid removing ordinary
    review language.
    """

    text = str(value).replace("\n", " ").strip()
    original_text = text

    patterns = [
        # Email addresses
        (
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            "[email removed]",
        ),

        # North American phone numbers
        (
            r"(?<!\d)(?:\+?1[\s.-]?)?"
            r"(?:\(?\d{3}\)?[\s.-]?)"
            r"\d{3}[\s.-]?\d{4}(?!\d)",
            "[phone removed]",
        ),

        # Canadian postal codes
        (
            r"\b[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z]"
            r"[ -]?\d[ABCEGHJ-NPRSTV-Z]\d\b",
            "[postal code removed]",
        ),

        # US ZIP codes
        (
            r"\b\d{5}(?:-\d{4})?\b",
            "[postal code removed]",
        ),

        # Explicit street addresses beginning with a street number
        (
            r"\b\d{1,6}\s+"
            r"(?:[A-Za-z0-9.'-]+\s+){0,5}"
            r"(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|"
            r"Drive|Dr|Lane|Ln|Court|Ct|Way|Place|Pl)\.?\b",
            "[address removed]",
        ),
    ]

    for pattern, replacement in patterns:
        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE,
        )

    # Remove a likely full name immediately before a redacted address.
    text = re.sub(
        r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\s*,?\s*"
        r"(?=\[address removed\])",
        "[personal details removed] ",
        text,
    )

    text = re.sub(r"\s+", " ", text).strip()

    redaction_markers = [
        "[email removed]",
        "[phone removed]",
        "[postal code removed]",
        "[address removed]",
        "[personal details removed]",
    ]

    was_redacted = any(
        marker in text
        for marker in redaction_markers
    )

    return text, was_redacted


def is_customer_caused_damage(text):
    """
    Identify reviews where damage was clearly caused by the customer,
    a pet, or an accident rather than by the product itself.
    """

    text = str(text).lower()

    customer_damage_terms = [
        "my dog chewed",
        "dog chewed",
        "my cat chewed",
        "cat chewed",
        "chewed a hole",
        "my dog couldn’t resist",
        "my dog couldn't resist",
        "dog couldn’t resist",
        "dog couldn't resist",
        "she decided to chew",
        "he decided to chew",
        "pet chewed",
        "i dropped it",
        "dropped it",
        "i broke it",
        "accidentally broke",
        "accidentally damaged",
        "left it in the car",
        "ran over it",
    ]

    return contains_any(text, customer_damage_terms)

def create_excerpt(text, limit=200):
    text = str(text).replace("\n", " ").strip()

    if len(text) <= limit:
        return text

    excerpt = text[:limit]

    if "." in excerpt:
        excerpt = excerpt.rsplit(".", 1)[0] + "."
    else:
        excerpt += "..."

    return excerpt


# ---------------------------------------------------------
# Load and validate input
# ---------------------------------------------------------

print("\nCreating customer voice highlights...\n")
print("Loading sentiment data...")

df = pd.read_csv(sentiment_file, low_memory=False)

required_columns = [
    "merchant",
    "product_name",
    "review_text",
    "roberta_label",
    "roberta_confidence",
    "rating",
]

missing_columns = [column for column in required_columns if column not in df.columns]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

print(f"Loaded {len(df)} reviews")
print("\nOriginal RoBERTa sentiment distribution:")
print(df["roberta_label"].value_counts(dropna=False))


# ---------------------------------------------------------
# Basic cleanup
# ---------------------------------------------------------

print("\nRemoving non-product items...")

exclude_products = [
    "Gift Card",
    "Gift Box",
    "Mug",
    "T-Shirt",
]

df = df[
    ~df["product_name"].str.contains(
        "|".join(exclude_products),
        case=False,
        na=False,
    )
].copy()

df = df[
    df["roberta_label"].isin(["positive", "negative"])
    & df["review_text"].notna()
    & df["review_text"].str.strip().ne("")
].copy()

df["review_text_clean"] = df["review_text"].apply(normalize_text)

df = (
    df.sort_values(
        ["merchant", "product_name", "roberta_confidence"],
        ascending=[True, True, False],
    )
    .drop_duplicates(
        subset=["merchant", "product_name", "review_text_clean"],
        keep="first",
    )
    .copy()
)

print(f"Remaining reviews after cleanup: {len(df)}")


# ---------------------------------------------------------
# Conservative sentiment correction
# ---------------------------------------------------------

print("\nCorrecting obvious sentiment mismatches...")

df["original_sentiment"] = df["roberta_label"]
df["sentiment"] = df.apply(correct_sentiment, axis=1)

print("\nCorrected sentiment distribution:")
print(df["sentiment"].value_counts(dropna=False))


# ---------------------------------------------------------
# Theme assignment
# ---------------------------------------------------------

print("\nAssigning review themes...")

df["theme"] = df.apply(
    lambda row: assign_theme(row["review_text"], row["sentiment"]),
    axis=1,
)

df["theme"] = df.apply(
    refine_theme,
    axis=1,
)

print("\nTheme distribution:")
print(df["theme"].value_counts())


# ---------------------------------------------------------
# Confidence and validation flags
# ---------------------------------------------------------

df["confidence_level"] = "Low"
df.loc[df["roberta_confidence"] >= 0.60, "confidence_level"] = "Medium"
df.loc[df["roberta_confidence"] >= 0.85, "confidence_level"] = "High"

df["is_valid_negative"] = df.apply(
    lambda row: is_true_negative(row) if row["sentiment"] == "negative" else True,
    axis=1,
)

df = df[
    (df["sentiment"] == "positive")
    | ((df["sentiment"] == "negative") & df["is_valid_negative"])
].copy()

df = df[df["roberta_confidence"] >= MIN_CONFIDENCE].copy()


# ---------------------------------------------------------
# Select positive and negative highlights separately
# ---------------------------------------------------------

print("\nSelecting customer highlights...")

positive_reviews = df[df["sentiment"] == "positive"].copy()
negative_reviews = df[df["sentiment"] == "negative"].copy()

negative_reviews = negative_reviews[
    ~negative_reviews["review_text"].apply(is_customer_caused_damage)
].copy()

positive_reviews["highlight_type"] = "Customer Favorite"
negative_reviews["highlight_type"] = "Customer Concern"

positive_reviews["selection_priority"] = 1

negative_theme_priority = {
    "Skin Reaction / Sensitivity": 1,
    "Shipping and Handling": 2,
    "Packaging Quality": 3,
    "Product Performance": 4,
    "Price / Value": 5,
    "Texture": 6,
    "Color / Shade": 7,
    "Hydration": 8,
    "Scent": 9,
    "Other Feedback": 10
}

negative_reviews["selection_priority"] = (
    negative_reviews["theme"].map(negative_theme_priority).fillna(8)
)

# Remove duplicate review text across products within each merchant before
# selecting highlights. This prevents the same customer review from appearing
# repeatedly for bundles, kits, and individual component products.
positive_candidates = (
    positive_reviews
    .sort_values(
        [
            "merchant",
            "roberta_confidence",
            "product_name",
        ],
        ascending=[
            True,
            False,
            True,
        ],
    )
    .drop_duplicates(
        subset=[
            "merchant",
            "review_text_clean",
        ],
        keep="first",
    )
    .copy()
)

negative_candidates = (
    negative_reviews
    .sort_values(
        [
            "merchant",
            "selection_priority",
            "roberta_confidence",
            "product_name",
        ],
        ascending=[
            True,
            True,
            False,
            True,
        ],
    )
    .drop_duplicates(
        subset=[
            "merchant",
            "review_text_clean",
        ],
        keep="first",
    )
    .copy()
)


positive_highlights = (
    positive_candidates
    .sort_values(
        [
            "merchant",
            "product_name",
            "roberta_confidence",
        ],
        ascending=[
            True,
            True,
            False,
        ],
    )
    .groupby(
        [
            "merchant",
            "product_name",
        ],
        group_keys=False,
    )
    .head(HIGHLIGHTS_PER_SENTIMENT)
    .copy()
)

negative_highlights = (
    negative_candidates
    .sort_values(
        [
            "merchant",
            "product_name",
            "selection_priority",
            "roberta_confidence",
        ],
        ascending=[
            True,
            True,
            True,
            False,
        ],
    )
    .groupby(
        [
            "merchant",
            "product_name",
        ],
        group_keys=False,
    )
    .head(HIGHLIGHTS_PER_SENTIMENT)
    .copy()
)


# Rank selected feedback within each product and highlight type.
# Rank 1 is the strongest representative review for the dashboard.
positive_highlights["feedback_rank"] = (
    positive_highlights
    .groupby(
        [
            "merchant",
            "product_name",
        ]
    )
    .cumcount()
    + 1
)

negative_highlights["feedback_rank"] = (
    negative_highlights
    .groupby(
        [
            "merchant",
            "product_name",
        ]
    )
    .cumcount()
    + 1
)

highlights = pd.concat(
    [positive_highlights, negative_highlights],
    ignore_index=True,
)


# ---------------------------------------------------------
# Format dashboard output
# ---------------------------------------------------------

highlights = highlights.rename(
    columns={
        "rating": "customer_star_rating",
        "review_text": "customer_feedback",
        "roberta_confidence": "sentiment_confidence",
    }
)

highlights["sentiment"] = highlights["sentiment"].str.capitalize()

redaction_results = (
    highlights["customer_feedback"]
    .apply(redact_personal_information)
)

highlights["customer_feedback"] = (
    redaction_results
    .str[0]
)

highlights["pii_redacted"] = (
    redaction_results
    .str[1]
)

highlights["feedback_excerpt"] = (
    highlights["customer_feedback"]
    .apply(create_excerpt)
)

highlights["feedback_priority"] = "Low"

highlights.loc[
    (highlights["highlight_type"] == "Customer Concern")
    & highlights["theme"].isin(
        [
            "Skin Reaction / Sensitivity",
            "Shipping and Handling",
            "Product Performance",
        ]
    ),
    "feedback_priority",
] = "High"

highlights.loc[
    (highlights["highlight_type"] == "Customer Concern")
    & highlights["theme"].isin(
        [
            "Packaging Quality",
            "Price / Value",
            "Texture",
            "Color / Shade",
            "Hydration",
            "Scent",
        ]
    ),
    "feedback_priority",
] = "Medium"

# ---------------------------------------------------------
# Final dashboard columns
# ---------------------------------------------------------

highlights = highlights[
    [
        "merchant",
        "product_name",
        "highlight_type",
        "sentiment",
        "theme",
        "customer_star_rating",
        "feedback_excerpt",
        "customer_feedback",
        "sentiment_confidence",
        "confidence_level",
        "feedback_priority",
        "feedback_rank",
        "pii_redacted",
    ]
]



# ---------------------------------------------------------
# Sort dashboard output
# ---------------------------------------------------------

priority_order = {
    "High": 1,
    "Medium": 2,
    "Low": 3,
}


highlights["feedback_priority_order"] = (
    highlights["feedback_priority"]
    .map(priority_order)
)


highlights = highlights.sort_values(
    [
        "merchant",
        "product_name",
        "highlight_type",
        "feedback_priority_order",
        "feedback_rank",
    ],
    ascending=[
        True,
        True,
        True,
        True,
        True,
    ],
)


highlights = highlights.drop(
    columns=["feedback_priority_order"]
)


# ---------------------------------------------------------
# Validation output
# ---------------------------------------------------------

print(f"Positive reviews available: {len(positive_reviews)}")
print(f"Validated negative reviews available: {len(negative_reviews)}")
print(f"Selected highlights: {len(highlights)}")
print(
    "Rows with personal information redacted: "
    f"{int(highlights['pii_redacted'].sum())}"
)

duplicate_check = (
    highlights[
        highlights["highlight_type"] == "Customer Concern"
    ]
    .duplicated(
        subset=[
            "merchant",
            "customer_feedback",
        ],
        keep=False,
    )
    .sum()
)

print(
    "Duplicate concern excerpts remaining across products: "
    f"{duplicate_check}"
)

high_rating_concerns = highlights[
    (highlights["highlight_type"] == "Customer Concern")
    & (highlights["customer_star_rating"] >= 4)
]

print(
    "High-rating customer concerns remaining: "
    f"{len(high_rating_concerns)}"
)

print("\nNegative highlight validation:")
negative_preview = highlights[
    highlights["highlight_type"] == "Customer Concern"
][
    [
        "product_name",
        "theme",
        "customer_star_rating",
        "customer_feedback",
    ]
].head(30)

if negative_preview.empty:
    print("No negative highlights found.")
else:
    print(negative_preview.to_string(index=False))


# ---------------------------------------------------------
# Save output
# ---------------------------------------------------------

print("\nSaving customer voice highlights...")

dashboard_path.mkdir(parents=True, exist_ok=True)
highlights.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig",
)

print(f"Saved {len(highlights)} customer voice highlights")
print(f"Location: {output_file}")