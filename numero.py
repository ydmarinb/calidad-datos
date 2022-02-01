import numpy as np
import re
from datetime import datetime
import pandas as pd


class Numero:
    def __init__(self, valores):
        self.__valores = np.array(valores)
        self.n = len(self.__valores)

    def __distribucion_acumulada(self, valores:np.array) -> np.array:
        n = len(valores)
        distribucion_empirica = np.array([0.0]*n)
        s = 0
        for i in range(n):
            s += valores[i]
            distribucion_empirica[i] = s
        return distribucion_empirica
    
    
    def evaluacion_exactitud(self, minimo_teorico:int, maximo_teorico:int,\
                             distribucion_teorica:list, suma_reglas=None) -> str:
        # Eliminar vacios
        valores = np.array(list(filter(lambda x: ~np.isnan(x), np.array(self.__valores))))
        n = len(valores)
        # Determinar quienes superan el maximo y el minimo teorico
        total_superan_maximo = sum(valores > maximo_teorico)
        total_superan_minimo = sum(valores < minimo_teorico)
        # Construir la distribución acumulada teorica
        distribucion_teorica_aux1 = np.array(distribucion_teorica) / 10
        distribucion_teorica_aux2 = np.sum(distribucion_teorica_aux1)
        distribucion_teorica_aux3 = distribucion_teorica_aux1 / distribucion_teorica_aux2
        distribucion_acumulada_teorica = self.__distribucion_acumulada(distribucion_teorica_aux3)
        # Construir la distribución acumulada empirica
        distribucion_empirica = np.histogram(valores, bins="sturges")[0]
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
        if suma_reglas:
            if resultado_test == "similares":
                exactitud = (0.1 * (n-total_superan_maximo)/n) + (0.1 *\
                     (n-total_superan_minimo)/n) + 0.3 + \
                    (0.5 * suma_reglas)
            else:
                exactitud = (0.1 * (n-total_superan_maximo)/n) + (0.1 \
                    * (n-total_superan_minimo)/n) + \
                    (0.5 * suma_reglas)
        else:
            if resultado_test == "similares":
                exactitud = (0.25 * (n-total_superan_maximo)/n) + (0.25 *\
                     (n-total_superan_minimo)/n) + 0.5
            else:
                exactitud = (0.25 * (n-total_superan_maximo)/n) + (0.25 \
                    * (n-total_superan_minimo)/n) 
        return f'El porcentaje de actualidad para la variable es de {round(exactitud * 100, 2)}%'

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
        actualidad = (self.n - pasaron_vigencia) / self.n
        return f'El porcentaje de actualidad para la variable es de {round(actualidad * 100, 2)}%'

    def evaluacion_completitud(self) -> str:
        # Contar el totol de valores nulos
        total_nulos = sum(pd.Series(self.__valores).isnull())
        # Calcular porcentaje de completitud
        completitud = (self.n - total_nulos) / self.n
        return  f'El porcentaje de completitud para la variable es de {round(completitud * 100, 2)}%'
    
    def evaluacion_accesibilidad(self, acceso:int, plantilla:int,\
        presentacion:int, restriccion:int) -> str:
        # Calcular porcentaje de accesibilidad
        accesibilidad = 0.6*plantilla + 0.2*presentacion + 0.1*presentacion + 0.1*(1-restriccion)
        return f'El porcentaje de accesibilidad para la variable es de {round(accesibilidad * 100, 2)}%'

    

    
        