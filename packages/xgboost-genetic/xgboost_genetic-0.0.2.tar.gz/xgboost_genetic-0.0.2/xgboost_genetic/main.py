"""
Módulo principal para execução do pipeline de treinamento e otimização do modelo XGBoost.

Este módulo contém a função `run_pipeline` que executa as etapas de carregamento dos dados, pré-processamento,
divisão dos dados, treinamento inicial do modelo, otimização dos hiperparâmetros usando algoritmos genéticos
e treinamento final do modelo com os melhores hiperparâmetros encontrados.

Também contém a função `predict` que carrega um modelo treinado e faz previsões com novos dados.
"""

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from .data_loader import load_data_from_csv
from .preprocessing import clean_data, split_features_and_target
from .model import train_model
from .genetic_optimizer import optimize_hyperparameters
from .graphics import plot_feature_importance, plot_optimization_results

def run_pipeline(dataset_path, target_column, test_size=0.2, ngen=100, population_size=50):
    """
    Executa o pipeline de treinamento e otimização do modelo XGBoost.

    Este pipeline inclui as etapas de carregamento dos dados, pré-processamento, divisão dos dados,
    treinamento inicial do modelo, otimização dos hiperparâmetros usando algoritmos genéticos e
    treinamento final do modelo com os melhores hiperparâmetros encontrados.

    Parâmetros:
    - dataset_path: str
        Caminho para o arquivo CSV contendo o dataset.
    - target_column: str
        Nome da coluna alvo (variável dependente) no dataset.
    - test_size: float, opcional (default=0.2)
        Proporção dos dados a serem usados como conjunto de teste.
    - ngen: int, opcional (default=100)
        Número de gerações para o algoritmo genético.
    - population_size: int, opcional (default=50)
        Tamanho da população para o algoritmo genético.

    Retorna:
    - None
    """
    # Carregar dados
    df = load_data_from_csv(dataset_path)

    # Pré-processamento
    df_cleaned = clean_data(df)

    # Dividir dados em features e alvo
    X, y = split_features_and_target(df_cleaned, target_column)

    # Dividir dados em treino e teste
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    # Treinar modelo inicial
    initial_params = {
        "n_estimators": 100,
        "learning_rate": 0.1,
        "max_depth": 6,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "gamma": 0,
        "min_child_weight": 1,
        "colsample_bylevel": 1,
        "reg_alpha": 0,
        "reg_lambda": 1,
    }

    # Definir intervalos de parâmetros para otimização
    param_intervals = {
        "n_estimators": (50, 500),
        "learning_rate": (0.01, 0.3),
        "max_depth": (3, 10),
        "subsample": (0.5, 1.0),
        "colsample_bytree": (0.5, 1.0),
        "gamma": (0, 5),
        "min_child_weight": (1, 10),
        "colsample_bylevel": (0.5, 1.0),
        "reg_alpha": (0, 1),
        "reg_lambda": (0, 1),
    }
    model, mse = train_model(x_train, y_train, x_test, y_test, initial_params)
    print(f"Initial MSE: {mse}")

    # Salvar o modelo inicial
    joblib.dump(model, 'model_first_train.pkl')

    # Mostrar as features mais importantes do primeiro treinamento
    plot_feature_importance(model, X.columns, 'feature_importance_first_train.png')

    # Otimizar hiperparâmetros
    optimization_results = optimize_hyperparameters(x_train, y_train, x_test, y_test, param_intervals, ngen=ngen, population_size=population_size)
    best_params = optimization_results['best_params']
    print(f"Best Hyperparameters: {best_params}")

    # Salvar os resultados da otimização
    joblib.dump(optimization_results, 'optimization_results.pkl')

    # Gerar gráfico dos resultados da otimização
    plot_optimization_results(optimization_results['optimization_results'], 'optimization_results.png')

    # Treinar modelo com melhores hiperparâmetros
    model, mse = train_model(x_train, y_train, x_test, y_test, best_params)
    print(f"Optimized MSE: {mse}")

    # Salvar o modelo otimizado
    joblib.dump(model, 'model_best_train.pkl')

def predict(model_path, input_data):
    """
    Carrega um modelo treinado e faz previsões com novos dados.

    Parâmetros:
    - model_path: str
        Caminho para o arquivo do modelo treinado.
    - input_data: DataFrame
        DataFrame contendo os dados de entrada para fazer a previsão.

    Retorna:
    - predictions: Series
        Série contendo as previsões.
    """
    # Carregar o modelo treinado
    model = joblib.load(model_path)

    # Verificar se todos os valores esperados estão presentes nos dados de entrada
    expected_features = model.get_booster().feature_names
    missing_features = set(expected_features) - set(input_data.columns)
    if missing_features:
        raise ValueError(f"Os seguintes valores esperados estão faltando nos dados de entrada: {missing_features}")

    # Fazer a previsão
    predictions = model.predict(input_data)
    return pd.Series(predictions)
