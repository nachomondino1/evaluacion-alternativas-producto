# Importo librerias
import pandas as pd
import string
import requests
from nltk.stem import SnowballStemmer


class TextPreparation:
    """Techniques to prepare text"""

    def __init__(self, textos):
        self.textos = textos  # debe ser una serie de pandas y no una frase suelta

    def to_lower(self):
        """
        Convierte a miniscula los textos de la Serie de texto
        :return: Serie del texto en miniscula
        """
        # Defino variables
        new_texts = []

        # Por text
        for text in self.textos:

            # Obtengo texto en miniscula
            new_text = text.lower()

            # Guardo texto procesado
            new_texts.append(new_text)

        # Reemplazo textos por textos procesados
        self.textos = pd.Series(new_texts)
        return self.textos

    def delete_accent(self):
        """
        Remueve acentos de textos de una Serie de texto
        :return: Serie del texto sin acentos
        """
        # Defino variables
        d = {'á': "a", 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'}  # diccionario, letra con acento en key y sin en value
        new_texts = []

        # Por texto
        for text in self.textos:
            new_text = str()

            # Recorro cada letra del texto
            for i in range(len(text)):

                # Si la letra tiene acento
                if text[i] in d.keys():

                    # Reemplazo letra con acento por letra sin acento
                    new_text += d[text[i]]

                # Si la letra no tiene acento
                else:
                    # no reemplazo nada
                    new_text += text[i]

            # Guardo texto procesado
            new_texts.append(new_text)

        # Reemplazo textos por textos procesados
        self.textos = pd.Series(new_texts)
        return self.textos

    def delete_punctuation(self):
        """
        Elimina cualquier signo de puntuacion de textos de una Serie de texto
        :return: Serie del texto sin puntuacion
        """
        # Defino variables
        new_texts = []

        # Por text
        for text in self.textos:
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

            # Guardo texto procesado
            new_texts.append(new_text)

        # Reemplazo textos por textos procesados
        self.textos = pd.Series(new_texts)
        return self.textos

    def tokenize(self):
        """
        Tokeniza textos de una Serie de texto, es decir, convierte cada texto en una lista cuyos elementos es cada
        palabra de este.
        :return: Serie del texto tokenizado
        """
        # Defino variables
        new_texts = []

        # Por text
        for text in self.textos:

            # Hago split
            new_text = text.split()

            # Guardo texto procesado
            new_texts.append(new_text)

        # Reemplazo textos por textos procesados
        self.textos = pd.Series(new_texts)

        return self.textos

    def stop_word_removal(self):
        """
        Elimina palabras vacias de textos de una Serie de texto
        :return: Serie del texto sin palabras vacias
        """
        # Read lista de palabras a remover (vacias.txt)
        path = '/p2_data_preparation/utils/vacias.txt'
        palabras_vacias = pd.read_csv(path)
        palabras_vacias = list(palabras_vacias['palabra'])  # ['palabra'] hace que acceda a la columna y lo convierto en lista para poder hacer la comparacion if token in palabras vacias

        # Defino variable
        new_texts = []

        # Por text
        for text in self.textos:

            new_text = []  # Lista de tokens nuevos sin las palabras vacias

            # Por palabra del texto
            for word in text:

                # Si la palabra es una palabra vacia
                if word in palabras_vacias:

                    # No guardo la palabra
                    pass

                # Si la palabra no es una palabra vacia
                else:
                    # Guardo palabra
                    new_text.append(word)

            # Guardo texto procesado
            new_texts.append(new_text)

        # Reemplazo textos por textos procesados
        self.textos = pd.Series(new_texts)

        return self.textos

    def dowload_stop_word_removal_file(self):
        """
        Descarga archivo que contiene todas las palabras vacias
        :return:
        """
        url = 'https://raw.githubusercontent.com/7PartidasDigital/AnaText/master/datos/diccionarios/vacias.txt'
        r = requests.get(url, allow_redirects=True)
        return open('vacias.txt', 'wb').write(r.content)

    def steamming(self):
        """
        Aplica steamming de textos de una Serie de texto
        :return: Serie del texto con palabras steam
        """
        # Defino variables
        new_text = []
        new_texts = []
        spanish_stemmer = SnowballStemmer('spanish')

        # Por token
        for token in self.textos:

            # Por palabra
            for word in token:

                # Le hago steam a la palabra
                new_text.append(spanish_stemmer.stem(word))

            # Guardo texto procesado
            new_texts.append(new_text)

        # Reemplazo textos por textos procesados
        self.textos = pd.Series(new_texts)

        return self.textos
