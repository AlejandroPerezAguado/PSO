# https://pypi.org/project/geneticalgorithm/
import numpy as np
import time
from geneticalgorithm import geneticalgorithm as ga

n = int(20) # Tamaño de fila del problema
tam = pow(n, 2) # Número de celdas totales

LU = np.empty(tam, dtype=int) # Número de actualizaciones de localización
P = np.empty(tam, dtype=int) # Número de búsquedas de usuario

#Función fitness del problema
const = int(5) # Valor de NLU - Recomendado 10
def fitness(I):
    NLU = NP = V = 0
    for i in range(tam):
        if (I[i] == 0):
            V = V + 0.5
    for i in range(tam):
        NLU = NLU + LU[i]*I[i]
        NP = NP + P[i]*V
    return NLU*const + NP

# MAIN #
inicio = time.time()
archivo = open('Instancia20x20.csv', 'r')
for linea in archivo:
    x = linea.split(";")
    LU[int(x[0])-1] = int(x[1])
    P[int(x[0])-1] = int(x[2])      
archivo.close()
varbound = np.array([[0, 1]]*tam)

# Algoritmo Genético #
algorithm_param = {'max_num_iteration': 1000,\
                   'population_size': 100,\
                   'mutation_probability': 0.2,\
                   'elit_ratio': 0.01,\
                   'crossover_probability': 0.5,\
                   'parents_portion': 0.3,\
                   'crossover_type': 'uniform',\
                   'max_iteration_without_improv': None}

model = ga(function=fitness, dimension=tam, variable_type='int', variable_boundaries=varbound, algorithm_parameters=algorithm_param)

model.run()
convergence = model.report
fin = time.time()
print(fin-inicio)