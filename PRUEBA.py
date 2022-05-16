import pandas as pd
# from data_preparation.utils import preparacion_texto

'''
df_alternativas = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_alt_celulares.xlsx')
df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_opi_celulares.xlsx')

print(df_alternativas.head())
print(df_opiniones.head())
j = 0
for id_pub in df_opiniones['id_alternativa'].unique():
    if id_pub not in list(df_alternativas['id_alternativa']):
        j += 1
        print(j)
'''

def sentences_in_text(text):
    # Defino variables
    punto = '.'
    sentences = []
    pos_ini = 0

    for pos, char in enumerate(text):
        if (char == punto):
            sentences.append(text[pos_ini:pos])
            pos_ini = pos + 1

    # Si el punto no es el ultimo caracter del texto
    if pos_ini != len(text):
        # Guardo ultima sentence
        sentences.append(text[pos_ini:len(text)])

    return sentences

text = 'Excelente producto relación precio equipo. Es fluido tiene un buen sonido. Las cámaras están muy bien aún en ambientes con sombras. El autofoco no es de los más rápidos pero funciona bien. El procesador tiene un buen rendimiento. Aún no puedo opinar de la autonomía. Viene con android 10 de raíz. La caja viene completa. Cargador usb auriculares funda templado. Mas no se puede pedir. Y la calidad del cartón es muy buena ,un cartón duro y sobrio llega en una caja negra con rígida con las letras de quantum frontal y de costado. No existen descripción alguna del equipo en la caja ,eso la hace muy sobria. Un equipo ideal para uso cotidiano. Yo habitualmente pruebo equipos y este equipo lo recomiendo. El up 32. El color bordo es hermoso. Tengan en cuenta que el quantum yolo es apenas más económico pero es 3g y tiene un procesador de 4 nucleos ( el up de 8) y una pantalla de 5 pulgadas (el up 5. 5 pulgadas ) y la batería del up es de 2700 mah '
print(sentences_in_text(text))


'''
l = [1, 2, 3, 4]
l_series = pd.Series(l)
print(l_series)
print(list(l_series.values))
'''


''' drop duplicates
df_alternativas = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_alt_celulares.xlsx')
print(df_alternativas)
df_alternativas = df_alternativas.drop_duplicates(subset=list(df_alternativas.columns[2:]), ignore_index=True)
print(df_alternativas)
df_alternativas.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_alt_cleaned_{}.xlsx'.format('celulares'), 'Hoja de datos', index=False)
'''

'''
d = {'a': 1, 'b': 2, 'c': 3}

if 'c' in d.keys():
    print(d['c'])

print(list(d.values()))


df = pd.DataFrame(data={"col1":[1,2,3,None,3,4], "col2": [4,5,6,4,6,7]})
print(df)

for a in df['col1']:
    print (a)
    #print(b)

# df = df['col1'].unique()
# df = df.drop_duplicates(subset='col2', ignore_index=True)
#print(df)
'''


'''
# 3. Data preparation - Preparacion texto
df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_opiniones_celulares.xlsx')
textos = df_opiniones['opinion']
texto = "Las hojas caen sobre mi casa"

texto = pd.Series([texto])
tp = preparacion_texto.TextPreparation(textos=texto)
texto = tp.to_lower()
print(texto)

# tp = preparacion_texto.TextPreparation(textos=textos)
# Voy sacandole tod@ a las opiniones como sigue:
# df_opiniones['opinion'] = tp.delete_accent()

# print(tp.delete_accent())
# print(tp.delete_punctuation())

# df_opiniones['opinion'] = tp.tokenize()
# df_opiniones['opinion'] = tp.stop_word_removal()
# print(df_opiniones['opinion'])
'''



'''
# 3. Data preparation - Construct data
import stanza

# stanza.download('es')       # This downloads the English models for the neural pipeline
nlp = stanza.Pipeline('es') # This sets up a default neural pipeline in English
doc = nlp("Hola")
# doc.sentences[0].print_dependencies()

# print(doc.sentences)
print(doc.sentences[0].words[0].pos)

for i, sent in enumerate(doc.sentences):
    print("[Sentence {}]".format(i+1))
    for word in sent.words:
        print("{:12s}\t{:12s}\t{:6s}\t{:d}\t{:12s}".format(\
              word.text, word.lemma, word.pos, word.head, word.deprel))
    print("")
'''


'''
# 4. Modelling - Atribucion to customer needs
import nltk
text = "Samsung galaxy z flip3 5g 128 gb phantom black 8 gb ram. Espectacular. Arranco con los puntos flojos: la batería y las cámaras. La batería con suerte llega a la noche, lo cual de por sí puede no ser un problema, pero uno espera algo más de un producto en este rango de precios. Lo mismo con las cámaras, existen otros celulares de la misma gama con cámaras bastante superiores. Se tuvieron que reducir las prestaciones de estos dos componentes por el diseño y arquitectura de este celular que se pliega? es probable. Tampoco viene con cargador, sólo con un cable usb-c en ambos extremos. Todo lo demás es excelente, pantalla super nítida con excelente densidad ppi, interacción muy fluida, android 12, mucha memoria, mucho espacio en disco, ligero y delgado, excelente soporte de audio (32-bit/384khz), la posibilidad de sacarse selfies con las cámaras de atrás al tener el celular plegado y la mejor característica de todas: el tamaño del celular cuando está cerrado. Es pasar de tener un ladrillo en la mano o en el bolsillo a algo muy pequeño, fruto de avance tecnológico. No hace falta abrir a cada momento el celular, con la pequeña pantalla de atrás donde se reciben las notificaciones basta y sobra para decidir si es necesario. Además, en argentina está a muy buen precio comparado con precios internacionales. Excelente producto. Lo recomiendo y dudo que en el futuro vuelva atrás y abandone la línea de celulares plegables."

for frase in nltk.tokenize.sent_tokenize(text):
    print(frase)
'''

'''
# 4. Modelling - Atribucion to customer needs
from pysentimiento import create_analyzer

analyzer = create_analyzer(task="sentiment", lang="es")
text = "Por fin un teléfono práctico !!!. Basta de andar con ladrillos en la mano con cara de no saber donde ponerlo !!!. Funcionamiento excelente. La batería dura un montón. No calienta para nada. El que diga lo contrario está mintiendo descaradamente. Lo mejor de todo: es súper portable, entra en el bolsillo y no te das cuenta de que lo tenés encima. Si lo que buscas es un teléfono de excelentes prestaciones y no te interesa andar mostrándolo a todo el mundo para mandarte la parte este es el teléfono ideal. Algo más: la pantallita de notificaciones exterior es bárbara !!!!, te indica lo necesario !!!!. A partir de este teléfono el resto no existe !!!!."
sent_frase = analyzer.predict(text)  # Predigo sentiment de frase

print(sent_frase)
print(type(sent_frase))
print(sent_frase.probas)
print(sent_frase.probas.keys())
'''


'''
# 4. Modelling - Entity Sentiment Analysis
import spacy
nlp = spacy.load("es_core_news_sm")

text1 = "Por fin un teléfono práctico !!!. Basta de andar con ladrillos en la mano con cara de no saber donde ponerlo !!!. Funcionamiento excelente. La batería dura un montón. No calienta para nada. El que diga lo contrario está mintiendo descaradamente. Lo mejor de todo: es súper portable, entra en el bolsillo y no te das cuenta de que lo tenés encima. Si lo que buscas es un teléfono de excelentes prestaciones y no te interesa andar mostrándolo a todo el mundo para mandarte la parte este es el teléfono ideal. Algo más: la pantallita de notificaciones exterior es bárbara !!!!, te indica lo necesario !!!!. A partir de este teléfono el resto no existe !!!!."
text2 = "Matias tiene un gato. Los lunes son dias muy bonitos. La chica de Boston estudia ciencias sociales en una universidad muy prestigiosa"
text3 = "Samsung galaxy z flip3 5g 128 gb phantom black 8 gb ram. Espectacular. Arranco con los puntos flojos: la batería y las cámaras. La batería con suerte llega a la noche, lo cual de por sí puede no ser un problema, pero uno espera algo más de un producto en este rango de precios. Lo mismo con las cámaras, existen otros celulares de la misma gama con cámaras bastante superiores. Se tuvieron que reducir las prestaciones de estos dos componentes por el diseño y arquitectura de este celular que se pliega? es probable. Tampoco viene con cargador, sólo con un cable usb-c en ambos extremos. Todo lo demás es excelente, pantalla super nítida con excelente densidad ppi, interacción muy fluida, android 12, mucha memoria, mucho espacio en disco, ligero y delgado, excelente soporte de audio (32-bit/384khz), la posibilidad de sacarse selfies con las cámaras de atrás al tener el celular plegado y la mejor característica de todas: el tamaño del celular cuando está cerrado. Es pasar de tener un ladrillo en la mano o en el bolsillo a algo muy pequeño, fruto de avance tecnológico. No hace falta abrir a cada momento el celular, con la pequeña pantalla de atrás donde se reciben las notificaciones basta y sobra para decidir si es necesario. Además, en argentina está a muy buen precio comparado con precios internacionales. Excelente producto. Lo recomiendo y dudo que en el futuro vuelva atrás y abandone la línea de celulares plegables."

def spacy_ner(text):
    """

    :param text: Texto
    :return: Entidades del texto
    """
    # Defino variables
    entities = []
    labels = []
    position_start = []
    position_end = []

    # Proceso el texto
    doc = nlp(text)

    # Por entidad
    for ent in doc.ents:
        print(ent)
        if ent.label_ in ['PERSON','ORG','GPE']:
            entities.append(ent)
            labels.append(ent.label_)
    return entities,labels

entities, labels = spacy_ner(text3)
print(entities)
print(labels)

'''

