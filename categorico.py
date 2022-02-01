from ast import Str
import numpy as np
import re
from datetime import datetime
import pandas as pd
from collections import Counter
import scipy.stats as etd


class Categorica:
    def __init__(self, valores) -> None:
        self.__valores = np.array(valores)
        self.__n = len(self.__valores)    

    def __reemplazar(self, cadena:str) -> Str:
        cadena = re.sub(r"Á", "A", cadena)
        cadena = re.sub(r"É", "E", cadena)
        cadena = re.sub(r"Í", "I", cadena)
        cadena = re.sub(r"Ó", "O", cadena)
        cadena = re.sub(r"Ú", "U", cadena)
        cadena.replace("!@#$%^&*()[]{};:,./<>?\|`~-=_+", "")
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
    
    def evaluacion_exactitud(self, distribucion_teorica:list, categorias_teoricas:tuple, suma_reglas=None) -> str:
        # Normalizar valores
        valores = np.array(list(filter(lambda x: str(x)!='nan', self.__valores)))
        n = len(valores)
        valores = list(map(lambda x: self.__reemplazar(str(x).upper().strip()),\
             valores))
        # Calcular la similitud para cada observación
        valores_similitud = []
        for i in valores:
            valores_similitud.append(list(map(lambda x: (self.__levenshtein_ratio_and_distance(i, x), x), categorias_teoricas))) 
        similitud = []
        categorias = []
        for idx, valor in enumerate(valores_similitud):
            categorias.append(dict(valores_similitud[idx])[max(dict(valores_similitud[idx]).keys())])
            similitud.append(max(dict(valores_similitud[idx]).keys()))
        # Contruir los conteos observados
        c = Counter(sorted(categorias))
        c = dict(c)
        valores_observados = list(c.values())
        # Construir la distribución teorica
        distribucion_teorica_aux1 = np.array(distribucion_teorica) / 10
        distribucion_teorica_aux2 = np.sum(distribucion_teorica_aux1)
        distribucion_teorica_aux3 = distribucion_teorica_aux1 / distribucion_teorica_aux2
        distribucion_teorica_aux3 = distribucion_teorica_aux3 * n
        distribucion_teorica_aux3 = np.array(list(map(lambda x: np.ceil(x), distribucion_teorica_aux3)))
        distribucion_teorica_aux3 = distribucion_teorica_aux3.astype(int)
        diferencia = sum(distribucion_teorica_aux3) - sum(valores_observados)
        distribucion_teorica_aux3[0] = distribucion_teorica_aux3[0] - diferencia
        # Calculo test chi cuadrado
        vp_chi = etd.chisquare(valores_observados, distribucion_teorica_aux3)[1]
        if vp_chi < 0.05:
            resultado_test = "diferentes"
        else:
            resultado_test = "similares"
        # Calcular porcentaje de exactitud
        if suma_reglas:
            if resultado_test == "similares":
                exactitud = 0.3 + suma_reglas * 0.5 + (sum(similitud)/n) * 0.2
            else:
                exactitud = suma_reglas * 0.5 + (sum(similitud)/n) * 0.2
        else:
            exactitud = ((vp_chi) * 0.7) + ((sum(similitud)/n) * 0.3)
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

    def evaluacion_consistencia(self, caracteres_especiales=False, mayusculas=True, minusculas=False,\
         espacio = False, tildes = False) -> str:
        valores = np.array(list(filter(lambda x: str(x)!='nan', self.__valores)))
        n = len(valores)
        lista_reglas = []
        if not caracteres_especiales:
            patron = re.compile("[\!|\@|\#|\$|\%|\^|\&|\*|\(|\)|\[|\]|\{|\}|;|:|,|\/|<|>|?|\|\`|~|-|=|\_|\+]")
            lista_reglas.append(n - sum(map(lambda x: 1 if re.search(patron, x) else 0, valores)))
        if not mayusculas:
            patron = re.compile("[A-Z]")
            lista_reglas.append(n - sum(map(lambda x: 1 if re.search(patron, x) else 0, valores)))
        if not minusculas:
            patron = re.compile("[a-z]")
            lista_reglas.append(n - sum(map(lambda x: 1 if re.search(patron, x) else 0, valores)))
        if not espacio:
            patron = re.compile("\s")
            lista_reglas.append(n - sum(map(lambda x: 1 if re.search(patron, x) else 0, valores)))
        if not tildes:
            patron = re.compile("\Á|\É|\Í|\Ó|\Ú|\á|é|í|ó|ú")
            lista_reglas.append(n - sum(map(lambda x: 1 if re.search(patron, x) else 0, valores)))
        # Calcular porcentaje de consistencia
        if True:
            if not tildes and not espacio and not minusculas and not caracteres_especiales:
                consistencia = 0.25 * (lista_reglas[0]/n) + 0.25 * (lista_reglas[1]/n) \
                    + 0.25 * (lista_reglas[2]/n) + 0.25 * (lista_reglas[3]/n)
            elif not tildes and espacio and not minusculas and not caracteres_especiales:

                consistencia = 0.5 * (lista_reglas[0]/n) + 0.5 * (lista_reglas[1]/n) 
            elif  tildes and not espacio and not minusculas and not caracteres_especiales:
                consistencia = 0.33 * (lista_reglas[0]/n) + 0.33 * (lista_reglas[1]/n) \
                    + 0.33 * (lista_reglas[2]/n)
            elif tildes and  espacio and not minusculas and not caracteres_especiales:
                consistencia = 0.5 * (lista_reglas[0]/n) + 0.5 * (lista_reglas[1]/n) 
            elif  tildes and  espacio and not minusculas and caracteres_especiales:
                consistencia = (lista_reglas[0]/n)
            elif  tildes and  espacio and not mayusculas and not caracteres_especiales:
                consistencia = 0.5 * (lista_reglas[0]/n) + 0.5 * (lista_reglas[1]/n) 
            elif  tildes and  espacio and not mayusculas and caracteres_especiales:
                consistencia = (lista_reglas[0]/n)
            elif  tildes and  espacio and not mayusculas and caracteres_especiales:
                consistencia =  (lista_reglas[0]/n)
            elif  not tildes and  not espacio and  not mayusculas and not minusculas and not caracteres_especiales:
                consistencia = 0.2 * (lista_reglas[0]/n) + 0.2 * (lista_reglas[1]/n) \
                    + 0.2 * (lista_reglas[2]/n) + 0.2 * (lista_reglas[3]/n) + 0.2 * (lista_reglas[4]/n)
        return f'El porcentaje de consistencia para la variable es de {round(consistencia * 100, 2)}%'

    
