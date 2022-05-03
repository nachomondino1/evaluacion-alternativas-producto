import pandas as pd
from data_preparation.utils import preparacion_texto
'''
d = {'a': 1, 'b': 2, 'c': 3}

if 'c' in d.keys():
    print(d['c'])

print(list(d.values()))


df = pd.DataFrame(data={"col1":[1,2,3,None,3,4], "col2": [4,5,6,4,6,7]})
print(df)
df = df.drop_duplicates(subset='col2')
print(df)
'''


# 3. Data preparation - Preparacion texto
df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx')
textos = df_opiniones['opinion']
tp = preparacion_texto.TextPreparation(textos=textos)

# Voy sacandole tod@ a las opiniones como sigue:
# df_opiniones['opinion'] = tp.delete_accent()

# print(tp.delete_accent())
# print(tp.delete_punctuation())

df_opiniones['opinion'] = tp.tokenize()
df_opiniones['opinion'] = tp.stop_word_removal()
print(df_opiniones['opinion'])


'''
# 3. Data preparation - Construct data

import stanza

# stanza.download('es')       # This downloads the English models for the neural pipeline
nlp = stanza.Pipeline('es') # This sets up a default neural pipeline in English
doc = nlp("Hola, no se que decir porque es una prueba.")
# doc.sentences[0].print_dependencies()

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

# nltk.download('punkt')

text = 'samsung galaxy z flip3 5g 128 gb phantom black 8 gb ram. espectacular. arranco con los puntos flojos: la bateria y las camaras. la bateria con suerte llega a la noche, lo cual de por si puede no ser un problema, pero uno espera algo mas de un producto en este rango de precios. lo mismo con las camaras, existen otros celulares de la misma gama con camaras bastante superiores. se tuvieron que reducir las prestaciones de estos dos componentes por el diseño y arquitectura de este celular que se pliega? es probable. tampoco viene con cargador, solo con un cable usb-c en ambos extremos. todo lo demas es excelente, pantalla super nitida con excelente densidad ppi, interaccion muy fluida, android 12, mucha memoria, mucho espacio en disco, ligero y delgado, excelente soporte de audio (32-bit/384khz), la posibilidad de sacarse selfies con las camaras de atras al tener el celular plegado y la mejor caracteristica de todas: el tamaño del celular cuando esta cerrado. es pasar de tener un ladrillo en la mano o en el bolsillo a algo muy pequeño, fruto de avance tecnologico. no hace falta abrir a cada momento el celular, con la pequeña pantalla de atras donde se reciben las notificaciones basta y sobra para decidir si es necesario. ademas, en argentina esta a muy buen precio comparado con precios internacionales. excelente producto. lo recomiendo y dudo que en el futuro vuelva atras y abandone la linea de celulares plegables'

a_list = nltk.tokenize.sent_tokenize(text)

print(a_list)
'''