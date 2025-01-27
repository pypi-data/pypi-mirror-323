"""
Módulo para treinamento do modelo XGBoost.

Este módulo contém a função `train_model` que treina um modelo XGBoost com os parâmetros fornecidos
e calcula o erro quadrático médio (MSE) no conjunto de teste.
"""

import xgboost as xgb
from sklearn.metrics import mean_squared_error

def train_model(x_train, y_train, x_test, y_test, params):
    """
    Treina o modelo XGBoost com os parâmetros fornecidos.

    Parâmetros:
    - x_train: DataFrame
        Conjunto de features de treino.
    - y_train: Series
        Conjunto de labels de treino.
    - x_test: DataFrame
        Conjunto de features de teste.
    - y_test: Series
        Conjunto de labels de teste.
    - params: dict
        Dicionário contendo os hiperparâmetros do modelo XGBoost.

    Retorna:
    - model: XGBRegressor
        Modelo XGBoost treinado.
    - mse: float
        Erro quadrático médio (MSE) no conjunto de teste.
    """
    model = xgb.XGBRegressor(**params)
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    mse = mean_squared_error(y_test, y_pred)
    return model, mse
