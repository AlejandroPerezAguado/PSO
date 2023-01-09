# IMPORTS #
import matplotlib.pyplot as plt
import numpy as np
import multiprocessing as mp
import random as rd
import time

# PARÁMETROS GLOBALES #
nParticulas = int(100) # Número de partículas
iteraciones = int(500) # Número de iteraciones
t_mutacion = float(0.2) # Tasa de mutación
current_time_milis = time.time_ns() # Tiempo actual para la semilla aleatoria

# PARÁMETROS PARTÍCULAS #
n = int(10) # Tamaño de fila del problema
tam = pow(n, 2) # Número de celdas totales

# PARÁMETROS PSO #
c1 = float(3.5) # Constante Aceleración Individual
c2 = float(0.5) # Constante Aceleración Colectiva
# c1 + c2 <= 4
r1 = float(0.8) # Random Memoria Individual
r2 = float(0.2) # Random Memoria Colectiva
w = float(0.2) # Inercia: Alto = Exploración/Global; Bajo = Explotación/Individual
const = int(5) # Valor de NLU - Recomendado 10

# PARÁMETROS VECINDARIO #
regiones = int(4) # Número de regiones
vecinos = nParticulas/regiones # Número de vecinos por región

# FUNCIÓN DE DESPLAZAMIENTO #
fit = int(2) # 1: Desplazamiento Básico; 2: Desplazamiento Nuevo
vCambio = float(0.4) # Valor de Probabilidad de Cambio de Desplazamiento 2: < vCambio = Explotación/Individual; >= vCambio = Exploración/Global
vMantener = float(0.05) # Probabilidad de que no cambie

# METODOS #
#Función fitness del problema
def fitness(I, LU, P):
    NLU = NP = V = 0
    for i in range(tam):
        if (I[i] == 0):
            V = V + 0.5
    for i in range(tam):
        NLU = NLU + LU[i]*I[i]
        NP = NP + P[i]*V
    return NLU*const + NP

# DESPLAZAMIENTO 1: Función para actualizar la velocidad de un bit
def actualizarVelocidad(i, v, pBestI, gBestI):
    Inercia = w*v
    MemIndividual = c1*r1*(pBestI-i)
    MemColectiva = c2*r2*(gBestI-i)
    return ((3 + Inercia + MemIndividual + MemColectiva) % 3) - 1

# Función para actualizar la posición de un bit
def actualizarPosicion(i, v):
    new_i = i + v
    return (4 + new_i) % 2

# DESPALAZAMIENTO 2: Nueva función de desplazamiento basada en probabilidades
def nuevoDesplazamiento(i, pBestI, gBestI):
    if (rd.random() < vMantener):
        return i
    else:
        if (rd.random() < vCambio):
            return pBestI
        else:
            return gBestI

# Función para mutar un bit
def mutacion(i):
    if (i == 1):
        return 0
    else:
        return 1
    
# Permuta todos los bits de un individuo
def permutacion(ind):
    for i in range(tam):
        if (ind[i] == 0):
            ind[i] = 1
        else:
            ind[i] = 0
    return ind
        
# CLASES #
class Particula:
    def __init__(self):
        self.I = np.empty(tam, dtype=int) # Existencia de antena (1) o no (0)
        for i in range(tam):
            self.I[i] = rd.randint(0, 1)
        self.V = np.empty(tam, dtype=int) # Velocidad de la celda
        for j in range(tam):
            self.V[j] = rd.randint(-1, 1)
        self.pBestF = 0 # Mejor fitness individual
        self.pBest = [] # Mejor particula individual
    
    def actualizarMejorIndividual(self, I, fitness):
        self.pBestF = fitness
        self.pBest = I
            
    def mostrarParticula(self):
        print(self.I)
        
    def mostrarVelocidades(self):
        print(self.V)
        
class Datos:
    def __init__(self):
        self.LU = np.empty(tam, dtype=int) # Número de actualizaciones de localización
        self.P = np.empty(tam, dtype=int) # Número de búsquedas de usuario
        
        archivo = open('Instancia10x10.csv', 'r')
        for linea in archivo:
            x = linea.split(";")
            self.LU[int(x[0])-1] = int(x[1])
            self.P[int(x[0])-1] = int(x[2])
        archivo.close()

##### MAIN #####
def main():
    # SEMILLA ALEATORIA #
    rd.seed(current_time_milis)
    
    # LECTURA DEL FICHERO DE INSTANCIA #
    Ins = Datos()
    
    # FICHERO DE ESCRITURA DE MEJORES INDIVIDUOS #
    resultado = open('Prueba.csv', 'w')
    resultado.write("Semilla Aleatoria: " + str(current_time_milis) + "\n")
    resultado.write("Vecindario1;Vecindario2;Vecindario3;Vecindario4" + "\n")
    
    # GENERACIÓN DE LA POBLACIÓN #
    Poblacion = []
    for i in range(nParticulas):
        Poblacion.append(Particula())
    
    ### ALGORITMO PSO ###
    gBestF = [0, 0, 0, 0] # Mejor fitness global
    gBest = [[], [], [], []] # Mejor particula global
    v = 0 # índice del vecindario
    for i in range(iteraciones):
        print("Iteracción: " + str(i+1))
        
        # FASE ACTUALIZACION MEJORES FITNESS #
        for j in range(nParticulas):
            # SELECCIONAR VECINDARIO
            if (j >= 0 and j < 25):
                v = 0
            elif (j > 24 and j < 50):
                v = 1
            elif (j > 49 and j < 75):
                v = 2
            else:
                v = 3
            # EVALUAR FITNESS PARTICULA #
            new_fitness = fitness(Poblacion[j].I, Ins.LU, Ins.P)
            # ACTUALIZAR MEJOR GLOBAL #
            if ((i == 0 and (j == 0 or j == 25 or j == 50 or j == 75)) or new_fitness < gBestF[v]):
                print("MEJORADO GLOBALMENTE GG")
                gBestF[v] = new_fitness
                gBest[v] = Poblacion[j].I
                # COMPARAR MEJORES DE CADA VECINDARIO #
                for k in range(regiones):
                    if (k != v):
                        if (gBestF[v] == gBestF[k]):
                            print("PERMUTACION")
                            gBest[v] = permutacion(gBest[v])
                            gBestF[v] = fitness(gBest[v], Ins.LU, Ins.P)
                            
            # ACTUALIZAR MEJOR INDIVIDUAL #
            if (i == 0 or new_fitness < Poblacion[j].pBestF):
                print("Mejorado Individualmente " + str(j+1))
                Poblacion[j].actualizarMejorIndividual(Poblacion[j].I, new_fitness)
        
        # ESCRIBIR MEJOR DE ESTA ITERACIÓN #
        for i in range(regiones):
            resultado.write(str(gBestF[i]) + ";")
        resultado.write("\n")
        
        # FASE CAMBIOS DE VELOCIDAD Y POSICION #        
        for k in range(nParticulas):
            # SELECCIONAR VECINDARIO
            if (j >= 0 and j < 25):
                v = 0
            elif (j > 24 and j < 50):
                v = 1
            elif (j > 49 and j < 75):
                v = 2
            else:
                v = 3
            for l in range(tam):
                if (fit == 1):
                    Poblacion[k].V[l] = actualizarVelocidad(Poblacion[k].I[l], Poblacion[k].V[l], Poblacion[k].pBest[l], gBest[v][l])
                    Poblacion[k].I[l] = actualizarPosicion(Poblacion[k].I[l], Poblacion[k].V[l])
                else:
                    Poblacion[k].I[l] = nuevoDesplazamiento(Poblacion[k].I[l], Poblacion[k].pBest[l], gBest[v][l])
                    
                # FASE DE MUTACIÓN #
                if (rd.random() < t_mutacion):
                    Poblacion[k].I[l] = mutacion(Poblacion[k].I[l])
                
    resultado.close()
    return 0
main()