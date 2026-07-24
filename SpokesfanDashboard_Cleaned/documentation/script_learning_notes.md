# Script 01 – Data Exploration Findings

---

## Objective

Explore the product and review datasets to understand their structure, identify data quality issues, and gather insights before beginning sentiment analysis.

---

## Key Findings

- Product dataset contains **863 rows** and **48 columns**.
- Review dataset contains **5,571 reviews** across **46 unique products**.
- Product data includes multiple rows per product due to product variants.
- Several Google Shopping columns are completely empty and are unlikely to be useful.
- Only **20 reviews** are missing sentiment values, while only **2 reviews** are missing review text.

---

## Ratings

- **91.15%** of reviews are 5-star ratings.
- Customer reviews are overwhelmingly positive, creating an imbalanced dataset.

---

## Existing Sentiment

- Sentiment scores generally increase as star ratings increase.
- One review containing only ❤ emojis received a sentiment score of **-1.0**, indicating possible issues with the existing sentiment model.
- Some low-rated reviews still have relatively high sentiment scores, showing that review text and star ratings do not always align.

---

## Review Characteristics

- Average review length is **157 characters**.
- Reviews range from very short comments to detailed feedback over **1,500 characters**, providing rich text for NLP.

---

## Next Steps

- Preprocess review text.
- Tokenize and clean the reviews.
- Build Bag of Words and TF-IDF representations.
- Generate sentiment using VADER.
- Compare generated sentiment with the provided sentiment values.
- Evaluate transformer-based models (BERT) for contextual sentiment analysis.

---

# Script 02 – Text Preprocessing Findings

## Objective

Prepare review text for sentiment analysis by cleaning, normalizing, and standardizing raw text into a consistent format suitable for NLP modeling.

---

## Key Steps Performed

- Lowercasing all text to ensure consistency
- Removed punctuation and special characters
- Tokenized text into individual words (tokens)
- Removed stop words (e.g., "the", "and", "is")
- Applied lemmatization to reduce words to base form

---

## Example Transformation

**Original Review:**
I have tried a lot of primers looking for any that have a smoothing effect for oily skin.

**Cleaned Output:**
tried lot primer looking smoothing effect oily skin smooth look natural glow

---

## Key Observations

- Text becomes significantly shorter and more focused after preprocessing.
- Most meaningful information is preserved (e.g., product features like “oily skin”, “glow”, “primer”).
- Stop word removal effectively removes grammatical noise but may slightly reduce readability.
- Lemmatization reduces word variation, but some words remain context-dependent (e.g., “looking” vs “look”).

---

## Important Insight

- Preprocessing improves consistency but does NOT fully preserve meaning.
- Context is partially lost when words are separated (motivation for later use of transformers like BERT).

---

## Issues Encountered

- NLTK resource dependencies required manual downloads (`punkt`, `punkt_tab`, `stopwords`, `wordnet`).
- Missing feature column (`review_length`) caused errors when scripts were not reused across files.

---

## Next Steps

- Convert cleaned text into numerical representations:
  - Bag of Words (CountVectorizer)
  - TF-IDF weighting
- Begin sentiment modeling using VADER
- Compare rule-based sentiment vs existing dataset sentiment
- Prepare for transformer-based contextual sentiment analysis (BERT/Hugging Face)


# Script 03 – Feature Extraction (Bag of Words & TF-IDF)

## Objective

Convert cleaned review text into numerical representations that can be used for machine learning models such as sentiment analysis.

This script introduces two key text vectorization techniques:
- Bag of Words (BoW)
- TF-IDF (Term Frequency–Inverse Document Frequency)

---

## Data Preparation

- Used cleaned review text from Script 2 (`clean_text` column)
- Removed punctuation, stopwords, and performed lemmatization
- Filtered vocabulary to include only alphabetic tokens
- Limited vocabulary size to top 5,000 features for efficiency

---

## Bag of Words (BoW)

- Converts text into word frequency counts
- Each review is represented as a vector of raw word counts
- Output shape: **(5571 reviews, 4604 unique words)**

### Key Insight:
- BoW captures **how often words appear**, but not importance or context
- Common words like “love” and “great” dominate counts across reviews
- Does not account for word rarity or informativeness

---

## TF-IDF Representation

- Improves on BoW by weighting words based on importance
- Reduces weight of common words across all reviews
- Increases weight of more unique, informative words

### Output Shape:
- Same dimensionality as BoW: **(5571, 4604)**

### Key Insight:
- TF-IDF provides a **more meaningful representation than raw counts**
- Words like “love”, “great”, and “easy” still appear, but are weighted by how distinctive they are across reviews

---

## Example Review Breakdown

A sample review was analyzed in both formats:

### Bag of Words Example
Shows raw frequency of words:
- "primer": 2
- "looking": 2
- "smooth": 1

### TF-IDF Example
Shows weighted importance of words:
- primer → 0.39
- looking → 0.38
- smoothing → 0.33

---

## Global TF-IDF Insights

Most important words across the dataset:

- love
- colour
- great
- product
- easy
- lip / lipstick
- smooth
- skin
- beautiful
- blend

### Interpretation:
- Reviews are strongly positive in tone
- Product experience themes dominate (beauty, application, feel)
- TF-IDF highlights both emotional language (“love”, “great”) and product attributes (“smooth”, “blend”, “lipstick”)

---

## Key Takeaways

- Bag of Words is useful for understanding **frequency of terms**
- TF-IDF improves representation by emphasizing **informative words**
- Both methods convert text into a format usable for machine learning models
- This step prepares the dataset for **sentiment analysis and classification models**

---

## Next Steps

- Use TF-IDF features for sentiment classification models
- Compare performance of:
  - VADER sentiment scoring
  - Logistic Regression / Naive Bayes
  - Transformer-based models (BERT/Hugging Face)
- Begin sentiment evaluation against existing ratings and sentiment column


# Script 04 – Sentiment Analysis (VADER)

## Objective

Apply a rule-based sentiment model (VADER) to review text and evaluate how well it aligns with star ratings and the dataset’s existing sentiment column.

---

## Model Overview

- Used VADER (Valence Aware Dictionary and sEntiment Reasoner)
- Outputs a compound sentiment score from -1 (negative) to +1 (positive)
- Generates a baseline sentiment representation of review text
- Compared against:
  - Star ratings (1–5)
  - Existing sentiment column in dataset

---

## Key Findings

### 1. Strong directional alignment with star ratings

Average VADER sentiment increases consistently with rating:

- 1★ → 0.07  
- 2★ → 0.13  
- 3★ → 0.43  
- 4★ → 0.69  
- 5★ → 0.75  

This confirms that VADER correctly captures **sentiment direction across rating levels**.

---

### 2. Moderate correlation with star ratings

- Correlation between VADER score and rating: **0.24**

Interpretation:
- VADER captures sentiment signal
- but does not fully explain rating intensity or nuance

This is expected.

---

### 3. Existing sentiment column vs VADER comparison

The dataset already contained a sentiment score column (previously assumed to be a sentiment model output).

Comparison results:

- Correlation (existing sentiment vs VADER): **0.36**
- Directional agreement: **0.94**

Summary interpretation:
- Both systems strongly agree on sentiment direction
- However, they differ in magnitude (scaling differences exist)
- This suggests the existing sentiment column is likely derived from a similar rule-based or lightweight model

---

### 4. Distribution differences

- Existing sentiment:
  - Highly compressed toward positive values
  - Mean: **0.92**
  - Narrow range: mostly 0.95–0.99

- VADER sentiment:
  - Wider distribution
  - Mean: **0.74**
  - Includes clear negative values (down to -0.92)

Key insight:
- Existing sentiment is **overly optimistic / compressed**
- VADER provides a more realistic sentiment spread

---

### 5. Model limitations

VADER struggles with:
- domain-specific beauty product language
- nuanced phrasing (“not bad”, “I didn’t expect this to work”)
- emotional vs functional satisfaction mismatch

Despite this, it remains a strong baseline for sentiment analysis.

---

## Key Insight

While VADER and the existing sentiment column are **strongly aligned in direction**, they differ significantly in scale and distribution.

This suggests:
- The dataset sentiment column is not a fully independent sentiment model
- VADER provides a more generalizable baseline

---

## Next Steps

- Compare VADER with TF-IDF + Logistic Regression model (Script 05)
- Evaluate whether supervised ML improves alignment with ratings
- Prepare for transformer-based sentiment analysis (BERT / Hugging Face)


# Script 05 – TF-IDF + Logistic Regression Sentiment Model

## Objective

Build a supervised machine learning model to predict product review star ratings (1–5) using TF-IDF features. This serves as the primary classical ML approach for sentiment classification.

---

## Model Approach

- Input: Cleaned review text (TF-IDF representation)
- Output: Star rating (1–5)
- Algorithm: Logistic Regression (multiclass classification)
- Feature type: TF-IDF weighted word vectors

TF-IDF was used because it weights words by importance across the corpus, reducing the impact of overly common terms while emphasizing more informative words.

---

## Dataset Characteristics

- Strong class imbalance:
  - ~91% of reviews are 5-star ratings
  - Very few low-star reviews (1–2 stars)

This imbalance impacts model performance, particularly for minority classes.

---

## Model Performance

- Accuracy: ~0.80

### Key Observations:
- Strong performance on 5-star reviews (majority class)
- Weak performance on 1–3 star reviews due to limited training examples
- Macro-average metrics are significantly lower than weighted averages, confirming class imbalance effects

---

## Feature Insights

Top predictive words by class show clear sentiment separation:

- **1-star:** broken, scratch, return, disappointed
- **2-star:** fade, slip, wrong, hard
- **3-star:** issue, smudge, thought, difference
- **4-star:** creamy, smooth, finish, slightly
- **5-star:** perfect, love, amazing, gorgeous, highly

This confirms that the model is capturing meaningful sentiment patterns.

---

## Key Insight

- The model learns strong patterns for extreme positive sentiment but struggles with minority classes due to imbalance.
- Despite this, TF-IDF + Logistic Regression provides a solid baseline for sentiment prediction.

---

## Conclusion

This model demonstrates that classical NLP techniques can effectively capture sentiment from customer reviews, but performance is limited by dataset imbalance.

It serves as a strong baseline for comparison against:
- VADER (rule-based sentiment)
- Transformer-based models (BERT) in Script 06

---

## Next Steps

- Evaluate transformer-based sentiment using BERT
- Compare performance against:
  - VADER (Script 04)
  - TF-IDF + Logistic Regression (Script 05)
- Analyze whether contextual embeddings improve classification of nuanced reviews


# Script 06 – Transformer-Based Sentiment Analysis (DistilBERT)

## Objective
Apply a transformer-based sentiment model (DistilBERT) to evaluate whether contextual language models outperform rule-based (VADER) and classical ML (TF-IDF + Logistic Regression) approaches.

This represents the most advanced sentiment modeling method in the project.

---

## Key Steps

### 1. Data Preparation
- Loaded full review dataset (5,571 reviews).
- Filled missing review text values to avoid processing errors.
- Created a sampled subset of 1,000 reviews for faster inference.

---

### 2. Model Selection (DistilBERT)
- Used pretrained Hugging Face sentiment model:
  - `distilbert-base-uncased-finetuned-sst-2-english`
- This model is trained on general sentiment classification (positive/negative).

**Key Insight:**
- Unlike VADER and TF-IDF models, DistilBERT uses contextual embeddings rather than word-based rules or counts.

---

### 3. Sentiment Scoring Method
- Model outputs:
  - Label: POSITIVE or NEGATIVE
  - Confidence score (0 to 1)

- Converted output into numeric sentiment:
  - Positive → +score  
  - Negative → -score  

This allows direct comparison with:
- VADER scores
- Star ratings

---

### 4. Handling Long Reviews
- Reviews longer than 512 tokens were truncated.
- This is a limitation of transformer models.

---

### 5. Aggregation by Star Rating
- Computed average DistilBERT sentiment per rating group.

**Results:**
- 1★ → -0.996  
- 2★ → -0.333  
- 3★ → -0.173  
- 4★ → 0.642  
- 5★ → 0.954  

---

## Key Takeaways

### 1. Strong alignment with star ratings
- Clear monotonic relationship between sentiment score and rating.
- Strong separation between negative and positive reviews.

---

### 2. Improved contextual understanding
- Captures meaning based on full sentence context.
- Handles phrases like “not bad” or “really love this” more effectively than VADER.

---

### 3. More stable predictions
- Less sensitive to individual words.
- Better performance on longer, more descriptive reviews.

---

### 4. Best-performing model so far
- Outperforms:
  - VADER (rule-based sentiment)
  - TF-IDF + Logistic Regression (classical ML)

---

## Key Limitations

- Pretrained on SST-2 (movie reviews), not cosmetics data.
- Can overestimate positivity in marketing-heavy language.
- Limited by 512-token input restriction.
- Requires more compute than previous models.

---

## Key Insight

Transformer-based models significantly improve sentiment understanding by incorporating context rather than relying on isolated words or lexicons.

However, domain mismatch (cosmetics vs movie reviews) still limits performance.

---


# Script 07 — Sentiment Analysis Consolidation

## Overview
This script consolidates three sentiment analysis approaches—VADER, TF-IDF + Logistic Regression, and DistilBERT—into a single dataset for comparison and evaluation.

---

## Data Source
- File: `cheekbonebeauty.com_YOTPO_all_product_reviews.csv`
- Location: `/data/raw/`

---

## Workflow

### 1. Data Loading
- Load review dataset using pandas
- Fill missing review text with empty strings

### 2. VADER Sentiment (Rule-Based)
- Uses NLTK `SentimentIntensityAnalyzer`
- Outputs compound sentiment score (-1 to 1)

### 3. TF-IDF + Logistic Regression (ML Model)
- Loads pre-trained TF-IDF vectorizer and Logistic Regression model
- Predicts review rating class

### 4. DistilBERT Sentiment (Transformer Model)
- Uses Hugging Face `distilbert-base-uncased-finetuned-sst-2-english`
- Converts output into signed sentiment score
- Applied to a 500-review sample for performance

### 5. Feature Consolidation
Final dataset includes:
- review text
- actual rating
- VADER score
- ML predicted class
- BERT score

### 6. Sentiment Labeling
Derived from BERT score:
- ≥ 0.3 → positive
- ≤ -0.3 → negative
- otherwise → neutral

### 7. Evaluation
- Model agreement calculated between TF-IDF predictions and actual ratings
- Error analysis identifies mismatched predictions

---

## Output Columns
- review_description
- rating
- vader_score
- ml_pred_class
- bert_score
- final_sentiment

---

## Key Results
- TF-IDF model agreement: ~87%
- Dataset is heavily skewed toward positive reviews
- Most model disagreements occur in short or ambiguous text

---

## Notes
- BERT inference is computationally expensive; sampling is used
- DistilBERT is binary sentiment (positive/negative), neutral is derived
- TF-IDF model predicts rating class, not direct sentiment

---

# Model Summary for Dashboard Use

This analysis evaluates three different approaches to sentiment analysis, each with different strengths depending on how the results are used in a dashboard or reporting environment.

### VADER (Rule-Based Sentiment)
- Fast and lightweight
- No training required
- Easy to interpret and explain
- Performs well at a high level (clear positive vs negative trends)
- Struggles with domain-specific language and nuanced sentiment

### TF-IDF + Logistic Regression (Classical Machine Learning)
- Uses learned patterns from the dataset
- More interpretable than deep learning models
- Captures domain-specific word importance better than VADER
- Limited by class imbalance and inability to fully capture context

### DistilBERT (Transformer-Based Model)
- Best overall alignment with star ratings
- Captures contextual meaning in full sentences
- Handles nuanced language better than both VADER and TF-IDF
- More computationally expensive and slower to run
- Pretrained on general sentiment data, not cosmetics-specific text

---

## Practical Takeaway for Dashboard

- **VADER** is best suited for real-time or lightweight sentiment tracking in a dashboard.
- **TF-IDF + Logistic Regression** provides a strong, interpretable baseline model for structured analysis.
- **DistilBERT** is the most accurate for understanding true sentiment patterns and can be used for batch analysis or validation.

---

## Overall Insight

All three models show strong agreement with review star ratings at a high level, but differ in how they handle and context. For a production dashboard, a hybrid approach is most practical:

- Use **VADER or TF-IDF models for speed and interpretability**
- Use **DistilBERT for deeper sentiment validation and benchmarking**

This layered approach provides both operational efficiency and analytical depth.