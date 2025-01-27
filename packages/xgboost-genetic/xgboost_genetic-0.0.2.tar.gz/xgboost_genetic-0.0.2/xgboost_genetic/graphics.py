"""
Módulo para geração de gráficos.

Este módulo contém funções para gerar e salvar gráficos de importância das features e dos resultados
da otimização dos hiperparâmetros.
"""

import matplotlib.pyplot as plt
import numpy as np

def plot_feature_importance(model, feature_names, output_path):
    """
    Gera e salva um gráfico de importância das features.

    Parâmetros:
    - model: XGBRegressor
        Modelo XGBoost treinado.
    - feature_names: list
        Lista com os nomes das features.
    - output_path: str
        Caminho para salvar o gráfico gerado.

    Retorna:
    - None
    """
    importance = model.feature_importances_
    indices = np.argsort(importance)[::-1]

    plt.figure(figsize=(10, 6))
    plt.title("Importância das Features")
    plt.bar(range(len(feature_names)), importance[indices], align="center")
    plt.xticks(range(len(feature_names)), [feature_names[i] for i in indices], rotation=90)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()  # Fecha a figura para liberar memória

def plot_optimization_results(optimization_results, output_path):
    """
    Gera e salva um gráfico dos resultados da otimização dos hiperparâmetros.

    Parâmetros:
    - optimization_results: list of dict
        Lista de dicionários contendo os parâmetros usados e seus respectivos resultados.
    - output_path: str
        Caminho para salvar o gráfico gerado.

    Retorna:
    - None
    """
    generations = [result['generation'] for result in optimization_results]
    fitness_values = [result['fitness'] for result in optimization_results]

    plt.figure(figsize=(10, 6))
    plt.plot(generations, fitness_values, marker='o')
    plt.title("Resultados da Otimização dos Hiperparâmetros")
    plt.xlabel("Geração")
    plt.ylabel("Fitness (MSE)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()  # Fecha a figura para liberar memória
