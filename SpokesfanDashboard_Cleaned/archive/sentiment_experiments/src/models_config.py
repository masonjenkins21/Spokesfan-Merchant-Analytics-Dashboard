"""
Transformer models used for merchant sentiment analysis experiments.

Each model will be evaluated across merchant datasets
to determine which provides the strongest business value.
"""


TRANSFORMER_MODELS = {

    "distilbert": {
        "name": "distilbert-base-uncased-finetuned-sst-2-english",
        "description": "Lightweight BERT-based sentiment classifier"
    },


    "roberta": {
        "name": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "description": "RoBERTa sentiment classifier trained on social media text"
    },


    "bertweet": {
        "name": "finiteautomata/bertweet-base-sentiment-analysis",
        "description": "BERTweet model fine-tuned for sentiment classification"
    },
}