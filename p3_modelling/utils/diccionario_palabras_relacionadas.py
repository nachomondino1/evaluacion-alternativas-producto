import pickle
import pandas as pd
from p3_modelling.sentiment_atribution import delete_accent


def get_marcas(df_alt):

    l_marcas = df_alt['Marca'].dropna().unique()
    l_marcas_cleaned = []
    for marca in l_marcas:
        marca = delete_accent(marca.lower())  # pues sino no identificaria las marcas dado que las opis estan limpias
        marca = " " + marca + " "  # pues sino lg seria identificada dentro de "algo" o de "alguno", etc
        l_marcas_cleaned.append(marca)
    return l_marcas_cleaned

def get_dict_related_words(df_alt):

    # Defino palabras relacionadas a algunas caracteristicas especificas   # deberia definirlos automaticamente segun valores unicos de atrib del producto?
    l_marcas = get_marcas(df_alt)

    l_sistemas_operativos = ['android',
                           'blackberry os',
                           ' ios ',
                           'kaios', 'kaistore',
                           'nokia',
                           'threadx',
                           's30 +',
                           'windows phone',
                           ]

    # Defino diccionario de palabras relacionadas para mejorar identificacion de customer needs
    d = {'aplicaciones': [' app '],
         'camara': [' fotos', 'imagenes', 'resolucion'],  # no incluiria: definicon, videos   # saco temporalmente 'selfie' y 'resolucion' # foto no pues si se refiere a la camara es "fotos". foto se confunde con la foto de la publicacion..
         'bateria': ['duracion', ' carga ', ' autonomia '],
         'bluetooth': ['conexion ', ' empareja', ' sincroniz', ' vincula', ' desconect', ' conectar '],
         'diseño': ['estetica'],
         'juegos': ['jueguito'],
         'microfono': [' micro '],
         'material': ['construccion'],
         'memoria': ['almacenamiento', ' ram ', 'velocidad', 'espacio', ' ram,', ' fluid', 'capacidad', 'gb ', ' agil '],  # no incluiria: lag  # saco temporalmente ' rapid', ' lent'  # rapido no tiene asociado sentiment alto.. perjudica cuando dicen "es rapidp"
         'marca': l_marcas,
         'oreja': ['cabeza', 'comodo ', 'comodos', 'comodidad ', 'almohadillas', ' gomas ', ' oido'],
         'pantalla': [' imagen ', ' imagen,'],  # no incluiria: definicion
         'precio': ['costo', ' caro ', ' caro,', 'barato'],
         'ruido': ['cancelacion', ' aisla'],
         'sistema': l_sistemas_operativos,
         'tamaño': [' peso ', ' pesad', ' livian'],
         "procesador": ["velocidad", "funcionamiento", 'software', ' rapid', ' lent', ' tilda', ' fluid', ' traba ', ' agil '],
         'sonido': ['audio ', 'audio,' 'volumen', 'musica', 'escucha']
         }
    return d

def main(df_alt):

    # Inicializo diccionario
    d_rel_words = get_dict_related_words(df_alt)

    # Imprimo diccionario por terminal
    for cust_need in d_rel_words.keys():
        print("Palabra: ", cust_need, "Relacionadas:", d_rel_words[cust_need])

    # Exporto diccionario
    with open("d_rel_words.pkl", "wb") as tf:
        pickle.dump(d_rel_words, tf)

''' Prueba
df_alt = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/auriculares/df_alt.xlsx')
main(df_alt)
'''