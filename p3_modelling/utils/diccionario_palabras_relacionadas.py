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
    d = {'aplicaciones': ['aplicaciones', ' app ', 'aplicacion ', 'youtube', 'amazon', ' flow ', 'disney', 'prime ', 'netflix', 'sistema', 'operativo', 'spotify', 'google', ' hbo ', 'navegador', 'android', ' so ', 'software'],  # 'internet'? # no usaria: ' smart'  3 le meto espacio a aplicacion para que no me borre aplicaciones
         'agua': [' agua '],
         'actividad': ['actividad fisica'],
         'bateria': ['bateria', 'duracion', ' carga ', ' autonomia'],
         'bluetooth': ['bluetooth'],  #  en auris podria usar (pero no en tv pues se mezcla con conexion a internet): ['conexion ', ' empareja', ' sincroniz', ' vincula', ' desconect', ' conectar '],
         'camara': [' camara', ' fotos', 'imagenes', 'resolucion', 'zoom'],  # no incluiria: definicon, videos   # saco temporalmente 'selfie' y 'resolucion' # foto no pues si se refiere a la camara es "fotos". foto se confunde con la foto de la publicacion..
         'cable': ['antena', ' aire ', 'videocable', 'canales de cable', ' tda '], # cable no porque e utilizado para muchos otros significados
         'diseño': ['diseño', 'estetica', 'terminacion', 'aspecto', ' peso ', ' pesad', ' livian'],  #' tamaño ', ' peso ', ' pesad', ' livian'],  # en tv agreguee desde tamanño (chequear si esta bieen)
         'gps': [' gps '],
         'hdmi': [' entrada hdmi', 'entradas hdmi', 'puerto' 'entrada usb', 'entradas usb'],
         'imagen': ['imagen', 'resolucion', ' 4k ', ' hd ', 'colores', 'pantalla', 'definicion', ' hdr '],  #Por producto tv
         'juegos': ['juegos', 'jueguito', 'gaming'],
         'microfono': ['microfono', ' micro ', ' mic '],
         'material': ['material', 'construccion', 'agarre', 'tacto', 'antideslizante', ' grip '],
         'memoria': [' memoria', 'almacenamiento', ' ram ', ' ram,', 'velocidad', 'espacio', 'capacidad', 'gb ', ' disco ', ' ssd '],  # no incluiria: lag  # saco temporalmente ' rapid', ' lent'  # rapido no tiene asociado sentiment alto.. perjudica cuando dicen "es rapidp", ' fluid'
         'mensajes': ['mensajes', 'notificaciones', 'whastsapp'],
         'marca': ['marca'] + l_marcas,
         'oreja': [' oreja', 'cabeza', 'comodo', 'comodidad ', 'almohadillas', ' gomas ', ' oido', 'diseño'],
         'pantalla': [' pantalla', ' imagen ', ' imagen,', ' brillo', 'definicion', 'tactil'],  # no incluiria: definicion
         'presion': ["presion arterial"],
         'proteccion': ['proteccion', 'protege', 'protej', 'caid', 'cubre ', 'cubrir', 'resiste', 'reforzada', 'cayo', 'golpes'], # bordees?
         'pulsaciones': ['pulsaciones', "frecuencia cardiaca"],
         'precio': ['precio', 'costo', ' caro ', ' caro,', 'barato', 'carisimo'],
         'procesador': ['procesador', 'velocidad', 'funcionamiento', 'software', ' rapid', ' lent', ' tilda', ' fluid',' traba '],
         'ruido': [' ruido', 'cancelacion', ' aisla', 'noise cancelling'],
         'señal': [' señal ', 'datos moviles'],
         'sistema': ['sistema operativo'] + l_sistemas_operativos, # ahora no se si seguir usandolo, o si usar "aplicaciones" --> tengo que ver para celulares que hago
         'sonido': ['sonido', 'audio ', 'audio,', 'volumen', 'escucha', ' suena', 'parlante'],
         'tamaño': [' tamaño ', ' peso ', ' pesad', ' livian'],  # en celulares usaria (pero no en tv)?
         'teclado': ['teclas', ' ñ '],
         'video': ['video', ' placa ', 'juego', 'tarjeta grafica']  # https://www.xataka.com/basics/tarjeta-grafica-que-que-hay-dentro-como-funciona
         }
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