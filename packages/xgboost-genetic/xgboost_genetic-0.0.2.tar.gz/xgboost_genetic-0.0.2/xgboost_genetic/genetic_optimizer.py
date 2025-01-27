"""
Módulo para otimização de hiperparâmetros do modelo XGBoost usando algoritmos genéticos.

Este módulo contém funções para gerar indivíduos (conjuntos de hiperparâmetros),
    avaliar esses indivíduos
treinando o modelo e calculando o erro quadrático médio (MSE), reparar indivíduos para
    garantir que os valores
estejam dentro dos intervalos permitidos, e otimizar os hiperparâmetros do modelo
    usando algoritmos genéticos.
"""

#pylint: disable=all

import random
import numpy as np
from deap import base, creator, tools, algorithms
from .model import train_model

def generate_individual(intervals):
    """
    Gera um indivíduo (conjunto de hiperparâmetros) para a população inicial.

    Parâmetros:
    - intervals: list of tuples
        Lista de intervalos para cada hiperparâmetro.

    Retorna:
    - individual: list
        Lista de valores de hiperparâmetros gerados aleatoriamente dentro dos intervalos fornecidos.
    """
    return [random.uniform(interval[0], interval[1]) if isinstance(interval[0], float) else random.randint(interval[0], interval[1]) for interval in intervals]

def evaluate(individual, x_train, y_train, x_test, y_test):
    """
    Avalia um indivíduo (conjunto de hiperparâmetros) treinando o modelo e calculando o MSE.

    Parâmetros:
    - individual: list
        Lista de valores de hiperparâmetros.
    - x_train: DataFrame
        Conjunto de features de treino.
    - y_train: Series
        Conjunto de labels de treino.
    - x_test: DataFrame
        Conjunto de features de teste.
    - y_test: Series
        Conjunto de labels de teste.

    Retorna:
    - mse: tuple
        Erro quadrático médio (MSE) do modelo treinado com os hiperparâmetros fornecidos.
    """
    params = {
        "n_estimators": int(individual[0]),
        "learning_rate": float(individual[1]),
        "max_depth": int(individual[2]),
        "subsample": float(individual[3]),
        "colsample_bytree": float(individual[4]),
        "gamma": float(individual[5]),
        "min_child_weight": int(individual[6]),
        "colsample_bylevel": float(individual[7]),
        "reg_alpha": float(individual[8]),
        "reg_lambda": float(individual[9]),
    }
    _, mse = train_model(x_train, y_train, x_test, y_test, params)
    return (mse,)

def repair_individual(individual, param_intervals):
    """
    Repara um indivíduo (conjunto de hiperparâmetros) para garantir que os valores estejam
        dentro dos intervalos permitidos.

    Parâmetros:
    - individual: list
        Lista de valores de hiperparâmetros.
    - param_intervals: dict
        Dicionário de intervalos permitidos para cada hiperparâmetro.

    Retorna:
    - individual: list
        Lista de valores de hiperparâmetros reparados.
    """
    for i, (_, interval) in enumerate(param_intervals.items()):
        if individual[i] < interval[0]:
            individual[i] = interval[0]
        elif individual[i] > interval[1]:
            individual[i] = interval[1]
    return individual

def optimize_hyperparameters(x_train, y_train, x_test, y_test, param_intervals, ngen=100, population_size=50):
    """
    Otimiza os hiperparâmetros do modelo XGBoost usando algoritmos genéticos.

    Parâmetros:
    - x_train: DataFrame
        Conjunto de features de treino.
    - y_train: Series
        Conjunto de labels de treino.
    - x_test: DataFrame
        Conjunto de features de teste.
    - y_test: Series
        Conjunto de labels de teste.
    - param_intervals: dict
        Dicionário de intervalos permitidos para cada hiperparâmetro.
    - ngen: int, opcional (default=100)
        Número de gerações para o algoritmo genético.
    - population_size: int, opcional (default=50)
        Tamanho da população para o algoritmo genético.

    Retorna:
    - dict
        Dicionário contendo os melhores hiperparâmetros encontrados e os resultados da otimização.
    """
    toolbox = base.Toolbox()
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin) # type: ignore
    toolbox.register("Genes", generate_individual, intervals=list(param_intervals.values()))
    toolbox.register("Individual", tools.initIterate, creator.Individual, toolbox.Genes)# type: ignore
    toolbox.register("Population", tools.initRepeat, list, toolbox.Individual)# type: ignore
    toolbox.register("repair", repair_individual, param_intervals=param_intervals)
    toolbox.register("mate", tools.cxUniform, indpb=0.5)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.2, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate, x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test)
    population = toolbox.Population(n=population_size)# type: ignore
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
    stats.register("mean", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)

    optimization_results = []

    for gen in range(ngen):
        population, logbook = algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.2, ngen=1, stats=stats, halloffame=hof, verbose=True)
        for ind in population:
            optimization_results.append({
                'generation': gen,
                'params': ind,
                'fitness': ind.fitness.values[0]
            })

    best_individual = hof[0]
    best_params = {
        "n_estimators": int(best_individual[0]),
        "learning_rate": float(best_individual[1]),
        "max_depth": int(best_individual[2]),
        "subsample": float(best_individual[3]),
        "colsample_bytree": float(best_individual[4]),
        "gamma": float(best_individual[5]),
        "min_child_weight": int(best_individual[6]),
        "colsample_bylevel": float(best_individual[7]),
        "reg_alpha": float(best_individual[8]),
        "reg_lambda": float(best_individual[9]),
    }
    return {'best_params': best_params, 'optimization_results': optimization_results}
