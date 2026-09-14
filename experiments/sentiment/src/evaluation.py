import pandas as pd


def compute_agreement(df, col1="rating", col2="ml_pred_class"):
    return (df[col1] == df[col2]).mean()


def error_analysis(df, true_col="rating", pred_col="ml_pred_class"):
    return df[df[true_col] != df[pred_col]]