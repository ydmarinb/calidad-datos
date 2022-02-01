from ast import Str
import numpy as np
import re
from datetime import datetime
import pandas as pd
from collections import Counter
import scipy.stats as etd


class Fecha:
    def __init__(self, valores, formato="%Y-%m-%d") -> None:
        self.__valores = np.array(valores.astype(str))
        self.__n = len(self.__valores)    
        self.__formato = formato

    def __distribucion_acumulada(self, valores:np.array) -> np.array:
        n = len(valores)
        distribucion_empirica = np.array([0.0]*n)
        s = 0
        for i in range(n):
            s += valores[i]
            distribucion_empirica[i] = s
        return distribucion_empirica
    
    def evaluacion_exactitud(self, minimo_teorico:str, maximo_teorico:str,\
                             distribucion_teorica:tuple, suma_reglas=None,\
                                  frecuencia="dias") -> str:
        # Eliminar vacios
        valores = np.array(list(filter(lambda x: str(x)!='NaT', self.__valores)))
        n = len(valores)
        # Convertir maximo y minumos a fecha
        minimo_teorico = datetime.strptime(minimo_teorico, "%Y-%m-%d")
        maximo_teorico = datetime.strptime(maximo_teorico, "%Y-%m-%d")
        minimo_teorico = np.datetime64(minimo_teorico.date())
        maximo_teorico = np.datetime64(maximo_teorico.date())
        # Calcula el tiempo de vigencia real del campo
        fecha = pd.Series(valores)
        fecha = pd.to_datetime(fecha, format = self.__formato)
        hoy = np.datetime64(datetime.now().date())
        diferencia_fechas = hoy - fecha
        if frecuencia == "dias":
            diferencia_fechas = diferencia_fechas.astype('timedelta64[D]')
        elif frecuencia == "meses":
            diferencia_fechas = diferencia_fechas.astype('timedelta64[M]')
        else:
            diferencia_fechas = diferencia_fechas.astype('timedelta64[Y]')
        # Determinar quienes superan el maximo y el minimo teorico
        total_superan_maximo = sum(diferencia_fechas >\
             int(str.split(str(hoy - (maximo_teorico)), " ")[0]))
        total_superan_minimo = sum(int(str.split(str(hoy - (minimo_teorico)), " ")[0]) <\
             diferencia_fechas )
        # Construir la distribución acumulada teorica
        distribucion_teorica_aux1 = np.array(distribucion_teorica) / 10
        distribucion_teorica_aux2 = np.sum(distribucion_teorica_aux1)
        distribucion_teorica_aux3 = distribucion_teorica_aux1 / distribucion_teorica_aux2
        distribucion_acumulada_teorica = self.__distribucion_acumulada(distribucion_teorica_aux3)
        # Construir la distribución acumulada empirica
        distribucion_empirica = np.histogram(diferencia_fechas, bins="sturges")[0]
        distribucion_empirica = distribucion_empirica / n
        distribucion_acumulada_empirica = self.__distribucion_acumulada(distribucion_empirica)
        # Calculo test kolmogorov-smirnov
        d_nm = np.max(distribucion_acumulada_empirica - distribucion_acumulada_teorica)
        if n < 30:
            d_critico = np.sqrt(-np.log(0.05/2) * (1/n))
        else:
            d_critico = 1.358 * np.sqrt(2*n / n ** 2)
        if d_nm > d_critico:
            resultado_test = "diferentes"
        else:
            resultado_test = "similares"
        # Calcular porcentaje de exactitud
        if resultado_test == "similares":
            exactitud = (0.15 * (n-total_superan_maximo)/n) + (0.15 *\
                    (n-total_superan_minimo)/n) + 0.7
        else:
            exactitud = 0.25 * ((n-total_superan_maximo)/n) + (0.25 \
                * ((n-total_superan_minimo)/n))  
        return f'El porcentaje de exactitud para la variable es de {exactitud * 100}%'

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
        return f'El porcentaje de actualidad para la variable es de {actualidad * 100}%'

    def evaluacion_completitud(self) -> str:
        # Contar el totol de valores nulos
        total_nulos = len(np.array(list(filter(lambda x: str(x)=='NaT', self.__valores))))
        # Calcular porcentaje de completitud
        completitud = (self.__n - total_nulos) / self.__n
        return  f'El porcentaje de completitud para la variable es de {round(completitud * 100, 2)}%'
    
    def evaluacion_accesibilidad(self, acceso:int, plantilla:int,\
        presentacion:int, restriccion:int) -> str:
        # Calcular porcentaje de accesibilidad
        accesibilidad = 0.6*plantilla + 0.2*presentacion + 0.1*presentacion + 0.1*(1-restriccion)
        return f'El porcentaje de accesibilidad para la variable es de {accesibilidad * 100}%'

    def evaluacion_consistencia(self) -> str:
        # Definicion de formato estandar
        formato_fecha = re.compile("[0-9]{4}\-[0-9]{2}\-[0-9]{2}")
        tiene_estandar = sum(list(map(lambda x: 1 if formato_fecha.match(x)!= None else 0,\
             self.__valores)))
        # Calcular porcentaje de consistencia
        consistencia =  tiene_estandar / self.__n
        return f'El porcentaje de consistencia para la variable es de {consistencia * 100}%'

    
