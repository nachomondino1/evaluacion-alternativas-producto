import pickle
import pandas as pd
from p3_modelling.sentiment_atribution import delete_accent


def get_marcas(df_alt):
    """
    Obtiene marcas de un producto
    :param df_alt: Dataframe alternativas
    :return: Lista de marcas del producto.
    """
    # Defino variables
    l_marcas_cleaned = []  # Lista a retornar

    # OBTENGO MARCAS DEL PRODUCTO
    # Si el atributo se llama "Marca" (como en la mayoria)
    try:
        l_marcas = df_alt['Marca'].dropna().unique()

    # Si el atributo no se llama "Marca"
    except:
        # Busco el atributo que se refiera a la marca (ej: en producto "fundas de celular" se llama "Marca de la funda"
        for atributo in df_alt.columns:
            if 'marca' in atributo.lower():
                atrib_marca = atributo
                break

        l_marcas = df_alt[atrib_marca].dropna().unique()
        print("Atributo de marca:", atrib_marca)


    # Limpio marcas para poder identificarlas en opiniones
    for marca in l_marcas:
        marca_limpia = delete_accent(marca.lower())  # pues sino no identificaria las marcas dado que las opis estan limpias
        marca_limpia = " " + marca_limpia + ' '  # pues sino lg seria identificada dentro de "algo" o de "alguno", etc
        l_marcas_cleaned.append(marca_limpia)
    return l_marcas_cleaned

def get_dict_related_words(df_alt):

    # Defino palabras relacionadas a algunas caracteristicas especificas   # deberia definirlos automaticamente segun valores unicos de atrib del producto?
    l_marcas = get_marcas(df_alt)  # falla en smartband dado que no queda el atrib marca en df_alt_cleaned.

    l_sistemas_operativos = ['android',
                             'blackberry os',
                             ' ios ',
                             'ginga ',
                             'kaios', 'kaistore',
                             #'nokia',
                             'threadx', 'tizen',
                             'linux'
                             's30 +', 'saphi',
                             'vidaa'
                             'xmart ui',
                             'windows phone', ' webos '
                             ]

    # ojo con incluir ADJ o VERB dado que asi como se pueden usar para un sustantivo se pueden usar para otros. Por ej, 'grande' puede ser para 'tamaño' asi como puede ser 'el inconveniente mas grande es...'
    # Defino diccionario de palabras relacionadas para mejorar identificacion de customer needs
    d = {'aplicaciones': ['aplicaciones', ' app', 'aplicacion', 'sistema smart', 'youtube', 'amazon', ' flow', 'disney', 'prime ', 'netflix', 'spotify', ' hbo ', 'navegador', 'browser', 'star'],  # Las apps propiamente se mencionan sin referirse a la cantidad de estas... -->'youtube', 'amazon', ' flow ', 'disney', 'prime ', 'netflix', 'spotify', 'google', ' hbo ', 'navegador'],  # 'sistema', 'operativo', 'android', ' so ', 'software'],  # 'internet'? # no usaria: ' smart'  3
         'agua': [' agua ', 'agua,', 'agua.' 'sumergi'],  #  no incluyo bañar (VERB)
         'bateria': ['bateria', 'duracion', ' carga ', ' autonomia'],
         'bluetooth': ['bluetooth', 'inalambrico'],  #  en auris podria usar (pero no en tv pues se mezcla con conexion a internet): ['conexion ', ' empareja', ' sincroniz', ' vincula', ' desconect', ' conectar '],
         'camara': [' camara', ' fotos', 'imagenes', 'resolucion'],  # no incluiria: definicon, videos 'selfie' # foto no pues si se refiere a la camara es "fotos". foto se confunde con la foto de la publicacion..
         'diseño': ['diseño', 'estetica', 'terminacion', 'aspecto ', 'tamaño', ' peso ', ' pesad', ' livian', ' comod', 'incomod', 'ergonom', 'materiales', 'material', 'construc'],  # En smartband:  considere tam y peso en materiales (tal vez podria llevarlo a diseño). # comod con esp al ppio por "acomodar"...
         'funciones': ['funciones', 'funcion', 'sensores', 'actividad', 'deporte', 'deportiv', 'entrenamiento', 'ejercicio'], # 'pasos', 'musica', 'llamada', 'pulso', 'mensajes', 'estres', 'relaja', 'cardiac', 'sueño', 'menstrual'],  # no incluyo 'pasos', 'distancia recorrida', 'cardiac', 'pulso', 'pulsaciones', 'gps' pues habla de la medicion precisa o no y no de si tiene tal sensor o no.
         'gps': ['gps'],
         # 'huella': ['huella', 'iris', 'facial'],
         'imagen': ['imagen', 'resolucion', ' 4k ', ' hd ', 'colores', 'pantalla', 'definicion', ' hdr '],
         'marca': ['marca'] + l_marcas,
         'materiales': ['materiales', 'material', 'construc'], # 'agarre', 'tacto', 'antideslizante', ' grip '],
         'memoria': ['memoria', 'interna', 'almacenamiento', 'espacio', 'capacidad', ' disco ', ' ssd ', 'juegos', 'gamer ','gaming'],  # no incluiria: lag. # inclui juegos porque necesitas espacio para tenerlos..
         'microfono': ['microfono', ' micro ', ' mic '],
         'oreja': [' oreja', 'cabeza', 'comodo', 'comodidad ', 'almohadillas', ' gomas ', ' oido', 'diseño'],
         'pantalla': [' pantalla', ' imagen ', ' imagen,', ' brillo', 'definicion', 'display'],  # no incluiria: tactil (se refiere a vel con que responde)
         'proteccion': ['proteccion', 'protege', 'protej', 'caid', 'cubre ', 'cubrir', 'resiste', 'reforzada', 'cayo', 'golpes'], # bordees?
         'precio': ['precio', 'costo', ' caro ', ' caro,', ' barat', 'carisim'], # caro y barato son ADJ pero siempre se refieren al SUST precio
         'ruido': [' ruido', 'cancelacion', ' aisla', 'noise cancelling'],
         # 'señal': [' señal ', 'datos moviles', '4g ', '5g ', '3g ', '3g '],  # espacio despues de por gb
         'sonido': ['sonido', 'audio ', 'audio,', 'volumen', 'escucha', 'parlante', ' suena'],
         # 'tamaño': ['tamaño'],  # pense en agregar "pulgadas" pero no se refieren a si es chico o gde. ' peso ', ' pesad', ' livian'],  # en celulares usaria (pero no en tv)? no deberia tener relacion con el peso pues es exclusivante el tamaño de la pantalla y no del dispositivo
         'teclado': ['teclas', ' ñ '],
         'usar': [' de usar', 'sistema', 'operativo', 'software', 'interfaz'] + l_sistemas_operativos, # ' usar ' es un verb y como tal se usa para otros sustantivos.. pero 'de usar' engloba 'facil de usar', 'practico de usar', 'no es dificil de usar', etc. Tuve que sacar 'entender' y 'intuitivo'. Uso 'sistema' a pesar de que exista sistema de audio, etc pues a veces se menciona solo como sistema y deams permite ahorrar ['sistemas operativos', 'sistema operativo', 'sistema smart']
         'video': ['video', ' placa ', 'juego', 'tarjeta grafica'],  # https://www.xataka.com/basics/tarjeta-grafica-que-que-hay-dentro-como-funciona
         'velocidad': ['velocidad', 'procesa', ' ram ', ' ram,', 'funcionamiento', 'software', 'respuesta', 'juegos', 'gamer ', 'gaming', 'streaming', 'simultaneo', 'mismo tiempo', 'veloz', ' rapid', ' lent', ' tilda', ' fluid', ' traba '], # 'procesa' incluye 'porcesador' y 'procesamiento'.  # rapido no tiene asociado sentiment alto.. perjudica cuando dicen "es rapidp", ' fluid'
         'voz': ['voz', 'assistant', 'alexa']
         }
    # no uso mas sistema sino 'usar' --> 'sistema': ['sistema operativo'] + l_sistemas_operativos,  # ahora no se si seguir usandolo, o si usar "aplicaciones" --> tengo que ver para celulares que hago

    return d

def main(df_alt):
    # Inicializo diccionario
    d_rel_words = get_dict_related_words(df_alt)

    '''
    # Imprimo diccionario por terminal
    for cust_need in d_rel_words.keys():
        print("Palabra: ", cust_need, "Relacionadas:", d_rel_words[cust_need])
    '''

    # Exporto diccionario
    with open("d_rel_words.pkl", "wb") as tf:
        pickle.dump(d_rel_words, tf)

''' Prueba
df_alt = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/auriculares/df_alt.xlsx')
main(df_alt)
'''