"""
Módulo utilitário para salvar resultados.

Este módulo contém uma função para salvar resultados em um arquivo CSV.
"""

import pandas as pd

def save_results(results, file_path):
    """
    Salva os resultados em um arquivo CSV.

    Parâmetros:
    - results: list of dict
        Lista de dicionários contendo os resultados a serem salvos.
    - file_path: str
        Caminho para o arquivo CSV onde os resultados serão salvos.

    Retorna:
    - None
    """
    df = pd.DataFrame(results)
    df.to_csv(file_path, index=False)
