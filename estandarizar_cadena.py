import re
def arreglar_cadena(cadena:str, tildes=False, mayuscular=False, minuscular=True, caracter_especial=False, espacios=True):
    if not caracter_especial:
        caracter_especial = re.compile(r'[\!|\$|\%|\^|\&|\*|\(|\)|\[|\]|\{|\}|;|:|,|\.|\/|<|>|?|\|\`|~|\-|=|\_|\+]')
        cadena = re.sub(caracter_especial, "", cadena)
    if not tildes:
        cadena = re.sub(r"Á", "A", cadena)
        cadena = re.sub(r"É", "E", cadena)
        cadena = re.sub(r"Í", "I", cadena)
        cadena = re.sub(r"Ó", "O", cadena)
        cadena = re.sub(r"Ú", "U", cadena)
        cadena = re.sub(r"á", "a", cadena)
        cadena = re.sub(r"é", "e", cadena)
        cadena = re.sub(r"í", "i", cadena)
        cadena = re.sub(r"ó", "o", cadena)
        cadena = re.sub(r"ú", "u", cadena)
    if not mayuscular:
        cadena = cadena.lower()
    if not minuscular:
        cadena = cadena.upper()
    if not espacios:
        cadena = cadena.replace(' ', '')
    return cadena

    

