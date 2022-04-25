# Importo librerias
import pandas as pd
import string
import requests
from nltk.stem import SnowballStemmer

""" ALTERNATIVA 2: SIN CLASE """
def delete_accent(text):
    """
    Remueve acentos de una cadena de texto
    :param text: Texto en minuscula
    :return: Texto en miniscula sin acentos
    """
    # Defino variables
    d = {'á': "a", 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'}  # diccionario, letra con acento en key y sin en value
    new_text = str()  # nuevo texto sin acentos

    # Recorro cada letra del texto
    for i in range(len(text)):
        if text[i] in d.keys():
             new_text += d[text[i]]
        else:
            new_text += text[i]

    return new_text

def delete_punctuation(text):
    # Defino variables
    new_text = str()  # nuevo texto sin acentos

    # Recorro cada letra del texto
    for i in range(len(text)):

        # si es un signo de puntuacion
        if text[i] in string.punctuation:
            # guardar string vacio
            new_text += ""

        # no es un signo de puntuacion
        else:
            # guardo string
            new_text += text[i]

    return new_text

def stop_word_removal(tokens):
    """

    :param tokens:
    :return:
    """
    # Read lista de palabras a remover (vacias.txt)
    path = '/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data_preparation/vacias.txt'
    palabras_vacias = pd.read_csv(path)
    palabras_vacias = list(palabras_vacias['palabra'])  # ['palabra'] hace que acceda a la columna y lo convierto en lista para poder hacer la comparacion if token in palabras vacias

    # Defino variable
    new_tokens = []  # Lista de tokens nuevos sin las palabras vacias

    # Por token en tokens
    for token in tokens:

        # Si el token es una palabra vacia
        if token in palabras_vacias:

            # No guardar el token
            pass

        # Si el token no es una palabra vacia
        else:
            # Guardo token
            new_tokens.append(token)

    return new_tokens

def dowload_stop_word_removal_file():
    url = 'https://raw.githubusercontent.com/7PartidasDigital/AnaText/master/datos/diccionarios/vacias.txt'
    r = requests.get(url, allow_redirects=True)
    return open('vacias.txt', 'wb').write(r.content)

def steamming(tokens):
    new_tokens = []
    spanish_stemmer = SnowballStemmer('spanish')

    for token in tokens:
        new_tokens.append(spanish_stemmer.stem(token))

    return new_tokens


'''
""" ALTERNATIVA 1: CON CLASE """
# Te da la opcion de usar solo si queres algunas funcionalidades
# podria decidir hacer steam para establecer customerr needs y no para el modelo de sentiment por ejemplo. te da esa funcionalidad.
# Ademas puedo usar esta clase para otro proyecto...
# igual no pienso crear dos objetos por corrida y limpiar las opiniones dos veces... en ese caso no seria necesaria la clase..
class TextPreparation:

    def __init__(self, textos):
        self.textos = textos

    def text_preparation(self, acentos=True, puntuacion=True, steam=True):

        df = pd.DataFrame(columns=["col"])

        # POR OPINION
        for opinion in self.textos:

            # Lo convierto en miniscula
            opinion = opinion.lower()

            # Correccion de repeticiones 'largooo' en vez de 'largo'
            # Correccion de palabras (mala escritura) 'espectativas' en vez de 'expectativas'
            # Correccion de abreviaturas 'q' en vez de 'que'

            # Elimino acentos
            if acentos:  # solo corrigo si quiere
                opinion = delete_accent(opinion)
            # print(opinion)

            # Elimino puntuacion
            if puntuacion:
                opinion = delete_punctuation(opinion)
            # print(opinion)

            # (1) TOKENIZATION: SEPARO SUS PALABRAS POR ESPACIOS EN BLANCO
            tokens = opinion.split()

            # (2) STOP WORD REMOVAL
            tokens = stop_word_removal(tokens)

            # (3) STEAM
            if steam:
                tokens = steamming(tokens)

                for token in tokens:
                    df = df.append({"col": token}, ignore_index=True)

            # faltaria guardar la opinion limpia

        print(df.value_counts()[:20])
        return df   # devuelvo el dataframe cleaned

    def delete_accent(self, text):
        """
        Remueve acentos de una cadena de texto
        :param text: Texto en minuscula
        :return: Texto en miniscula sin acentos
        """
        # Defino variables
        d = {'á': "a", 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'}  # diccionario, letra con acento en key y sin en value
        new_text = str()  # nuevo texto sin acentos

        # Recorro cada letra del texto
        for i in range(len(text)):
            if text[i] in d.keys():
                new_text += d[text[i]]
            else:
                new_text += text[i]

        return new_text

    def delete_punctuation(self, text):
        # Defino variables
        new_text = str()  # nuevo texto sin acentos

        # Recorro cada letra del texto
        for i in range(len(text)):

            # si es un signo de puntuacion
            if text[i] in string.punctuation:
                # guardar string vacio
                new_text += ""

            # no es un signo de puntuacion
            else:
                # guardo string
                new_text += text[i]

        return new_text

    def stop_word_removal(self, tokens):

        # Read lista de palabras a remover (vacias.txt)
        path = '/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data_preparation/vacias.txt'
        palabras_vacias = pd.read_csv(path)
        palabras_vacias = list(palabras_vacias[
                                   'palabra'])  # ['palabra'] hace que acceda a la columna y lo convierto en lista para poder hacer la comparacion if token in palabras vacias

        # Defino variable
        new_tokens = []  # Lista de tokens nuevos sin las palabras vacias

        # Por token en tokens
        for token in tokens:

            # Si el token es una palabra vacia
            if token in palabras_vacias:

                # No guardar el token
                pass

            # Si el token no es una palabra vacia
            else:
                # Guardo token
                new_tokens.append(token)

        return new_tokens

    def dowload_stop_word_removal_file(self):
        url = 'https://raw.githubusercontent.com/7PartidasDigital/AnaText/master/datos/diccionarios/vacias.txt'
        r = requests.get(url, allow_redirects=True)
        return open('vacias.txt', 'wb').write(r.content)

    def steamming(self, tokens):
        new_tokens = []
        spanish_stemmer = SnowballStemmer('spanish')

        for token in tokens:
            new_tokens.append(spanish_stemmer.stem(token))

        return new_tokens

'''