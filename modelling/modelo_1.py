# Creo que implementare un modelo por archivo
# Importo librerias
import pandas as pd

df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx')

from pysentimiento import create_analyzer
analyzer = create_analyzer(task="sentiment", lang="es")

for i in range(10): # range(len(df_opiniones)):
    opinion = df_opiniones.iloc[i, 2]
    rate = df_opiniones.iloc[i, 3]
    print(opinion)
    print(rate)
    print(analyzer.predict(opinion))
    print("++++")


''' Fallo la implementacion del modelo que use en el trabajo el año pasado
from sentiment_analysis_spanish import sentiment_analysis

df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx')

# Creo objeto de clase SentimentAnalysisSpanish
sentiment = sentiment_analysis.SentimentAnalysisSpanish

print()

df_opiniones['sentiment'] = df_opiniones['content'].apply(sentiment.sentiment, 3)
print(df_opiniones)
'''



