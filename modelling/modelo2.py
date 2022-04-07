
''' Fallo la implementacion del modelo que use en el trabajo el año pasado
from sentiment_analysis_spanish import sentiment_analysis

df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx')

# Creo objeto de clase SentimentAnalysisSpanish
sentiment = sentiment_analysis.SentimentAnalysisSpanish

print()

df_opiniones['sentiment'] = df_opiniones['content'].apply(sentiment.sentiment, 3)
print(df_opiniones)
'''
