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
c1 = float(4.0) # Constante Aceleración Individual
c2 = float(0.0) # Constante Aceleración Colectiva
# c1 + c2 <= 4
r1 = float(1.0) # Random Memoria Individual
r2 = float(0.0) # Random Memoria Colectiva
w = float(1) # Inercia: Alto = Exploración/Global; Bajo = Explotación/Individual
const = int(5) # Valor de NLU - Recomendado 10

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
    contador = int(0)
    xplr_again = False
    aux = 0
    aux2 = 0
    t_mutacion = float(0.2)

    # SEMILLA ALEATORIA #
    rd.seed(current_time_milis)
    
    # LECTURA DEL FICHERO DE INSTANCIA #
    Ins = Datos()
    
    # FICHERO DE ESCRITURA DE MEJORES INDIVIDUOS #
    resultado = open('Prueba.csv', 'w')
    resultado.write("Semilla Aleatoria: " + str(current_time_milis) + "\n")
    
    # GENERACIÓN DE LA POBLACIÓN #
    Poblacion = []
    for i in range(nParticulas):
        Poblacion.append(Particula())
    
    ### ALGORITMO PSO ###
    gBestF = 0 # Mejor fitness global
    gBest = [] # Mejor particula global
    for i in range(iteraciones):
        mejorado = False

        if (contador >= 300):
            if (contador==300):
                aux = iteraciones-i
                aux2 = 0
            xplr_again = True
        
        if xplr_again:
            c1 = float(4.0 * ((aux-aux2)/aux))
            c2 = float(4.0 * (1 - ((aux-aux2)/aux)))
            r1 = float(1.0 * ((aux-aux2)/aux))
            r2 = float(1.0 * (1 - ((aux-aux2)/aux)))
            w = float(1 - ((i+1)/100))
            t_mutacion = float(0.4)
            aux2 += 1
        else:
            c1 = float(4.0 * ((iteraciones-i)/iteraciones))
            c2 = float(4.0 * (1 - ((iteraciones-i)/iteraciones)))
            r1 = float(1.0 * ((iteraciones-i)/iteraciones))
            r2 = float(1.0 * (1 - ((iteraciones-i)/iteraciones)))
            w = float(1 - ((i+1)/iteraciones))


        print("Iteracción: " + str(i+1))
        
        # FASE ACTUALIZACION MEJORES FITNESS #
        for j in range(nParticulas):
            # EVALUAR FITNESS PARTICULA #
            new_fitness = fitness(Poblacion[j].I, Ins.LU, Ins.P)
            # ACTUALIZAR MEJOR GLOBAL #
            if ((i == 0 and j == 0) or new_fitness < gBestF):
                print("MEJORADO GLOBALMENTE GG")
                gBestF = new_fitness
                gBest = Poblacion[j].I
                mejorado = True
                contador = 0
            # ACTUALIZAR MEJOR INDIVIDUAL #
            if (i == 0 or new_fitness < Poblacion[j].pBestF):
                print("Mejorado Individualmente " + str(j+1))
                Poblacion[j].actualizarMejorIndividual(Poblacion[j].I, new_fitness)
        
        # ESCRIBIR MEJOR DE ESTA ITERACIÓN #
        resultado.write(str(gBestF) + "\n")
        
        # FASE CAMBIOS DE VELOCIDAD Y POSICION #        
        for k in range(nParticulas):
            for l in range(tam):
                if (fit == 1):
                    Poblacion[k].V[l] = actualizarVelocidad(Poblacion[k].I[l], Poblacion[k].V[l], Poblacion[k].pBest[l], gBest[l])
                    Poblacion[k].I[l] = actualizarPosicion(Poblacion[k].I[l], Poblacion[k].V[l])
                else:
                    Poblacion[k].I[l] = nuevoDesplazamiento(Poblacion[k].I[l], Poblacion[k].pBest[l], gBest[l])
                    
                # FASE DE MUTACIÓN #
                if (rd.random() < t_mutacion):
                    Poblacion[k].I[l] = mutacion(Poblacion[k].I[l])
        
        if(not mejorado):
            contador +=1
                
    resultado.close()
    return 0
main()