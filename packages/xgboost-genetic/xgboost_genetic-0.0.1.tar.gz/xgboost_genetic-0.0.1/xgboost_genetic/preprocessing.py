import pandas as pd

def clean_data(df):
    """
    Limpa e prepara os dados.
    """
    df = pd.get_dummies(df, drop_first=True)
    df = df.fillna(0)
    return df

def split_features_and_target(df, target_column):
    """
    Divide os dados em features (X) e alvo (y).
    """
    X = df.drop(target_column, axis=1)
    y = df[target_column]
    return X, y
