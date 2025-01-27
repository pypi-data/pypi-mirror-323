"""
Script de configuração para a biblioteca xgboost_genetic.

Este script lê as dependências do arquivo requirements.txt e configura a distribuição do pacote.
"""

from setuptools import setup, find_packages

def parse_requirements(filename):
    """
    Lê o arquivo requirements.txt e retorna uma lista de dependências.

    Parâmetros:
    - filename: str
        Caminho para o arquivo requirements.txt.

    Retorna:
    - list of str
        Lista de dependências.
    """
    with open(filename, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip() and not line.startswith('#')]

setup(
    name='xgboost_genetic',
    version='0.0.1',
    description='Biblioteca para otimização de hiperparâmetros do XGBoost usando algoritmos genéticos.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Paulo Do Monte',
    author_email='paulo.monte.fis@gmail.com',
    url='https://github.com/PauloDoMonte/xgboost_genetic',
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
