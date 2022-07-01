import pickle
import pandas as pd

def get_dict_related_words(producto):

    '''
    Como selecciono customer needs?
    Obtengo lista de las n palabras mas frecuentes (por ej, n = 200).     Debo correr 'Data preparation'
    Por palabra frecuente,
        Identificar que significado tiene. Podria tener 1 solo significado o varios.
            Casos:
            1) Si tiene 1 significado => Mantengo la palabra
            2) Si tiene +1 significado => a) Mantengo la palabra y evito otros significados (FP) b) Quito la palabra
            Obs: Cuanto mas frecuente es una palabra, mayor es la posibilidad de que tenga mas de 1 significado.

        Asociar cada palabra frecuente a un significado (sera una customer need)
        Obs: ese importante entender que la relacion entre customer need y cantidad de significados es 1-1. Un significado por customer need.


    Como elegir palabras relacionadas?
    Una vez identificadas las customer needs:
    # Obtengo dataframe con las n palabras mas frecuentes (ordenado por frecuencia descendente)
    # Por palabra frecuente ir asociandola a la customer need que corresponda
    # Por customer need, verificar que cada una de sus palabras tenga un significado (el de la customer need). Si tuviese otro, puedo: 1) dejar la palabra igual pero evitar FP mediante dict_avoid 2) quitar la palabra


    Intento 1
    Como elegir palabras relacionadas?
    1) Por palabra mas frecuente (utilizadas por clientes en opiniones)
        Identificar significado de cada palabra. A que se refiere el cliente cuando usa la palabra? Cuidado: puede tener varios significados como por ejemplo pantalla (dividir pantalla, fondo de pantalla, tamano de pantalla, calidad de imagen, etc)
        Juntar palabras que se refieran a la misma caracteristica. Por ejemplo, 'imagen', 'pantalla' y 'definicion'.

    2) Identificar customer needs (cada una es un significado). Por ej, 'calidad de imagen' (y esta reunira varias palabras como imagen, pantalla, resolucion, defincion, etc)

    # identificar usos? puees no seran incluidos en cust needs...

    3) Obtener palabras utilizadas para referirse a la customer need incluyendo adjetivos. decir como...leyendo opis por ej

    4) Ver frecuencia de cada palabra relacionada (si hay 10000 opis minimo 20 sino no vale la pena). Descartar aquellas de baja frecuencia y centrarnos en las que tienen mayor frec
    # ordenar dic de pal rel segun frecuencia de pal rel (aumenta eficiencia del proceso)

    #tmb puede que descartes una customere need pues te das cuenta que no es tan frecuente al final (la frecuencia de una cust need es la suma de las frec de sus pal rel y hay veces que esta puede terminar siendo baja a pesar de tener una palabra frecuente...) Por ej, Tiene comando de voz

    5)  Las palabras muy frecueentes es probable que tengan mas de un significado. Si la quiero incluir igual tendree que utilizar el dict_Avoid para evitar FP.



    '''
    # Defino palabras relacionadas a algunas caracteristicas especificas   # deberia definirlos automaticamente segun valores unicos de atrib del producto?
    # l_marcas = get_marcas(df_alt)  # falla en smartband dado que no queda el atrib marca en df_alt_cleaned.

    # ojo con incluir ADJ o VERB dado que asi como se pueden usar para un sustantivo se pueden usar para otros. Por ej, 'grande' puede ser para 'tamaño' asi como puede ser 'el inconveniente mas grande es...'
    # Poner palabras relacionadas con mayor frecuencia primero para ser mas eficiente en tiempo (hace break antes)

    # Defino diccionario de palabras relacionadas para mejorar identificacion de customer needs

    # CELULARES
    l_sistemas_operativos = ['android', 'blackberry os', ' ios ', ' ginga ', ' kaios ', 'kaistore', ' miui ', #'nokia',
                             'threadx', ' tizen ', 'linux' 's30 +', ' saphi ', ' oreo ', ' vidaa' ' xmart ui',
                             'windows phone', ' webos ']
    l_pantallas = [' amoled ', ' lcd ', ' hd ', ' ips ', ' oled ', ' pls ', ' tft ']

    d1 = {'bateria': ['bateria', ' autonomia'],  # No incluiria: [cargador, carga, cargar, turbo] (hablan de tiempo de carga en lugar de duracion de bateria) ; [duracion, dura, ahorro] (siempre acompañados del termino "bateria") ; juegos (muy frecunete a la altura de bateria, taparia rdos), [pila, mah] (Pocas menciones)
        'camara': [' camara', ' fotos', 'definicion', ' selfie', ' filma', ' flash ', 'estabiliza', ' lente', 'fotografi'], # No incluiria: [hdr,  optico/a] (pocas menciones como para ver si agregar) ; [delantera, frontal, trasera, megapixeles, mp, grabacion, reflex, enfoque, luz] (siempre acompañados del termino 'camara'); [imagen (pant), zoom (app), foto (pub), grabar (audios),  video/s (video prop), imagenes (varios), luminosidad (pant)] (Otros significados) ; [gcam] (no se refieren a calidad de camara base) ;  # foto no pues si se refiere a la camara es "fotos". foto se confunde con la foto de la publicacion.. # filma incluye filmar, filmacion, filmaciones. # fotografi incluye fotografia/s fotografica
        'diseño': ['diseño', 'estetic', ' terminacion', 'material', 'construc', 'resisten', 'gorila glass', 'gorilla glass',
                   ' fragil', 'robust', ' caida', 'elegante', ' curvo', 'curvatura', ' cayo ', 'plastico ', ' moja',
                   ' acabado', ' facher', ' sobresale', 'delgad', ' ergonom', ' grueso ', ' pliega'],  # 'belleza ', ' bello ', 'bonito ', 'hermoso', --> muy grales como 'lindo' # No incluiria: [grip, aluminio, metal, golpe, resbaladizo, texturada] (Pocas menciones) ; [lindo (en gral), feo (varios), tacto (pant), agarre (detectar), aspecto (aspectos), cristal (otro), mate (otro), vidrio (protector), rompio (otro), atractivo(otro), compacto (tamaño)] (Otros significados)
        'memoria': ['memoria', 'capacidad', 'almacenamiento', ' espacio ', 'interna', 'juegos'],  #'pesadas', 'pesados'],  # No incluria: [sdd, disco, cant de apps] (Pocas menciones) ; [instalar (app y otro), varias apps (velocidad), descargar (varios), gb (ram), gigas (ram), aplicaciones (varios), hardware (gral)] (Otros significados) ; [sd, microsd] (no se refieren a tamaño de memoria base) ; [almacenar, 256, capacidad] (siempre acompañada de palabra relacionada)  juegos (muy frecuente a la altura de 'memoria', taparia rdos) juegos pesados (puede haber coment negativos por velocidad y no tiene que ver con memoria)
        'pantalla': [' pantalla ', 'resolucion', ' imagen ', 'refresco', ' grafic', ] + l_pantallas,  # No incluiria: [luminosidad, luz azul, iluminacion, 1080, 720, calidad de video, contraste, densidad] (pocas menciones) ; [hz] (No gano significativamente) ; [luz (camara), pantallas (otro), vista(varios), 4k (camara), pixeles (camara), nitidez (camara), tactil (responde), display (varios)] (Otros significados) ; [colores, definicion]  (siempre acompañados de 'pantalla') ; [brillo (como func el sensor de brillo autom)] (no se refieren a la calidad de la pantalla)    , display  # grafic incluye grafica/o/os/as
        'precio': ['precio', ' marca ', ' costo ', ' economic', ' barat', ' caro ', 'carisim', ' gastar', ' plata ',
                   ' dinero'],  # No incluiria: (1) Pocas menciones: dolares, euros (2) Muchos significados: gasto/a (bateria), vale (pena), sale (varios), cuesta (entender), pesos (varios) # caro y barato son ADJ pero siempre se refieren al SUST precio # No uso l_marcas pues hay mas FP # "marcas" incluye muchos FP (comparaciones de otros aspectos con otras marcas)
        'sistema': ['sistema ', ' facil ', 'funciones', 'tactil', 'software', 'funcionalidades', 'interfaz', 'interface', 'actualizaciones', ' so ', 'preinstal'] + l_sistemas_operativos, # Veer si agrego: configura # No incluiria: [operativo] (siempre acompañada de 'sistema') ; [imcompatible] (Pocas menciones) ; [funcion (varios), de usar (varios), actualizar (modelo), actualizacion (varios)]   (Otro significado)
        'sonido': ['sonido', 'volumen', 'escucha ', ' audio ', ' parlante', ' suena', ' altavo'], # No incluria: [peliculas, agudos, auditivamente] (Pocas menciones) ; [graves (problema), auriculares (si trae o no), musica (uso)] (Otro significado) ; [dolby] (siempre acomapañado de 'sonido') # ojo con escucha que no debe incluir escuchar # altavo incluye altavoz y altavoces
         'tamaño': ['tamaño ', ' grande ', ' comodo', ' livian', ' peso ', 'pesado ', 'pesada ',  'dimensiones', ' ancho ',
                    ' gigante', 'pulgadas', ' compact'],  # No incluiria: [pequeño (diseño), bolsillo (caidas), ligero (velocidad)] (Otros significados)    , 'pesa', ' comod', 'incomod', 'mano', largo, alto, angosto, armatoste, enorme (muy pocas veces se ref a tamaño, y las que lo hacen se pueden salvar) # pense en agregar "pulgadas" pero no se refieren a si es chico o gde. # Pongo 'pesado ' porque pesados se refiere a juegos pesados.
        'velocidad': ['velocidad', ' rapido ', 'procesador', 'juegos', ' ram ', 'rendimiento', 'mismo tiempo', ' lento ',
                      ' fluid', 'funcionamiento', ' tilda', 'agil', 'rapidez', ' lentitud ', 'procesamiento', 'snapdragon',
                      'exynos', 'calienta', 'calent', 'temperatura', ' avion ', ' vuela ', ' nave ', ' potencia ',
                      'abren y cierran', ' corre ', ' cuelga', ' traba ', ' trabo ', ' veloz', ' abiertas', ' congela ']
                      # 'pesadas', 'pesados'],  # No incluiria:  (1) Pocas menciones: [lag, laguea/o/an, unisoc, bionic, gaming, simultaneo, snp] (2) Otros significados: [reinicia, apaga, core/s (modelo), streaming (uso), gamer(uso), a la vez (varios), respuesta (de vendedor), funciona rapido (gral), se cierra , cierra/n, responde (so y gral), tarda] ; [mediatek, jugar] (siempre acompañada de otra palabra relacionada)   # 'procesa' incluye 'porcesador' y 'procesamiento'.  # rapido no tiene asociado sentiment alto.. perjudica cuando dicen "es rapidp", ' fluid' # calent incluye calento, sobrecalento, calentarse, recalentar
         }

    # TV
    d2 = {'control': [' control ', ' boton', ' teclado ', 'voz'],  # No incluiria: (1) Pocas menciones: manos libres, assistant, alexa, asistente
        'conexion': ['conexion', ' entrada' , 'conectividad', 'conecta', 'wifi', 'internet', 'ethernet', 'bluetooth', ' puerto'],
        'diseño': ['diseño', 'estetic', ' terminacion', 'material', 'construc', ' patas ', ' fragil', 'elegante',
                   'delgad', ' borde', ' marco'],  # No incluiria: (1) Pocas menciones: feo/a, resisten(te/ncia), robusta/o, curvo/a, acabado, fachero/a, grueso/a. (2) Otros significados:                  # 'belleza ', ' bello ', 'bonito ', 'hermoso', --> muy grrales como 'lindo' ; [lindo (en gral), feo (varios), tacto (pant), agarre (detectar), aspecto (aspectos), cristal (otro), mate (otro), vidrio (protector), rompio (otro), atractivo(otro), compacto (tamaño)] (Otros significados)
        'imagen': [' imagen ', ' se ve ', 'definicion', 'pantalla ', ' 4k ', ' colores ', ' hd ', 'resolucion', ' hdr ',
                   ' contraste ', ' brillo '],  # No incluiria: (1) Pocas menciones: 8k, refresco
        'precio': ['precio', ' marca ', ' costo ', ' barat', ' caro ', ' gastar'],  # No incluria: (1) Pocas menciones: dolar/es, euro/s, carisimo, gasto/a, economico/a. (2) Otros significados: sale (sonido), vale (pena), cuesta (tilda), pesos (compara), plata (varios y poco frec), dinero (varios y poco frec)         # caro y barato son ADJ pero siempre se refieren al SUST precio # No uso l_marcas pues hay mas FP # "marcas" incluye muchos FP (comparaciones de otros aspectos con otras marcas)
        'sistema': ['sistema ', ' facil ', 'aplicaciones', ' app', 'software', 'funciones', 'funcionalidades', 'interfaz',
                    'interface', 'actualizaciones', ' so ', 'compartir', 'transmitir', 'duplicar', 'descargar'] + l_sistemas_operativos, # No incluiria (1) Pocas menciones: share, preinstalada (2) Otros significados: smart (tv)        # + l_apps? (OJO CON FP CON INTERNET) + rapid + lent + instalar (ojo con FP de instalar el tv fisicamente)+   # No incluiria: [opciones de configuracion] (Pocas menciones) 'configuracion', 'configurar'
        'sonido': ['sonido', ' audio ', 'volumen', 'escucha ', ' parlante', ' suena'],  # No incluria: (1) Pocas menciones: altavoz, home-theater
        'tamaño': ['tamaño ', ' livian', ' grande ', ' gigante', 'pulgadas'],  # No incluiria: (1) Pocas menciones: peso, pesado/a, dimensiones, ancho, enorme, compacta/o. (2) Otros significados:
        'velocidad': ['velocidad', 'rapido', 'netflix', 'youtube', 'disney', 'lento', ' fluid', 'funcionamiento',
                      ' tilda', 'agil', 'rapidez', ' lentitud ', ' cuelga', ' traba ', ' veloz'],   # Pocas menciones: procesamiento
    }

    # AURICULARES
    d3 = {# 'agua': [' agua ', 'agua,', 'agua.' 'sumergi'], #  no incluyo bañar (VERB)
        'bateria': ['bateria', ' autonomia'],  # No incluiria: [cargador, carga, cargar, turbo] (hablan de tiempo de carga en lugar de duracion de bateria) ; [duracion, dura, ahorro] (siempre acompañados del termino "bateria") ; juegos (muy frecunete a la altura de bateria, taparia rdos), [pila, mah] (Pocas menciones)
        'bluetooth': ['bluetooth', 'inalambrico'],  # en auris podria usar (pero no en tv pues se mezcla con conexion a internet): ['conexion ', ' empareja', ' sincroniz', ' vincula', ' desconect', ' conectar '],
        'conexion': ['conexion', 'conectividad', 'conecta', 'wifi', 'internet', 'ethernet', 'bluetooth'],
        'diseño': ['diseño', 'estetic', ' terminacion', 'material', 'construc', 'resisten', ' patas ', ' fragil',
                   'robust', 'elegante', ' curvo', 'curvatura', 'plastico ', ' acabado', ' facher', 'delgad',
                   ' grueso '],  # 'belleza ', ' bello ', 'bonito ', 'hermoso', --> muy grrales como 'lindo' # No incluiria: [grip, aluminio, metal, golpe, resbaladizo, texturada] (Pocas menciones) ; [lindo (en gral), feo (varios), tacto (pant), agarre (detectar), aspecto (aspectos), cristal (otro), mate (otro), vidrio (protector), rompio (otro), atractivo(otro), compacto (tamaño)] (Otros significados)
         'microfono': ['microfono', ' micro ', ' mic '],
        'oreja': [' oreja', 'cabeza', 'comodo', 'comodidad ', 'almohadillas', ' gomas ', ' oido', 'diseño'],
        'precio': ['precio', ' marca ', ' costo ', ' caro ', ' barat', ' economic', 'carisim', ' gastar', ' plata ',
                   ' dinero'],  # Muy pocas menciones para ver si incluir: dolares, euros  # No incluiria: sale,  vale, cuesta, gasto/a, pesos, # caro y barato son ADJ pero siempre se refieren al SUST precio # No uso l_marcas pues hay mas FP # "marcas" incluye muchos FP (comparaciones de otros aspectos con otras marcas)
        'ruido': [' ruido', 'cancelacion', ' aisla', 'noise cancelling'],
        'sonido': ['sonido', ' audio ', 'volumen', 'escucha ', ' parlante', ' suena', ' altavo'],  # No incluria: [peliculas, agudos, auditivamente] (Pocas menciones) ; [graves (problema), auriculares (si trae o no), musica (uso)] (Otro significado) ; [dolby] (siempre acomapañado de 'sonido') # ojo con escucha que no debe incluir escuchar # altavo incluye altavoz y altavoces
        'tamaño': ['tamaño ', ' peso ', 'pesado ', 'pesada ', ' livian', ' grande ', 'dimensiones', ' ancho ',
                   ' gigante', 'pulgadas', ' compact'],  # No incluiria: [pequeño (diseño), bolsillo (caidas), ligero (velocidad)] (Otros significados)    , 'pesa', ' comod', 'incomod', 'mano', largo, alto, angosto, armatoste, enorme (muy pocas veces se ref a tamaño, y las que lo hacen se pueden salvar) # pense en agregar "pulgadas" pero no se refieren a si es chico o gde. # Pongo 'pesado ' porque pesados se refiere a juegos pesados.
    }

    # NOTEBOOK

    # SMARTBAND
    d4 = {'conecta': ['conect', 'conexion', 'sincroniz', 'vincul', ' alcance '],  # No incluiria: (1) Pocas mencionas: emparejar, enlazar, asociar (2) Otros significados: bluetooth (duracion de bat x tenerlo prendido)
          'bateria': ['bateria', ' dura ', 'autonomia'],
        'diseño': ['diseño', ' malla', ' agua ', ' sumerg', 'estetic', ' terminacion', 'material', 'resisten', 'elegante',
                   'plastico ', ' facher', ' correa',  ' fragil', 'construc'], # No incluiria: (1) Pocas menciones: grueso, delgad, acabado, robust
        'facil': [' facil ', 'configurar', 'configuracion', 'intuitiv', 'personaliz'] + l_sistemas_operativos,  # opciones (se ref a cant de opciones)
        'funciones': ['funciones', 'pasos', 'notificacion', 'sueño',' gps ', 'presion', 'mensajes', 'musica', 'oxigeno',
                      'cardiac', 'llamada', 'pulsacion', 'medicion', ' mide ', 'precis', 'caloria', 'sensor', 'actividad',
                      'entrenamiento', 'ejercicio', 'deporte', 'deportiv', ' sangre ', 'funcionalidad'],  # ritmo?, No incluiria: opciones
        'pantalla': [' pantalla ', 'se ve', 'tamaño', 'brillo'] + l_pantallas,
        'precio': ['precio', ' costo ', ' caro ', ' barat', ' economic', ' gastar', ' plata ', ' dinero'],  # Muy pocas menciones para ver si incluir: dolares, euros  # No incluiria: sale,  vale, cuesta, gasto/a, pesos, # caro y barato son ADJ pero siempre se refieren al SUST precio # No uso l_marcas pues hay mas FP # "marcas" incluye muchos FP (comparaciones de otros aspectos con otras marcas)
    }

    # FUNDAS DE CELULAR

    d_prod = {'celulares': d1, 'tv': d2, 'auriculares': d3, 'smartband': d4}

    return d_prod[producto]

def get_dict_avoid(producto):
    # Palabras a evitar por palabra relacionada!

    # CELULARES
    d1 = {'precio': ['precioso'],   # estaria bueno agregar l_marcas en pal rel y avoid [' compara', 'vengo', 'venia', 'viejo', 'mejor', 'tenia', ' cambia', 'anterior', 'hace', 'superior', ' pase ', ' mas '] PERO cada marca deberia ser una key en este diccionario avoidiando cada palabra de la lista anterior... # cambia incluye cambiado y cambiar. Compara incluye comparado y comparar # No incluiria: 'por el precio' # agregar l_marcas y evitar
          'caro': [' mas '],  # "Compren otro mas caro"

          # Camara
          'camara': [' gcam '],  # gcam es app que mejora calidad de fotos
          'fotos': [' uso ', ' sacar ', ' tomar ', 'documento', ' gcam ', ' editar '],
          'definicion': ['pantalla'],

          # Pantalla
          'pantalla': ['tamaño', 'protector', 'huella', ' fondo', 'pantalla completa', 'todo pantalla', ' grande ', ' chica ',
                       'pequeñ', 'gigante', 'sucia ', 'borde', ' curva', ' plana ', 'cayo', ' caida', 'rompio',' raya',
                       'funda', ' film ', ' rompe ', ' negra ', ' negro ', 'gorila glass', 'gorilla glass', ' gesto', ' consum', ' edge '], # (se puso la pantalla negra...), # huella  #Cuando... (cuenta historia de que se pone negra/azul la pantalla)
          'resolucion': ['camara', 'fotos'],
          'imagen': ['fotos', ' camara'],

          # Velocidad
          'rendimiento': ['bateria'],
          'rapido': [' carga ', 'cargador', 'huella', 'solucion', ' llega ', ' viene '],  # predictivo (teclado)
          'lento': [' carga ', 'cargador', 'huella', 'internet'],
          'juegos': ['no lo uso'],

          # Memoria
          'memoria': [' ram ', 'microsd', ' sd ', ' extra ', 'expandible', ' tarjeta ', 'externa', 'extraíble'],  # No incluiria: ocupa
          'espacio': ['tarjeta', ' sd ', ' sim ', 'teclado'],
          'capacidad': ['bateria', 'tarjeta', ' sd ', ' sim '],

          # Sistema operativo
          'funciones': [' cumple ', 'probando', ' redes '],
          'facil': [' livian'],
          'practico': ['huella'],

          # Tamaño
          'grande': ['diferencia', 'presupuesto', 'bateria', ' gente ', ' señor', 'persona', 'numero', ' tecla', ' boton'],
          'comodo': ['huella'],

          # Sonido
          'volumen': [' boton'],

          # Bateria
          'bateria': ['extraible', 'calienta', 'calent'],  # No incluiria: gasta (habla de duracion)
          }

    # TV
    d2 = {'precio': ['precioso'],   # estaria bueno agregar l_marcas en pal rel y avoid [' compara', 'vengo', 'venia', 'viejo', 'mejor', 'tenia', ' cambia', 'anterior', 'hace', 'superior', ' pase ', ' mas '] PERO cada marca deberia ser una key en este diccionario avoidiando cada palabra de la lista anterior... # cambia incluye cambiado y cambiar. Compara incluye comparado y comparar # No incluiria: 'por el precio' # agregar l_marcas y evitar
          'caro': [' mas '],

          # Control remoto
          'control': ['trae', 'pilas'], # código, voz? por 'control por voz'
          'boton': ['comprar'],
          'teclado': ['inalambrico'],

          # Pantalla
          'pantalla': ['duplicar', 'transmitir', 'compartir', 'bordes', ' marco', ' negra ', ' azul ', ' verde ', ' caida', ' romp'],

          # Sistema
          'facil': ['instalar', 'armar', 'colgar', 'transportar'],
          'funciones': ['cumple'],

          # Velocidad
          'netflix': ['chromecast', 'conexion', 'internet', 'se ve'],
          'youtube': ['chromecast', 'conexion', 'internet', 'se ve'],
          'disney': ['chromecast', 'conexion', 'internet', 'se ve'],
          'rapido': ['control', 'conecta'],
          'lento': ['control', 'conecta'],

          # Diseño
          'diseño': ['control'],

          # Tamaño
          'tamaño': ['ideal para', 'control', 'cocina', 'comedor', 'cuarto', 'dormitorio', 'habitacion', 'living'],  #  ideal para pequeños lugares
          'grande': ['control', 'comedor'],
          # 'pesada': ['app'],
          }

    # SMARTBAND
    d4 = {'precio': ['precioso'],
          'caro': [' mas '],
          'barato': [' mas '],

          # Bluetooth
          'conect': ['cargador', ' conectado '],

          # Facil
          'facil': ['sincron', 'conecta', ' leer '],

          # Funciones
          'funciones': [' cumple', ' uso ', 'activ'],  # No incluiria: 'carga', 'bateria', dura (con activa y aevito FP con bateria)
          # Cada funcion y 'carga', 'bateria'
          'pasos': ['carga', 'bateria', ' fondo'],
          'sueño': ['carga', 'bateria'],
          ' gps ': ['carga', 'bateria'],
         'presion': ['carga', 'bateria'],
         'musica': ['carga', 'bateria'],
         'oxigeno': ['carga', 'bateria'],
         'cardiac': ['carga', 'bateria'],
         'medicion': ['carga', 'bateria'],
         # ' mide ': ['carga', 'bateria'],
         'caloria': ['carga', 'bateria', ' fondo'],
         'sensor': ['carga', 'bateria', 'activ'],
         'actividad': ['carga', 'bateria'],
         'entrenamiento': ['carga', 'bateria'],
          'ejercicio': ['carga', 'bateria'],
          'deporte': ['carga', 'bateria'],
          'deportiv': ['carga', 'bateria'],
          ' sangre ': ['carga', 'bateria'],
          'notificacion': ['pantalla', ' se ve', 'carga', 'bateria'],  # activar
          'mensajes': ['pantalla', 'carga', 'bateria', 'vibracion'],

          # Pantalla
          'pantalla': ['protector', ' fondo', ' proteg', 'activa', ' prende', 'muñeca', 'sucia ', 'cayo', ' caida',
                       'rompio', ' raya', 'funda', ' film ', ' rompe ', ' negra ', ' consum', ' tilda'], # agua? prendida
          'se ve': ['se ve que', 'como'],
          'brillo': ['bateria', 'dura'],

          # Diseño
          'agua': ['tomar agua'],
          'malla': ['repuesto', 'adicional', 'extra', 'alternativa', 'color'],
          'correa': ['repuesto', 'adicional', 'extra', 'alternativa', 'color'],
          }

    d_prod = {'celulares': d1, 'tv': d2, 'smartband': d4}

    return d_prod[producto]




'''
def main(df_alt):
    # Inicializo diccionario
    d_rel_words = get_dict_related_words(df_alt)

    """
    # Imprimo diccionario por terminal
    for cust_need in d_rel_words.keys():
        print("Palabra: ", cust_need, "Relacionadas:", d_rel_words[cust_need])
    """

    # Exporto diccionario
    with open("d_rel_words.pkl", "wb") as tf:
        pickle.dump(d_rel_words, tf)
'''

''' Prueba
df_alt = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/auriculares/df_alt.xlsx')
main(df_alt)
'''

'''
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
'''



'''
    d = {  # 'agua': [' agua ', 'agua,', 'agua.' 'sumergi'], #  no incluyo bañar (VERB)
        'bateria': ['bateria', ' autonomia'],
        # No incluiria: [cargador, carga, cargar, turbo] (hablan de tiempo de carga en lugar de duracion de bateria) ; [duracion, dura, ahorro] (siempre acompañados del termino "bateria") ; juegos (muy frecunete a la altura de bateria, taparia rdos), [pila, mah] (Pocas menciones)
        'bluetooth': ['bluetooth', 'inalambrico'],
        # en auris podria usar (pero no en tv pues se mezcla con conexion a internet): ['conexion ', ' empareja', ' sincroniz', ' vincula', ' desconect', ' conectar '],
        'camara': [' camara', ' fotos', 'definicion', ' selfie', ' filma', ' flash ', 'estabiliza', ' lente',
                   'fotografi'],
        # No incluiria: [hdr,  optico/a] (pocas menciones como para ver si agregar) ; [delantera, frontal, trasera, megapixeles, mp, grabacion, reflex, enfoque, luz] (siempre acompañados del termino 'camara'); [imagen (pant), zoom (app), foto (pub), grabar (audios),  video/s (video prop), imagenes (varios), luminosidad (pant)] (Otros significados) ; [gcam] (no se refieren a calidad de camara base) ;  # foto no pues si se refiere a la camara es "fotos". foto se confunde con la foto de la publicacion.. # filma incluye filmar, filmacion, filmaciones. # fotografi incluye fotografia/s fotografica
        'control': [' control ', ' boton', ' teclado '],
        'conexion': ['conexion', 'conectividad', 'conecta', 'wifi', 'internet', 'ethernet', 'bluetooth'],
        # 'diseño': ['diseño', 'estetic', 'terminacion', 'material', 'construc', 'resisten', 'gorila glass', 'gorilla glass',' fragil', 'robust', ' caida', 'elegante', ' curvo', 'curvatura', ' cayo ', 'plastico ', ' moja',' acabado', ' facher', ' sobresale', 'delgad', ' ergonom', ' grueso ', ' pliega', ' patas '],  # 'belleza ', ' bello ', 'bonito ', 'hermoso', --> muy grrales como 'lindo' # No incluiria: [grip, aluminio, metal, golpe, resbaladizo, texturada] (Pocas menciones) ; [lindo (en gral), feo (varios), tacto (pant), agarre (detectar), aspecto (aspectos), cristal (otro), mate (otro), vidrio (protector), rompio (otro), atractivo(otro), compacto (tamaño)] (Otros significados)
        # Diseño para tv
        'diseño': ['diseño', 'estetic', 'terminacion', 'material', 'construc', 'resisten', ' patas ', ' fragil',
                   'robust', 'elegante', ' curvo', 'curvatura', 'plastico ', ' acabado', ' facher', 'delgad',
                   ' grueso '],
        # 'belleza ', ' bello ', 'bonito ', 'hermoso', --> muy grrales como 'lindo' # No incluiria: [grip, aluminio, metal, golpe, resbaladizo, texturada] (Pocas menciones) ; [lindo (en gral), feo (varios), tacto (pant), agarre (detectar), aspecto (aspectos), cristal (otro), mate (otro), vidrio (protector), rompio (otro), atractivo(otro), compacto (tamaño)] (Otros significados)

        'funciones': ['funciones', 'funcion', 'sensores', 'actividad', 'deporte', 'deportiv', 'entrenamiento',
                      'ejercicio'],
        # 'pasos', 'musica', 'llamada', 'pulso', 'mensajes', 'estres', 'relaja', 'cardiac', 'sueño', 'menstrual'],  # no incluyo 'pasos', 'distancia recorrida', 'cardiac', 'pulso', 'pulsaciones', 'gps' pues habla de la medicion precisa o no y no de si tiene tal sensor o no.
        'gps': ['gps'],
        'imagen': [' imagen ', 'pantalla ', 'definicion', 'resolucion', ' 4k ', ' hdr ', ' colores ', ' contraste ',
                   ' brillo ', 'refresco', ' 8k '] + l_pantallas,
        # 'materiales': ['materiales', 'material', 'construc'], # 'agarre', 'tacto', 'antideslizante', ' grip '],
        'memoria': ['memoria', 'interna', 'almacenamiento', ' espacio ', 'juegos', 'pesadas', 'pesados'],
        # No incluria: [sdd, disco, cant de apps] (Pocas menciones) ; [instalar (app y otro), varias apps (velocidad), descargar (varios), gb (ram), gigas (ram), aplicaciones (varios), hardware (gral)] (Otros significados) ; [sd, microsd] (no se refieren a tamaño de memoria base) ; [almacenar, 256, capacidad] (siempre acompañada de palabra relacionada)  juegos (muy frecuente a la altura de 'memoria', taparia rdos) juegos pesados (puede haber coment negativos por velocidad y no tiene que ver con memoria)
        'microfono': ['microfono', ' micro ', ' mic '],
        'oreja': [' oreja', 'cabeza', 'comodo', 'comodidad ', 'almohadillas', ' gomas ', ' oido', 'diseño'],
        'pantalla': [' pantalla ', ' imagen ', 'refresco', ' grafic', 'resolucion'] + l_pantallas,
        # No incluiria: [luminosidad, luz azul, iluminacion, 1080, 720, calidad de video, contraste, densidad] (pocas menciones) ; [hz] (No gano significativamente) ; [luz (camara), pantallas (otro), vista(varios), 4k (camara), pixeles (camara), nitidez (camara), tactil (responde), display (varios)] (Otros significados) ; [colores, definicion]  (siempre acompañados de 'pantalla') ; [brillo (como func el sensor de brillo autom)] (no se refieren a la calidad de la pantalla)    , display  # grafic incluye grafica/o/os/as
        'proteccion': ['proteccion', 'protege', 'protej', 'caid', 'cubre ', 'cubrir', 'resiste', 'reforzada', 'cayo',
                       'golpes'],  # bordees?
        'precio': ['precio', ' marca ', ' costo ', ' caro ', ' barat', ' economic', 'carisim', ' gastar', ' plata ',
                   ' dinero'],
        # Muy pocas menciones para ver si incluir: dolares, euros  # No incluiria: sale,  vale, cuesta, gasto/a, pesos, # caro y barato son ADJ pero siempre se refieren al SUST precio # No uso l_marcas pues hay mas FP # "marcas" incluye muchos FP (comparaciones de otros aspectos con otras marcas)
        'ruido': [' ruido', 'cancelacion', ' aisla', 'noise cancelling'],
        'señal': [' señal ', 'datos moviles', ' recepcion', ' antena', ' cobertura', ' 2g ', ' 3g ', ' 4g ', ' lte '],
        # No inluiria: [rural] (Pocas menciones) ; [5g (modelo), datos (datos prop)] (Otros significados)
        # 'sistema': ['sistema ', 'software', 'funciones', 'funcionalidades', 'interfaz', 'interface', 'actualizaciones', ' so ', 'preinstal'] + l_sistemas_operativos, # Veer si agrego: configura # No incluiria: [operativo] (siempre acompañada de 'sistema') ; [imcompatible] (Pocas menciones) ; [funcion (varios), de usar (varios), actualizar (modelo), actualizacion (varios)]   (Otro significado)
        # Sistema para tv
        'sistema': ['sistema ', 'software', 'funciones', 'funcionalidades', 'interfaz', 'interface', 'actualizaciones',
                    ' so ', 'preinstal', ' velocidad ', ' app', 'aplicaciones', 'respuesta', 'compartir', ' share ',
                    'transmitir', 'duplicar', 'descargar', ' tilda ', 'facil de configurar'] + l_sistemas_operativos,
        # + l_apps? (OJO CON FP CON INTERNET) + rapid + lent + instalar (ojo con FP de instalar el tv fisicamente)+   # No incluiria: [opciones de configuracion] (Pocas menciones) 'configuracion', 'configurar'
        'sonido': ['sonido', ' audio ', 'volumen', 'escucha ', ' parlante', ' suena', ' altavo'],
        # No incluria: [peliculas, agudos, auditivamente] (Pocas menciones) ; [graves (problema), auriculares (si trae o no), musica (uso)] (Otro significado) ; [dolby] (siempre acomapañado de 'sonido') # ojo con escucha que no debe incluir escuchar # altavo incluye altavoz y altavoces
        'tamaño': ['tamaño ', ' peso ', 'pesado ', 'pesada ', ' livian', ' grande ', 'dimensiones', ' ancho ',
                   ' gigante',
                   'pulgadas', ' compact'],
        # No incluiria: [pequeño (diseño), bolsillo (caidas), ligero (velocidad)] (Otros significados)    , 'pesa', ' comod', 'incomod', 'mano', largo, alto, angosto, armatoste, enorme (muy pocas veces se ref a tamaño, y las que lo hacen se pueden salvar) # pense en agregar "pulgadas" pero no se refieren a si es chico o gde. # Pongo 'pesado ' porque pesados se refiere a juegos pesados.
        'video': ['video', ' placa ', 'juego', 'tarjeta grafica'],
        # https://www.xataka.com/basics/tarjeta-grafica-que-que-hay-dentro-como-funciona
        'velocidad': ['velocidad', ' rapid', ' lento ', ' fluid', 'juegos', ' lentitud ', 'procesador', 'procesamiento',
                      ' ram ', 'funcionamiento', 'snapdragon', 'exynos', 'calienta', 'calent', 'temperatura', ' avion ',
                      ' vuela ', ' nave ', ' potencia ', 'abren y cierran', ' corre ', ' cuelga', ' tilda', ' traba ',
                      ' trabo ', 'rendimiento', 'mismo tiempo', ' veloz', ' abiertas', ' congela ', 'pesadas',
                      'pesados'],
        # No incluiria:  [lag, laguea/o/an, unisoc, bionic, gaming, simultaneo, snp] (Pocas menciones) ; [reinicia, apaga, core/s (modelo), streaming (uso), gamer(uso), a la vez (varios), respuesta (de vendedor), funciona rapido (gral), se cierra , cierra/n, responde (so y gral), tarda] (Otros significados) ; [mediatek, jugar] (siempre acompañada de otra palabra relacionada)   # 'procesa' incluye 'porcesador' y 'procesamiento'.  # rapido no tiene asociado sentiment alto.. perjudica cuando dicen "es rapidp", ' fluid' # calent incluye calento, sobrecalento, calentarse, recalentar
        'voz': ['voz', 'assistant', 'alexa']
    }
'''