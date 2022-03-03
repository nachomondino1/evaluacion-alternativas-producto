# 2DO intento: LIBRERIA PYCURL
# importo libreria
import pycurl
from io import BytesIO

b_obj = BytesIO()
crl = pycurl.Curl()

# Set URL value
crl.setopt(crl.URL, 'https://api.mercadolibre.com/reviews/item/MLA813473400')

# Write bytes that are utf-8 encoded
crl.setopt(crl.WRITEDATA, b_obj)

# Perform a file transfer
crl.perform()

# End curl session
crl.close()

# Get the content stored in the BytesIO object (in byte characters)
get_body = b_obj.getvalue()

# Decode the bytes stored in get_body to HTML and print the result
print('Output of GET request:\n%s' % get_body.decode('utf8'))

# curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/reviews/item/MLA813473400

"""
1er intento: LIBRERIA REQUESTS
# Obtengo las opiniones de un producto
r = requests.get("https://api.mercadolibre.com/reviews/item/MLA813473400")
print(r.content)

# Convierto variable r de Bytes a JSON para facilitar operacion
r = r.json()
# print(type(r))
#print(r["reviews"])
#print(type(r["reviews"]))

# Imprimo cada opinion
for element in r["reviews"]:
    print(element)

# print(r["reviews"][0])
# print(type(r["reviews"][0]))
"""