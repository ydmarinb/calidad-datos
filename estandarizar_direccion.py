import re
import pandas as pd
import numpy as np
from datetime import datetime as dt


class Direccion():
    def __init__(self):
        self.estandar = {'nomenclatura_princial' : None,
        'numero_principal' : None,
        'letra' : None,
        'numero_secundario' : None,
        'numero_puerta' : None
        }
    

    def isvalid(self):
         return self.estandar['nomenclatura_princial'] is not None and\
         self.estandar['numero_principal'] is not None and\
         self.estandar['numero_secundario'] is not None 

    def txt(self):
        txt = '{nomenclatura_princial} {numero_principal} {letra} # {numero_secundario} - {numero_puerta}'\
            .format(**{k: v if v is not None else '' for k,v in self.estandar.items()})
        while txt.find('   ') >=0 :
            txt = txt.replace('   ', '  ')
        return txt


separar_caracter_numero = re.compile(r'([A-Z])([0-9])', re.IGNORECASE)# ignorar mayusculas y minusculas
separar_numero_caracter = re.compile(r'([0-9])([A-Z])', re.IGNORECASE)
separar_letra = re.compile(r'([A-F])([NS])', re.IGNORECASE)
separar_caracter_numero = re.compile(r'([A-Z])([0-9])', re.IGNORECASE)
separar_numero_caracter = re.compile(r'([0-9])([A-Z])', re.IGNORECASE)
separar_numero_especial = re.compile(r'([0-9])([\!|\$|\%|\^|\&|\*|\(|\)|\[|\]|\{|\}|;|:|,|\.|\/|<|>|?|\|\`|#|~|\-|=|\_|\+])'\
                    , re.IGNORECASE)
separar_especial_numero = re.compile(r'([\!|\$|\%|\^|\&|\*|\(|\)|\[|\]|\{|\}|;|:|,|\.|\/|<|>|?|\|\`|~|\-|#|=|\_|\+])([0-9])'\
                , re.IGNORECASE)
separar_caracter_especial = re.compile(r'([A-Z])([\!|\$|\%|\^|\&|\*|\(|\)|\[|\]|\{|\}|;|:|,|\.|\/|<|>|?|\|\`|~|\-|=|#|\_|\+])'\
                    , re.IGNORECASE)
separar_especial_caracter = re.compile(r'([\!|\$|\%|\^|\&|\*|\(|\)|\[|\]|\{|\}|;|:|,|\.|\/|<|>|?|\|\`|~|\-|#|=|\_|\+])([A-Z])'\
                , re.IGNORECASE)

def levenshtein_ratio_and_distance(s, t, ratio_calc = True):
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
        
import re

def arreglar_direccion(direccion_cruda, categorias_teoricas):
   

    direccion_temp = direccion_cruda
    if direccion_temp is None or direccion_temp == "":
        return None

    direccion_temp = direccion_temp.upper()
    direccion_temp = separar_caracter_numero.sub(r'\1 \2', direccion_temp)
    direccion_temp = separar_numero_caracter.sub(r'\1 \2', direccion_temp)
    direccion_temp = separar_numero_especial.sub(r'\1 \2', direccion_temp)
    direccion_temp = separar_especial_numero.sub(r'\1 \2', direccion_temp)
    direccion_temp = separar_caracter_especial.sub(r'\1 \2', direccion_temp)
    direccion_temp = separar_especial_caracter.sub(r'\1 \2', direccion_temp)


    patron = re.compile("[A-Z]{2,}")
    for palabra in direccion_temp.split():
        if re.search(patron, palabra):
            distancias = list(map(lambda x: (levenshtein_ratio_and_distance(palabra,\
                        str(x)), x), categorias_teoricas))
            similutud =  max(dict(distancias).keys())
            llave = dict(distancias)[similutud] if similutud > 0 else 'none'
            direccion_temp = direccion_temp.replace(palabra, llave)
    
    

    direccion = Direccion()


    for parte in direccion_temp.split(' '):
        if direccion.estandar['nomenclatura_princial'] is None and direccion.estandar['numero_principal'] is None:
            if parte in ('CL.', 'CRA.', 'DIG.', 'TRAV.'):
                direccion.estandar['nomenclatura_princial'] = parte
        elif direccion.estandar['nomenclatura_princial'] is not None and direccion.estandar['numero_principal'] is None and direccion.estandar['letra'] is None:
            if parte.isnumeric():
                direccion.estandar['numero_principal'] = parte
        elif direccion.estandar['nomenclatura_princial'] is not None and direccion.estandar['numero_principal'] is not None\
             and direccion.estandar['letra'] is None and direccion.estandar['numero_secundario'] is None:
            if parte in ('A', 'B', 'C', 'D', 'E'):
                direccion.estandar['letra'] = parte
            if parte.isnumeric():
                direccion.estandar['numero_secundario'] = parte
        elif direccion.estandar['nomenclatura_princial'] is not None and direccion.estandar['numero_principal'] is not None\
             and direccion.estandar['letra'] is not None and direccion.estandar['numero_secundario'] is None:
            if parte.isnumeric():
                direccion.estandar['numero_secundario'] = parte
        elif direccion.estandar['nomenclatura_princial'] is not None and direccion.estandar['numero_principal'] is not None \
             and direccion.estandar['numero_secundario'] is not None and direccion.estandar['numero_puerta'] is None:
            if parte.isnumeric():
                direccion.estandar['numero_puerta'] = parte
    direccion_buena =  direccion.txt() if direccion.isvalid() else direccion_cruda

    caracter_especial = re.compile(r'[\!|\$|\%|\^|\&|\*|\(|\)|\[|\]|\{|\}|;|:|,|\/|<|>|?|\|\`|~|=|\_|\+]')
    direccion_buena = re.sub(caracter_especial, "", direccion_buena)
    no_letra = re.compile(r'[A-Za-z]{2,}')
    no_numeros = re.compile(r'[0-9]')
    direccion_buena = direccion_buena.upper()
    if not re.search(no_numeros, direccion_buena):
        direccion_buena = np.nan
    elif not re.search(no_letra, direccion_buena):
        direccion_buena = np.nan
    elif len(str(direccion_buena))<10:
        direccion_buena = np.nan
    elif direccion_buena == "":
        direccion_buena = np.nan
    return direccion_buena







