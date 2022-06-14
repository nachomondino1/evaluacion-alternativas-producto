import pickle
import pandas as pd

def get_dict_related_words(producto):

    # Defino palabras relacionadas a algunas caracteristicas especificas   # deberia definirlos automaticamente segun valores unicos de atrib del producto?
    # l_marcas = get_marcas(df_alt)  # falla en smartband dado que no queda el atrib marca en df_alt_cleaned.

    # ojo con incluir ADJ o VERB dado que asi como se pueden usar para un sustantivo se pueden usar para otros. Por ej, 'grande' puede ser para 'tamaño' asi como puede ser 'el inconveniente mas grande es...'
    # Poner palabras relacionadas con mayor frecuencia primero para ser mas eficiente en tiempo (hace break antes)

    # Defino diccionario de palabras relacionadas para mejorar identificacion de customer needs

    # CELULARES
    l_sistemas_operativos = ['android', 'blackberry os', ' ios ', ' ginga ', ' kaios ', 'kaistore', ' miui ', #'nokia',
                             'threadx', ' tizen ', 'linux' 's30 +', ' saphi ', ' oreo ', ' vidaa' ' xmart ui',
                             'windows phone', ' webos ']
    # l_apps = ['whatsapp', 'facebook', 'instagram', 'tik tok', 'redes', 'youtube', 'amazon', ' flow', 'disney', 'prime ', 'netflix', 'spotify', ' hbo ', 'navegador', 'browser', 'star']
    # l_juegos = ['call of duty', 'asphalt', 'royale', 'cod mobile', ' fifa ', 'genshin impact'] # clash of clans, pokemon go, free fire, fortnite
    l_pantallas = [' amoled ', ' lcd ', ' hd ', ' ips ', ' oled ', ' pls ', ' tft ']

    d1 = {'bateria': ['bateria', ' autonomia'],  # No incluiria: [cargador, carga, cargar, turbo] (hablan de tiempo de carga en lugar de duracion de bateria) ; [duracion, dura, ahorro] (siempre acompañados del termino "bateria") ; juegos (muy frecunete a la altura de bateria, taparia rdos), [pila, mah] (Pocas menciones)
        'camara': [' camara', ' fotos', 'definicion', ' selfie', ' filma', ' flash ', 'estabiliza', ' lente', 'fotografi'], # No incluiria: [hdr,  optico/a] (pocas menciones como para ver si agregar) ; [delantera, frontal, trasera, megapixeles, mp, grabacion, reflex, enfoque, luz] (siempre acompañados del termino 'camara'); [imagen (pant), zoom (app), foto (pub), grabar (audios),  video/s (video prop), imagenes (varios), luminosidad (pant)] (Otros significados) ; [gcam] (no se refieren a calidad de camara base) ;  # foto no pues si se refiere a la camara es "fotos". foto se confunde con la foto de la publicacion.. # filma incluye filmar, filmacion, filmaciones. # fotografi incluye fotografia/s fotografica
        'diseño': ['diseño', 'estetic', 'terminacion', 'material', 'construc', 'resisten', 'gorila glass', 'gorilla glass',
                   ' fragil', 'robust', ' caida', 'elegante', ' curvo', 'curvatura', ' cayo ', 'plastico ', ' moja',
                   ' acabado', ' facher', ' sobresale', 'delgad', ' ergonom', ' grueso ', ' pliega'],  # 'belleza ', ' bello ', 'bonito ', 'hermoso', --> muy grales como 'lindo' # No incluiria: [grip, aluminio, metal, golpe, resbaladizo, texturada] (Pocas menciones) ; [lindo (en gral), feo (varios), tacto (pant), agarre (detectar), aspecto (aspectos), cristal (otro), mate (otro), vidrio (protector), rompio (otro), atractivo(otro), compacto (tamaño)] (Otros significados)
        'memoria': ['memoria', 'interna', 'almacenamiento', ' espacio ', 'juegos'],  #'pesadas', 'pesados'],  # No incluria: [sdd, disco, cant de apps] (Pocas menciones) ; [instalar (app y otro), varias apps (velocidad), descargar (varios), gb (ram), gigas (ram), aplicaciones (varios), hardware (gral)] (Otros significados) ; [sd, microsd] (no se refieren a tamaño de memoria base) ; [almacenar, 256, capacidad] (siempre acompañada de palabra relacionada)  juegos (muy frecuente a la altura de 'memoria', taparia rdos) juegos pesados (puede haber coment negativos por velocidad y no tiene que ver con memoria)
        'pantalla': [' pantalla ', ' imagen ', 'refresco', ' grafic', 'resolucion'] + l_pantallas,  # No incluiria: [luminosidad, luz azul, iluminacion, 1080, 720, calidad de video, contraste, densidad] (pocas menciones) ; [hz] (No gano significativamente) ; [luz (camara), pantallas (otro), vista(varios), 4k (camara), pixeles (camara), nitidez (camara), tactil (responde), display (varios)] (Otros significados) ; [colores, definicion]  (siempre acompañados de 'pantalla') ; [brillo (como func el sensor de brillo autom)] (no se refieren a la calidad de la pantalla)    , display  # grafic incluye grafica/o/os/as
        'precio': ['precio', ' marca ', ' costo ',  ' caro ', ' barat', ' economic', 'carisim', ' gastar', ' plata ',
                   ' dinero'],  # No incluiria: (1) Pocas menciones: dolares, euros (2) Muchos significados: gasto/a (bateria), vale (pena), sale (varios), cuesta (entender), pesos (varios) # caro y barato son ADJ pero siempre se refieren al SUST precio # No uso l_marcas pues hay mas FP # "marcas" incluye muchos FP (comparaciones de otros aspectos con otras marcas)
         'señal': [' señal ', 'datos moviles', ' recepcion', ' antena', ' cobertura', ' 2g ', ' 3g ', ' 4g ', ' lte '],  # No inluiria: [rural] (Pocas menciones) ; [5g (modelo), datos (datos prop)] (Otros significados)
        'sistema': ['sistema ', 'software', 'funciones', 'funcionalidades', 'interfaz', 'interface', 'actualizaciones', ' so ', 'preinstal'] + l_sistemas_operativos, # Veer si agrego: configura # No incluiria: [operativo] (siempre acompañada de 'sistema') ; [imcompatible] (Pocas menciones) ; [funcion (varios), de usar (varios), actualizar (modelo), actualizacion (varios)]   (Otro significado)
        'sonido': ['sonido', ' audio ', 'volumen', 'escucha ', ' parlante', ' suena', ' altavo'], # No incluria: [peliculas, agudos, auditivamente] (Pocas menciones) ; [graves (problema), auriculares (si trae o no), musica (uso)] (Otro significado) ; [dolby] (siempre acomapañado de 'sonido') # ojo con escucha que no debe incluir escuchar # altavo incluye altavoz y altavoces
         'tamaño': ['tamaño ', ' peso ', 'pesado ', 'pesada ', ' livian', ' grande ', 'dimensiones', ' ancho ', ' gigante',
                    'pulgadas', ' compact'],  # No incluiria: [pequeño (diseño), bolsillo (caidas), ligero (velocidad)] (Otros significados)    , 'pesa', ' comod', 'incomod', 'mano', largo, alto, angosto, armatoste, enorme (muy pocas veces se ref a tamaño, y las que lo hacen se pueden salvar) # pense en agregar "pulgadas" pero no se refieren a si es chico o gde. # Pongo 'pesado ' porque pesados se refiere a juegos pesados.
        'velocidad': ['velocidad', ' rapid', ' lento ', ' fluid', 'juegos', ' lentitud ', 'procesador', 'procesamiento',
                      ' ram ', 'funcionamiento', 'snapdragon', 'exynos', 'calienta', 'calent', 'temperatura', ' avion ',
                      ' vuela ', ' nave ', ' potencia ', 'abren y cierran', ' corre ', ' cuelga', ' tilda', ' traba ',
                      ' trabo ', 'rendimiento', 'mismo tiempo', ' veloz', ' abiertas', ' congela ', 'pesadas', 'pesados'],  # No incluiria:  [lag, laguea/o/an, unisoc, bionic, gaming, simultaneo, snp] (Pocas menciones) ; [reinicia, apaga, core/s (modelo), streaming (uso), gamer(uso), a la vez (varios), respuesta (de vendedor), funciona rapido (gral), se cierra , cierra/n, responde (so y gral), tarda] (Otros significados) ; [mediatek, jugar] (siempre acompañada de otra palabra relacionada)   # 'procesa' incluye 'porcesador' y 'procesamiento'.  # rapido no tiene asociado sentiment alto.. perjudica cuando dicen "es rapidp", ' fluid' # calent incluye calento, sobrecalento, calentarse, recalentar
         }

    # TV
    d2 = {'control': [' control ', ' boton', ' teclado '],
        'conexion': ['conexion', 'conectividad', 'conecta', 'wifi', 'internet', 'ethernet', 'bluetooth'],
        'diseño': ['diseño', 'estetic', 'terminacion', 'material', 'construc', 'resisten', ' patas ', ' fragil',
                   'robust', 'elegante', ' curvo', 'curvatura', 'plastico ', ' acabado', ' facher', 'delgad', ' grueso '],  # 'belleza ', ' bello ', 'bonito ', 'hermoso', --> muy grrales como 'lindo' # No incluiria: [grip, aluminio, metal, golpe, resbaladizo, texturada] (Pocas menciones) ; [lindo (en gral), feo (varios), tacto (pant), agarre (detectar), aspecto (aspectos), cristal (otro), mate (otro), vidrio (protector), rompio (otro), atractivo(otro), compacto (tamaño)] (Otros significados)
        'imagen': [' imagen ', 'pantalla ', 'definicion', 'resolucion', ' 4k ', ' hdr ', ' colores ', ' contraste ',
                   ' brillo ', 'refresco', ' 8k '] + l_pantallas,
        'precio': ['precio', ' marca ', ' costo ', ' caro ', ' barat', ' economic', 'carisim', ' gastar', ' plata ',
                   ' dinero'],  # Muy pocas menciones para ver si incluir: dolares, euros  # No incluiria: sale,  vale, cuesta, gasto/a, pesos, # caro y barato son ADJ pero siempre se refieren al SUST precio # No uso l_marcas pues hay mas FP # "marcas" incluye muchos FP (comparaciones de otros aspectos con otras marcas)
        'sistema': ['sistema ', 'software', 'funciones', 'funcionalidades', 'interfaz', 'interface', 'actualizaciones',
                    ' so ', 'preinstal', ' velocidad ', ' app', 'aplicaciones', 'respuesta', 'compartir', ' share ',
                    'transmitir', 'duplicar', 'descargar', ' tilda ', 'facil de configurar'] + l_sistemas_operativos,  # + l_apps? (OJO CON FP CON INTERNET) + rapid + lent + instalar (ojo con FP de instalar el tv fisicamente)+   # No incluiria: [opciones de configuracion] (Pocas menciones) 'configuracion', 'configurar'
        'sonido': ['sonido', ' audio ', 'volumen', 'escucha ', ' parlante', ' suena', ' altavo'],  # No incluria: [peliculas, agudos, auditivamente] (Pocas menciones) ; [graves (problema), auriculares (si trae o no), musica (uso)] (Otro significado) ; [dolby] (siempre acomapañado de 'sonido') # ojo con escucha que no debe incluir escuchar # altavo incluye altavoz y altavoces
        'tamaño': ['tamaño ', ' peso ', 'pesado ', 'pesada ', ' livian', ' grande ', 'dimensiones', ' ancho ',
                   ' gigante', 'pulgadas', ' compact'],  # No incluiria: [pequeño (diseño), bolsillo (caidas), ligero (velocidad)] (Otros significados)    , 'pesa', ' comod', 'incomod', 'mano', largo, alto, angosto, armatoste, enorme (muy pocas veces se ref a tamaño, y las que lo hacen se pueden salvar) # pense en agregar "pulgadas" pero no se refieren a si es chico o gde. # Pongo 'pesado ' porque pesados se refiere a juegos pesados.
        'voz': ['voz', 'assistant', 'alexa']
    }

    # AURICULARES
    d3 = {# 'agua': [' agua ', 'agua,', 'agua.' 'sumergi'], #  no incluyo bañar (VERB)
        'bateria': ['bateria', ' autonomia'],  # No incluiria: [cargador, carga, cargar, turbo] (hablan de tiempo de carga en lugar de duracion de bateria) ; [duracion, dura, ahorro] (siempre acompañados del termino "bateria") ; juegos (muy frecunete a la altura de bateria, taparia rdos), [pila, mah] (Pocas menciones)
        'bluetooth': ['bluetooth', 'inalambrico'],  # en auris podria usar (pero no en tv pues se mezcla con conexion a internet): ['conexion ', ' empareja', ' sincroniz', ' vincula', ' desconect', ' conectar '],
        'conexion': ['conexion', 'conectividad', 'conecta', 'wifi', 'internet', 'ethernet', 'bluetooth'],
        'diseño': ['diseño', 'estetic', 'terminacion', 'material', 'construc', 'resisten', ' patas ', ' fragil',
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

    # FUNDAS DE CELULAR

    d_prod = {'celulares': d1, 'tv': d2, 'auriculares': d3}

    return d_prod[producto]

def get_dict_avoid(producto):
    # Palabras a evitar por palabra relacionada!

    # CELULARES
    d1 = {'precio': ['precioso'],   # estaria bueno agregar l_marcas en pal rel y avoid [' compara', 'vengo', 'venia', 'viejo', 'mejor', 'tenia', ' cambia', 'anterior', 'hace', 'superior', ' pase ', ' mas '] PERO cada marca deberia ser una key en este diccionario avoidiando cada palabra de la lista anterior... # cambia incluye cambiado y cambiar. Compara incluye comparado y comparar # No incluiria: 'por el precio' # agregar l_marcas y evitar
          'caro': [' mas '],  # "Compren otro mas caro"

          # Camara
          'camara': ['gcam'],  # gcam es app que mejora calidad de fotos
          'fotos': ['documento', ' uso ', ' gcam ', ' editar '],
          'definicion': ['pantalla'],

          # Pantalla
          'pantalla': ['protector', 'tamaño', ' fondo', 'pantalla completa', 'todo pantalla', ' grande ',
                       ' chica ', 'pequeñ', 'gigante', 'sucia ', 'borde', ' curva', ' plana ', 'cayo', ' caida',
                       'rompio',' raya', 'funda', ' film ', ' rompe ', ' negra ', 'gorila glass', 'gorilla glass',
                       'gesto', ' consumo ', ' edge '], # (se puso la pantalla negra...), # huella  #Cuando... (cuenta historia de que se pone negra/azul la pantalla)
          'resolucion': ['camara'],
          'imagen': [' foto', ' camara'],

          # Velocidad
          'rendimiento': ['bateria'],
          'rapid': ['carga', 'cargador', 'huella', 'solucion', ' llega ', ' viene '],  # predictivo (teclado)
          'lento': ['carga', 'cargador', 'huella', 'internet'],
          'juegos': ['no lo uso'],

          # Memoria
          'memoria': [' ram ', 'microsd', ' sd ', ' extra ', 'expandible', ' tarjeta ', 'externa', 'extraíble'],  # No incluiria: ocupa
          'espacio': ['tarjeta', ' sd ', ' sim ', 'teclado'],

          # Sistema operativo
          'funciones': ['cumple', 'probando','redes'],

          # Tamaño
          'grande': ['diferencia', 'presupuesto'],

          # Señal
          'cobertura': ['garantia'],

          # Bateria
          'bateria': ['extraible', 'calienta', 'calent'],  # No incluiria: gasta (habla de duracion)
          }

    # TV
    d2 = {'precio': ['precioso'],   # estaria bueno agregar l_marcas en pal rel y avoid [' compara', 'vengo', 'venia', 'viejo', 'mejor', 'tenia', ' cambia', 'anterior', 'hace', 'superior', ' pase ', ' mas '] PERO cada marca deberia ser una key en este diccionario avoidiando cada palabra de la lista anterior... # cambia incluye cambiado y cambiar. Compara incluye comparado y comparar # No incluiria: 'por el precio' # agregar l_marcas y evitar
          'caro': [' mas '],

          # Control remoto
          'control': ['trae'], # código
          'boton': ['comprar'],
          'teclado': ['inalambrico'],

          'pesada': ['app'],

          # Conexion - Conectividad
          'conectar': ['entradas'],

          # Diseño
          'diseño': ['control'],

          # Tamaño
          'tamaño': ['ideal para', 'control', 'cocina', 'comedor', 'cuarto', 'dormitorio', 'habitacion', 'living'],  #  ideal para pequeños lugares
          'grande': ['comedor'],
          }

    d_prod = {'celulares': d1, 'tv': d2}

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

""" DEJO EL DICCIONARIO ANTES DE INTENTO 6 DE CELULARES (LA REVOLUCION)
   d = {# 'aplicaciones': ['aplicaciones', ' app', 'aplicacion', 'sistema smart', 'youtube', 'amazon', ' flow', 'disney', 'prime ', 'netflix', 'spotify', ' hbo ', 'navegador', 'browser', 'star'],  # Las apps propiamente se mencionan sin referirse a la cantidad de estas... -->'youtube', 'amazon', ' flow ', 'disney', 'prime ', 'netflix', 'spotify', 'google', ' hbo ', 'navegador'],  # 'sistema', 'operativo', 'android', ' so ', 'software'],  # 'internet'? # no usaria: ' smart'  3
        # 'aplicaciones': ['velocidad', 'procesador', 'procesamiento', ' ram ', ' ram,', 'funcionamiento', 'respuesta', 'cuelga', ' tilda', 'traba ', 'rendimiento', 'fluidez', 'reaccion', 'simultaneo', 'mismo tiempo', ' core ', 'cores', 'lentitud', 'rapidez', 'aplicaciones abiertas','apps abiertas'],  # 'veloz', ' rapid', ' lent', ' tilda', ' fluid', ' traba '],  #'aplicaciones', ' app', 'aplicacion', 'sistema smart',  # Las apps propiamente se mencionan sin referirse a la cantidad de estas... -->'youtube', 'amazon', ' flow ', 'disney', 'prime ', 'netflix', 'spotify', 'google', ' hbo ', 'navegador'],  # 'sistema', 'operativo', 'android', ' so ', 'software'],  # 'internet'? # no usaria: ' smart'  3
        'agua': [' agua ', 'agua,', 'agua.' 'sumergi'], #  no incluyo bañar (VERB)
        'bateria': ['bateria', 'duracion', ' carga ', ' autonomia', 'turbo power'],
        'bluetooth': ['bluetooth', 'inalambrico'],  #  en auris podria usar (pero no en tv pues se mezcla con conexion a internet): ['conexion ', ' empareja', ' sincroniz', ' vincula', ' desconect', ' conectar '],
        'camara': [' camara', ' fotos', 'frontal', 'trasera', 'imagenes', 'resolucion', 'selfie', 'filmar', 'zoom', 'flash'],  # no incluiria: definicon, videos 'selfie' # foto no pues si se refiere a la camara es "fotos". foto se confunde con la foto de la publicacion..
        'diseño': ['diseño', ' comod', 'incomod', 'estetica', 'terminacion', 'tamaño', ' peso ', 'material', 'construc', 'ergonom', 'resisten', 'dimensiones', 'largo', 'ancho', 'gorilla glass'],  # No incluiria: 'aspecto '  ADJ: ' pesad', ' livian' # En smartband:  considere tam y peso en materiales (tal vez podria llevarlo a diseño). # comod con esp al ppio por "acomodar"...
        'funciones': ['funciones', 'funcion', 'sensores', 'actividad', 'deporte', 'deportiv', 'entrenamiento', 'ejercicio'],  # 'pasos', 'musica', 'llamada', 'pulso', 'mensajes', 'estres', 'relaja', 'cardiac', 'sueño', 'menstrual'],  # no incluyo 'pasos', 'distancia recorrida', 'cardiac', 'pulso', 'pulsaciones', 'gps' pues habla de la medicion precisa o no y no de si tiene tal sensor o no.
        'gps': ['gps'],
        'imagen': [' imagen ', ' imagen,', 'definicion', 'colores', ' brillo', 'contraste', 'refresco', 'refresh', 'hz '] + l_pantallas,  # resolucion para tv
        # no incluiria: tactil (se refiere a vel con que responde), pantallas (se refiere a otros aspectos), display (no suele refereirse a calidad de pantalla), 'pantalla' (se refiere a velocidad del tactil, o como se ve algo en la pantalla, o el tamaño de la pantalla, o que se raya facil, o el protector de pantalla, etc)
        'juegos': [ 'juegos', 'jugar', 'jueguito', 'gamer ', 'gaming'] + l_juegos,  # No agregar pal rel de procesador, quiero saber como funciona en juegos para la gente
        # 'marca': ['marca'] + l_marcas,
        # 'materiales': ['materiales', 'material', 'construc'], # 'agarre', 'tacto', 'antideslizante', ' grip '],
        'memoria': ['memoria', 'interna', 'almacenamiento', 'espacio', 'capacidad', ' disco ', ' ssd '],  # no incluiria: lag. # inclui juegos porque necesitas espacio para tenerlos..
        'microfono': ['microfono', ' micro ', ' mic '],
        'oreja': [' oreja', 'cabeza', 'comodo', 'comodidad ', 'almohadillas', ' gomas ', ' oido', 'diseño'],
        # 'pantalla': [' imagen ', ' imagen,', ' brillo', 'definicion', 'colores', 'amoled', ' hd ', 'hz ', 'lcd', 'refresco', 'refresh', 'contraste'],  # no incluiria: tactil (se refiere a vel con que responde), pantallas (se refiere a otros aspectos), display (no suele refereirse a calidad de pantalla), 'pantalla' (se refiere a velocidad del tactil, o como se ve algo en la pantalla, o el tamaño de la pantalla, o que se raya facil, o el protector de pantalla, etc)
        'proteccion': ['proteccion', 'protege', 'protej', 'caid', 'cubre ', 'cubrir', 'resiste', 'reforzada', 'cayo', 'golpes'], # bordees?
        'precio': ['precio', 'marca ', 'marca,' 'costo', ' caro ', ' caro,', ' barat', 'carisim'],  # caro y barato son ADJ pero siempre se refieren al SUST precio # No uso l_marcas pues hay mas FP # "marcas" incluye muchos FP (comparaciones de otros aspectos con otras marcas)
        'ruido': [' ruido', 'cancelacion', ' aisla', 'noise cancelling'],
        'sistema': ['sistema', ' de usar', 'operativo', 'software', 'interfaz'] + l_sistemas_operativos,  # ' usar ' es un verb y como tal se usa para otros sustantivos.. pero 'de usar' engloba 'facil de usar', 'practico de usar', 'no es dificil de usar', etc. Tuve que sacar 'entender' y 'intuitivo'. Uso 'sistema' a pesar de que exista sistema de audio, etc pues a veces se menciona solo como sistema y deams permite ahorrar ['sistemas operativos', 'sistema operativo', 'sistema smart']
        'sonido': ['sonido', 'audio ', 'audio,', 'volumen', 'escucha', 'parlante', ' suena'],
         # 'tamaño': ['tamaño'],  # pense en agregar "pulgadas" pero no se refieren a si es chico o gde. ' peso ', ' pesad', ' livian'],  # en celulares usaria (pero no en tv)? no deberia tener relacion con el peso pues es exclusivante el tamaño de la pantalla y no del dispositivo
        'teclado': ['teclas', ' ñ '],
         # 'usar': [' de usar', 'sistema', 'operativo', 'software', 'interfaz'] + l_sistemas_operativos, # ' usar ' es un verb y como tal se usa para otros sustantivos.. pero 'de usar' engloba 'facil de usar', 'practico de usar', 'no es dificil de usar', etc. Tuve que sacar 'entender' y 'intuitivo'. Uso 'sistema' a pesar de que exista sistema de audio, etc pues a veces se menciona solo como sistema y deams permite ahorrar ['sistemas operativos', 'sistema operativo', 'sistema smart']
        'video': ['video', ' placa ', 'juego', 'tarjeta grafica'],  # https://www.xataka.com/basics/tarjeta-grafica-que-que-hay-dentro-como-funciona
        # 'velocidad': ['velocidad', 'procesa', ' ram ', ' ram,', 'funcionamiento', 'software', 'respuesta', 'juegos', 'gamer ', 'gaming', 'streaming', 'simultaneo', 'mismo tiempo', 'veloz', ' rapid', ' lent', ' tilda', ' fluid', ' traba '], # 'procesa' incluye 'porcesador' y 'procesamiento'.  # rapido no tiene asociado sentiment alto.. perjudica cuando dicen "es rapidp", ' fluid'
        'voz': ['voz', 'assistant', 'alexa']
         }
         
    DEJO DIC ANTES DE INTENTO 10 DE CELULARES DONDE AGREGUE D_TO_AVOID
    d = {# 'agua': [' agua ', 'agua,', 'agua.' 'sumergi'], #  no incluyo bañar (VERB)
         'bateria': ['bateria', 'duracion', ' carga ', ' autonomia', ' turbo'],
        'bluetooth': ['bluetooth', 'inalambrico'],  #  en auris podria usar (pero no en tv pues se mezcla con conexion a internet): ['conexion ', ' empareja', ' sincroniz', ' vincula', ' desconect', ' conectar '],
        'camara': [' camara', ' fotos', 'resolucion', ' selfie', ' filma', ' flash ', 'estabiliza', ' lente', 'fotografi'],  # no incluiria: imagen, grabar, delantera, frontal, video/s, foto, trasera, zoom, optico/a, definicon, videos, reflex, megapixelees, grabacion, mp, imagenes # foto no pues si se refiere a la camara es "fotos". foto se confunde con la foto de la publicacion.. # filma incluye filmar, filmacion, filmaciones. # fotografi incluye fotografia/s fotografica
        'diseño': ['diseño', 'estetic', 'terminacion', 'material', 'construc', 'resisten', 'gorila glass', 'gorilla glass', ' fragil', 'robust', ' cayo ', ' caida', 'plastico', 'hermoso', 'elegante', 'bonito ', ' moja', ' metal', ' acabado', ' ergonom', 'belleza ', ' bello ', ' curvo', 'curvatura', ' fachero', ' pliega', ' sobresale', 'delgado'],  # No incluiria: 'aspecto ', 'tacto', agarre,, resbaladizo, grip, golpe, rompio, lindo, feo, aluminio, vidrio, cristal, mate, atractivo
        'funciones': ['funciones', 'funcion', 'sensores', 'actividad', 'deporte', 'deportiv', 'entrenamiento', 'ejercicio'],  # 'pasos', 'musica', 'llamada', 'pulso', 'mensajes', 'estres', 'relaja', 'cardiac', 'sueño', 'menstrual'],  # no incluyo 'pasos', 'distancia recorrida', 'cardiac', 'pulso', 'pulsaciones', 'gps' pues habla de la medicion precisa o no y no de si tiene tal sensor o no.
        'gps': ['gps'],
        # 'imagen': [' imagen ', ' imagen,', 'pantalla ', 'definicion', ' 4k ', ' hdr '],
        # 'juegos': [ 'juegos', 'jugar', 'jueguito', 'gamer ', 'gaming'] + l_juegos,  # No agregar pal rel de procesador, quiero saber como funciona en juegos para la gente
        # 'materiales': ['materiales', 'material', 'construc'], # 'agarre', 'tacto', 'antideslizante', ' grip '],
        'memoria': ['memoria', ' interna ', 'almacenamiento', ' espacio ', ' capacidad', ' disco '],  # quito temporalmente a espera de rdos:  ' sd ', ' microsd ' # no incluiria: lag, sdd  # inclui juegos porque necesitas espacio para tenerlos..
        'microfono': ['microfono', ' micro ', ' mic '],
        'oreja': [' oreja', 'cabeza', 'comodo', 'comodidad ', 'almohadillas', ' gomas ', ' oido', 'diseño'],
        'pantalla': [' pantalla', 'refresco', 'hz ', ' grafic'] + l_pantallas,  # No incluiria: pantallas, imagen, pixeles, definicion, tactil, densidad, brillo, colores, refresh, vista, contraste, 4k, display   # resolucion para tv  # grafic incluye grafica/o/os/as
        'proteccion': ['proteccion', 'protege', 'protej', 'caid', 'cubre ', 'cubrir', 'resiste', 'reforzada', 'cayo', 'golpes'],  # bordees?
        'precio': ['precio', ' marca ', ' costo ',  ' caro ', ' barat', ' carisim'],  # caro y barato son ADJ pero siempre se refieren al SUST precio # No uso l_marcas pues hay mas FP # "marcas" incluye muchos FP (comparaciones de otros aspectos con otras marcas) # ojo con precioso en 'precio'
        'ruido': [' ruido', 'cancelacion', ' aisla', 'noise cancelling'],
         'señal': [' señal ', 'datos moviles', ' recepcion', ' antena', ' cobertura', ' 2g ', ' 3g ', ' 4g ', ' lte '], # no inluiria: 5g, datos, rural
        'sistema': ['sistema ', 'operativo', ' so ', 'software', 'interfaz', 'interface', 'actualizaciones'] + l_sistemas_operativos,  # No incluiria:  de usar, actualizar, actualizacion, terminos relacionados con tilderse
        'sonido': ['sonido', ' audio ', 'volumen', 'escucha ', ' parlante', ' suena', ' altavo'], # ojo con escucha que no debe incluir escuchar # altavo incluye altavoz y altavoces
         'tamaño': ['tamaño ', ' peso ', 'pesado ', 'liviano ', 'grande ', 'dimensiones', ' ancho ', ' gigante', 'pulgadas'],  # No incluiria: pequeño, 'pesa', ' comod', 'incomod', 'mano', bolsillo, largo, alto, angosto, armatoste, enorme (muy pocas veces se ref a tamaño, y las que lo hacen se pueden salvar) # pense en agregar "pulgadas" pero no se refieren a si es chico o gde. # Pongo 'pesado ' porque pesados se refiere a juegos pesados.
        'teclado': ['teclas', ' ñ '],
        'video': ['video', ' placa ', 'juego', 'tarjeta grafica'],  # https://www.xataka.com/basics/tarjeta-grafica-que-que-hay-dentro-como-funciona
        'velocidad': ['velocidad', 'procesador', 'procesamiento', ' ram ',  'funcionamiento', 'snapdragon', 'exynos', 'calienta', 'calent', 'temperatura', ' avion ', ' vuela ', ' nave ', ' potencia ', ' se cierra ', 'abren y cierran', ' responde ', ' corre ',  ' cuelga', ' tilda', ' traba ', ' trabo ', 'rendimiento', 'simultaneo', 'mismo tiempo', ' veloz', ' fluid', 'lentitud', 'rapidez', ' abiertas', ' congela '],  # No incluiria: juegos, respuesta, mediatek, unisoc, tarda, cierra/n, bionic, reinicia, apaga, jugar, core/s, gamer, gaming, streaming, funciona rapido   # 'procesa' incluye 'porcesador' y 'procesamiento'.  # rapido no tiene asociado sentiment alto.. perjudica cuando dicen "es rapidp", ' fluid' # calent incluye calento, sobrecalento, calentarse, recalentar
        'voz': ['voz', 'assistant', 'alexa']
         }
"""


'''
    # PRUEBA AGREGO USOS
    d = {# 'agua': [' agua ', 'agua,', 'agua.' 'sumergi'], #  no incluyo bañar (VERB)
         'bateria': ['bateria', ' autonomia', 'trabajar', ' jugar ', 'juegos', ' trabajar ', ' trabajo ', ' laburar', 'redes sociales'],  # No incluiria: [cargador, carga, cargar, turbo] (hablan de tiempo de carga en lugar de duracion de bateria) ; [duracion, dura, ahorro] (siempre acompañados del termino "bateria") ; juegos (muy frecunete a la altura de bateria, taparia rdos), [pila, mah] (Pocas menciones)
        'bluetooth': ['bluetooth', 'inalambrico'],  #  en auris podria usar (pero no en tv pues se mezcla con conexion a internet): ['conexion ', ' empareja', ' sincroniz', ' vincula', ' desconect', ' conectar '],
        'camara': [' camara', ' fotos', 'definicion', ' selfie', ' filma', ' flash ', 'estabiliza', ' lente', 'fotografi', 'redes sociales'], # No incluiria: [hdr,  optico/a] (pocas menciones como para ver si agregar) ; [delantera, frontal, trasera, megapixeles, mp, grabacion, reflex, enfoque, luz] (siempre acompañados del termino 'camara'); [imagen (pant), zoom (app), foto (pub), grabar (audios),  video/s (video prop), imagenes (varios), luminosidad (pant)] (Otros significados) ; [gcam] (no se refieren a calidad de camara base) ;  # foto no pues si se refiere a la camara es "fotos". foto se confunde con la foto de la publicacion.. # filma incluye filmar, filmacion, filmaciones. # fotografi incluye fotografia/s fotografica
        'diseño': ['diseño', 'estetic', 'terminacion', 'material', 'construc', 'resisten', 'gorila glass', 'gorilla glass',
                   ' fragil', 'robust', ' caida', 'elegante', ' curvo', 'curvatura', ' cayo ', 'plastico', ' moja',
                   ' acabado', ' fachero', ' sobresale', 'delgado', ' ergonom', ' grueso ', ' pliega'], # 'belleza ', ' bello ', 'bonito ', 'hermoso', --> muy grrales como 'lindo' # No incluiria: [grip, aluminio, metal, golpe, resbaladizo, texturada] (Pocas menciones) ; [lindo (en gral), feo (varios), tacto (pant), agarre (detectar), aspecto (aspectos), cristal (otro), mate (otro), vidrio (protector), rompio (otro), atractivo(otro), compacto (tamaño)] (Otros significados)
        'funciones': ['funciones', 'funcion', 'sensores', 'actividad', 'deporte', 'deportiv', 'entrenamiento', 'ejercicio'],  # 'pasos', 'musica', 'llamada', 'pulso', 'mensajes', 'estres', 'relaja', 'cardiac', 'sueño', 'menstrual'],  # no incluyo 'pasos', 'distancia recorrida', 'cardiac', 'pulso', 'pulsaciones', 'gps' pues habla de la medicion precisa o no y no de si tiene tal sensor o no.
        'gps': ['gps'],
        'imagen': [' imagen ', 'pantalla ', 'definicion', ' 4k ', ' hdr ', ' colores ', ' contraste ', ' brillo ', 'refresco'],
        # 'materiales': ['materiales', 'material', 'construc'], # 'agarre', 'tacto', 'antideslizante', ' grip '],
        'memoria': ['memoria', 'interna', 'almacenamiento', ' espacio ', ' jugar ', 'juegos', ' trabajar ', ' trabajo ', ' laburar'], #  'pesadas', 'pesados'],  # No incluria: [sdd, disco, cant de apps] (Pocas menciones) ; [instalar (app y otro), varias apps (velocidad), descargar (varios), gb (ram), gigas (ram), aplicaciones (varios), hardware (gral)] (Otros significados) ; [sd, microsd] (no se refieren a tamaño de memoria base) ; [almacenar, 256, capacidad] (siempre acompañada de palabra relacionada)  juegos (muy frecuente a la altura de 'memoria', taparia rdos) juegos pesados (puede haber coment negativos por velocidad y no tiene que ver con memoria)
        'microfono': ['microfono', ' micro ', ' mic '],
        'oreja': [' oreja', 'cabeza', 'comodo', 'comodidad ', 'almohadillas', ' gomas ', ' oido', 'diseño'],
        'pantalla': [' pantalla ', ' imagen ', 'refresco', ' grafic', 'resolucion', 'juegos', 'jugar'] + l_pantallas,  # No incluiria: [luminosidad, luz azul, iluminacion, 1080, 720, calidad de video, contraste, densidad] (pocas menciones) ; [hz] (No gano significativamente) ; [luz (camara), pantallas (otro), vista(varios), 4k (camara), pixeles (camara), nitidez (camara), tactil (responde), display (varios)] (Otros significados) ; [colores, definicion]  (siempre acompañados de 'pantalla') ; [brillo (como func el sensor de brillo autom)] (no se refieren a la calidad de la pantalla)    , display  # grafic incluye grafica/o/os/as
        'proteccion': ['proteccion', 'protege', 'protej', 'caid', 'cubre ', 'cubrir', 'resiste', 'reforzada', 'cayo', 'golpes'],  # bordees?
        'precio': ['precio', ' marca ', ' costo ',  ' caro ', ' barat', ' economic', 'carisim', ' gastar', ' plata ',
                   ' dinero'], # Muy pocas menciones para ver si incluir: dolares, euros  # No incluiria: sale,  vale, cuesta, gasto/a, pesos, # caro y barato son ADJ pero siempre se refieren al SUST precio # No uso l_marcas pues hay mas FP # "marcas" incluye muchos FP (comparaciones de otros aspectos con otras marcas)
        'ruido': [' ruido', 'cancelacion', ' aisla', 'noise cancelling'],
         'señal': [' señal ', 'datos moviles', ' recepcion', ' antena', ' cobertura', ' 2g ', ' 3g ', ' 4g ', ' lte ', 'comunicar'],  # No inluiria: [rural] (Pocas menciones) ; [5g (modelo), datos (datos prop)] (Otros significados)
        'sistema': ['sistema ', 'software', 'funciones', 'funcionalidades', 'interfaz', 'interface', 'actualizaciones', ' so ', 'preinstal'] + l_sistemas_operativos, # Veer si agrego: configura # No incluiria: [operativo] (siempre acompañada de 'sistema') ; [imcompatible] (Pocas menciones) ; [funcion (varios), de usar (varios), actualizar (modelo), actualizacion (varios)]   (Otro significado)
        'sonido': ['sonido', ' audio ', 'volumen', 'escucha ', ' parlante', ' suena', ' altavo', 'comunicar'], # No incluria: [peliculas, agudos, auditivamente] (Pocas menciones) ; [graves (problema), auriculares (si trae o no), musica (uso)] (Otro significado) ; [dolby] (siempre acomapañado de 'sonido') # ojo con escucha que no debe incluir escuchar # altavo incluye altavoz y altavoces
         'tamaño': ['tamaño ', ' peso ', 'pesado ', 'liviano ', 'grande ', 'dimensiones', ' ancho ', ' gigante',
                    'pulgadas', 'compacto', 'comunicar'],  # No incluiria: [pequeño (diseño), bolsillo (caidas), ligero (velocidad)] (Otros significados)    , 'pesa', ' comod', 'incomod', 'mano', largo, alto, angosto, armatoste, enorme (muy pocas veces se ref a tamaño, y las que lo hacen se pueden salvar) # pense en agregar "pulgadas" pero no se refieren a si es chico o gde. # Pongo 'pesado ' porque pesados se refiere a juegos pesados.
        'teclado': ['teclas', ' ñ '],
        'video': ['video', ' placa ', 'juego', 'tarjeta grafica'],  # https://www.xataka.com/basics/tarjeta-grafica-que-que-hay-dentro-como-funciona
        'velocidad': ['velocidad', ' rapid', ' lento ', ' fluid', 'juegos', ' lentitud ', 'procesador', 'procesamiento',
                      ' ram ', 'funcionamiento', 'snapdragon', 'exynos', 'calienta', 'calent', 'temperatura', ' avion ',
                      ' vuela ', ' nave ', ' potencia ', 'abren y cierran', ' corre ', ' cuelga', ' tilda', ' traba ',
                      ' trabo ', 'rendimiento', 'mismo tiempo', ' veloz', ' abiertas', ' congela ', 'jugar ', 'juegos', ' trabajar ', ' trabajo ', ' laburar', 'redes sociales'],  # No incluiria:  [lag, laguea/o/an, unisoc, bionic, gaming, simultaneo, snp] (Pocas menciones) ; [reinicia, apaga, core/s (modelo), streaming (uso), gamer(uso), a la vez (varios), respuesta (de vendedor), funciona rapido (gral), se cierra , cierra/n, responde (so y gral), tarda] (Otros significados) ; [mediatek, jugar] (siempre acompañada de otra palabra relacionada)   # 'procesa' incluye 'porcesador' y 'procesamiento'.  # rapido no tiene asociado sentiment alto.. perjudica cuando dicen "es rapidp", ' fluid' # calent incluye calento, sobrecalento, calentarse, recalentar
        'voz': ['voz', 'assistant', 'alexa']
         }

'''