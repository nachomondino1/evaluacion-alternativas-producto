'''
d = {'a': 1, 'b': 2, 'c': 3}

if 'c' in d.keys():
    print(d['c'])
'''

import stanfordnlp

stanfordnlp.download('es')


nlp = stanfordnlp.Pipeline(lang='es', processors='tokenize,pos')
texto = "Cats fue una película realmente terrible. Esa película fue un desastre natural.”"
doc = nlp(texto)

print(doc.sentences)