"""
Módulo para carregamento de dados.

Este módulo contém funções para carregar dados de arquivos CSV e de bancos de dados.
"""

import pandas as pd
import psycopg2
from psycopg2 import sql

def load_data_from_csv(file_path):
    """
    Carrega dados de um arquivo CSV.

    Parâmetros:
    - file_path: str
        Caminho para o arquivo CSV.

    Retorna:
    - DataFrame
        DataFrame contendo os dados carregados do arquivo CSV.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.") from exc
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"O arquivo {file_path} está vazio.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(f"Erro ao analisar o arquivo CSV: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Erro ao carregar o arquivo CSV: {exc}") from exc

def load_data_from_db(connection_string, query):
    """
    Carrega dados de um banco de dados.

    Parâmetros:
    - connection_string: str
        String de conexão para o banco de dados.
    - query: str
        Consulta SQL para extrair os dados.

    Retorna:
    - DataFrame
        DataFrame contendo os dados carregados do banco de dados.
    """
    try:
        conn = psycopg2.connect(connection_string)
        df = pd.read_sql_query(sql.SQL(query), conn)
        conn.close()
        return df
    except psycopg2.OperationalError as exc:
        raise psycopg2.OperationalError(f"Erro ao conectar ao banco de dados: {exc}") from exc
    except psycopg2.ProgrammingError as exc:
        raise psycopg2.ProgrammingError(f"Erro na consulta SQL: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Erro ao executar a consulta SQL: {exc}") from exc
