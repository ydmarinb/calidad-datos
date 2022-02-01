import re
import pandas as pd
import numpy as np
def estandar_numero(celular):
    caracter_especial = re.compile(r'[\!|\$|\%|\^|\&|\*|\(|\)|\[|\]|\{|\}|;|:|,|\.|\/|<|>|?|\|\`|~|\-|=|\_|\+]')
    letras = re.compile(r'[A-Z]')
    indicativo = re.compile(r'\+[0-9]{2}')
    numero_solo = re.compile(r'\([0-9]{1}\)')
    eliminar_extencion = re.compile(r'[A-Za-z]+\.?[0-9]*')
    cero_inicio = re.compile(r'^(0[0-9]{2})')
    siempre_cero = re.compile(r'^(0{3,})')
    no_numeros = re.compile(r'[0-9]')
    celular= celular.replace(" ", "")
    celular = re.sub(eliminar_extencion, "", celular)
    celular = re.sub(numero_solo, "", celular)
    celular = re.sub(indicativo, "", celular)
    celular = re.sub(caracter_especial, "", celular)
    celular = re.sub(letras, "", celular)
    celular = re.sub(cero_inicio, "", celular)
    celular = re.sub(siempre_cero, "", celular)
    if not re.search(no_numeros, celular):
        celular = np.nan
    if len(str(celular))<=5:
        celular = np.nan
    if celular == "":
        celular = np.nan
    return celular