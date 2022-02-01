from ast import Str
import numpy as np
import re
from datetime import datetime
import pandas as pd
from collections import Counter
import scipy.stats as etd


class Caracter:
    def __init__(self, valores) -> None:
        self.__valores = np.array(valores)
        self.__n = len(self.__valores)    

    def __reemplazar(self, cadena:str) -> Str:
        cadena = re.sub(r"Á", "A", cadena)
        cadena = re.sub(r"É", "E", cadena)
        cadena = re.sub(r"Í", "I", cadena)
        cadena = re.sub(r"Ó", "O", cadena)
        cadena = re.sub(r"Ú", "U", cadena)
        return cadena

    def __levenshtein_ratio_and_distance(self, s, t, ratio_calc = True):
        # Initialize matrix of zeros
        rows = len(s)+1
        cols = len(t)+1
        distance = np.zeros((rows,cols),dtype = int)
        # Populate matrix of zeros with the indeces of each character of both strings
        for i in range(1, rows):
            for k in range(1,cols):
                distance[i][0] = i
                distance[0][k] = k
        # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions    
        for col in range(1, cols):
            for row in range(1, rows):
                if s[row-1] == t[col-1]:
                    cost = 0 
                else:
                    if ratio_calc == True:
                        cost = 2
                    else:
                        cost = 1
                distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                    distance[row][col-1] + 1,          # Cost of insertions
                                    distance[row-1][col-1] + cost)     # Cost of substitutions
        if ratio_calc == True:
            # Computation of the Levenshtein Distance Ratio
            Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
            return Ratio
        else:
            return "The strings are {} edits away".format(distance[row][col])
    
    def evaluacion_exactitud(self, numeros=False, letras=True, longitud=None) -> str:
        # Normalizar valores
        valores = np.array(list(filter(lambda x: str(x) not in ['nan', 'NAN'], self.__valores)))
        n = len(valores)
        # Buscar reglas
        lista_reglas = []
        patron = re.compile("[\!|\$|\%|\^|\&|\*|\(|\)|\[|\]|\{|\}|;|:|,|\/|<|>|?|\|\`|\~|=|\_|\+]")
        lista_reglas.append(n - sum(map(lambda x: 1 if re.search(patron, str(x)) else 0, valores)))
        if not numeros:
            patron = re.compile("[0-9]")
            lista_reglas.append(n - sum(map(lambda x: 1 if re.search(patron, str(x)) else 0, valores)))
        if not letras:
            patron = re.compile("[A-Za-z]")
            lista_reglas.append(n - sum(map(lambda x: 1 if re.search(patron, str(x)) else 0, valores)))
        if longitud is not None:
            lista_reglas.append(n - sum(map(lambda x: 1 if len(str(x))<longitud  else 0, valores)))
        # Calcular porcentaje de exactitud
        if not numeros and letras:
            exactitud = (lista_reglas[0] / n) * 0.4 + (lista_reglas[1] / n) * 0.4 + (lista_reglas[2] / n) * 0.2
        elif not letras and numeros:
            exactitud = (lista_reglas[1] / n) * 0.4 + (lista_reglas[0] / n) * 0.4 + (lista_reglas[2] / n) * 0.2
        else:
            exactitud = (lista_reglas[0] / n) * 0.8 + (lista_reglas[1] / n) * 0.2
        return f'El porcentaje de exactitud para la variable es de {round(exactitud * 100, 2)}%'

    def evaluacion_actualidad(self, fecha_actualizacion:pd.Series, tiempo_vigencia:tuple) -> str:
        # Calcula el tiempo de vigencia real del campo
        fecha_actualizacion = np.array(fecha_actualizacion)
        hoy = np.datetime64(datetime.now().date())
        diferencia_fechas = hoy - fecha_actualizacion
        if tiempo_vigencia[1] == "dias":
            diferencia_fechas = diferencia_fechas.astype('timedelta64[D]')
        elif tiempo_vigencia[1] == "meses":
            diferencia_fechas = diferencia_fechas.astype('timedelta64[M]')
        else:
            diferencia_fechas = diferencia_fechas.astype('timedelta64[Y]')
        # Calcular quienes ya pasaron el tiempo de vigencia
        pasaron_vigencia = sum(np.array(list(map(lambda x: int(x), diferencia_fechas))) > tiempo_vigencia[0])
        # Calcular porcentaje de actualidad
        actualidad = (self.__n - pasaron_vigencia) / self.__n
        return f'El porcentaje de actualidad para la variable es de {round(actualidad * 100, 2)}%'

    def evaluacion_completitud(self) -> str:
        # Contar el totol de valores nulos
        total_nulos = sum(pd.Series(self.__valores).isnull())
        # Calcular porcentaje de completitud
        completitud = (self.__n - total_nulos) / self.__n
        return  f'El porcentaje de completitud para la variable es de {round(completitud * 100, 2)}%'
    
    def evaluacion_accesibilidad(self, acceso:int, plantilla:int,\
        presentacion:int, restriccion:int) -> str:
        # Calcular porcentaje de accesibilidad
        accesibilidad = 0.6*plantilla + 0.2*presentacion + 0.1*presentacion + 0.1*(1-restriccion)
        return f'El porcentaje de accesibilidad para la variable es de {round(accesibilidad * 100, 2)}%'

    def evaluacion_consistencia(self, estandar:str, diccionario_dominios=None,\
         tildes = False, numeros = True, mayusculas = True, minusculas = False,\
              categorias_teoricas=None, letras=True) -> str:
        # Normalizar cadenas
        valores = np.array(list(filter(lambda x: str(x) not in ['nan', 'NAN'], self.__valores)))
        n = len(valores)
        patron = re.compile("[\!|\$|\%|\^|\&|\*|\[|\]|\{|\}|;|:|,|\.|\/|<|>|?|\|\`|~|=|\_]")
        valores = list(map(lambda x: re.sub(patron, " ", x), valores))
        # Calcular las reglas simples
        lista_reglas = []
        if numeros and letras:
            if not tildes:
                patron = re.compile("\Á|\É|\Í|\Ó|\Ú|\á|é|í|ó|ú")
                lista_reglas.append(n - sum(map(lambda x: 1 if re.search(patron, x) else 0, valores)))
            if not mayusculas:
                patron = re.compile("[A-Z]")
                lista_reglas.append(n - sum(map(lambda x: 1 if re.search(patron, x) else 0, valores)))
            if not minusculas:
                patron = re.compile("[a-z]")
                lista_reglas.append(n - sum(map(lambda x: 1 if re.search(patron, x) else 0, valores)))
        # estructurar formato
        valores = list(map(lambda x: x.upper(), valores))
        # Asignar token a un dominio
        valores_similitud = []
        categorias = []
        listas = list(map(lambda x: x.strip().split(" "), valores))
        for j in listas:
            valores_similitud = []
            for i in j:
                if i != '':
                    valores_similitud.append(list(map(lambda x: (self.__levenshtein_ratio_and_distance(i,\
                        str(x)), x), categorias_teoricas))) 
            cadena = ""
            for idx, valor in enumerate(valores_similitud):
                similutud =  max(dict(valores_similitud[idx]).keys())
                llave = dict(valores_similitud[idx])[similutud] if similutud > 0 else 'none'
                cadena += ' '+diccionario_dominios[llave] 
                cadena = cadena.strip()
            categorias.append(cadena)
        similitud = []
        for idx,i in enumerate(categorias):
            if i != "":
                similitud.append(self.__levenshtein_ratio_and_distance(str(i), estandar))
        # Calcular porcentaje de consistencia
        if numeros and letras:
            if not tildes and numeros:
                consistencia =  0.2 * ( 0.5*(lista_reglas[0]/n) + 0.5*(lista_reglas[1]/n) ) + 0.8 * (sum(similitud)/n)
            elif tildes  and numeros:
                consistencia =  0.2*(lista_reglas[0]/n)  + 0.8*(sum(similitud)/n)
            elif not tildes and not numeros:
                consistencia = 0.3 * ( 0.33*(lista_reglas[0]/n) + 0.33*(lista_reglas[1]/n) + \
                    0.33*(lista_reglas[2]/n) ) + 0.7 * (sum(similitud)/n) 
            elif tildes and not numeros:
                consistencia =  0.2 * ( 0.5*(lista_reglas[0]/n) + 0.5*(lista_reglas[1]/n) ) + 0.8 * (sum(similitud)/n)
        else:
            if not letras and numeros:
                consistencia =  sum(similitud)/n
        return f'El porcentaje de consistencia para la variable es de {round(consistencia * 100, 2)}%'

    
