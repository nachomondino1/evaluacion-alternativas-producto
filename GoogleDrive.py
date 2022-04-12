import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import FileNotUploadedError

directorio_credenciales = 'credentials_module.json'


# INICIAR SESION
def login():
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = directorio_credenciales
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(directorio_credenciales)

    if gauth.credentials is None:
        gauth.LocalWebserverAuth(port_numbers=[8092])
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile(directorio_credenciales)
    credenciales = GoogleDrive(gauth)
    return credenciales


def crear_archivo_texto(nombre_archivo, contenido, id_folder):
    credenciales = login()
    archivo = credenciales.CreateFile({'title': nombre_archivo, 'parents': [{"kind": "drive#fileLink", "id": id_folder}]})
    archivo.SetContentString('Hey MoonCoders!')
    archivo.Upload()


# SUBIR UN ARCHIVO A DRIVE
def subir_archivo(ruta_archivo, id_folder):
    credenciales = login()
    archivo = credenciales.CreateFile({'parents': [{"kind": "drive#fileLink", "id": id_folder}]})
    archivo['title'] = ruta_archivo.split("/")[-1]
    archivo.SetContentFile(ruta_archivo)
    archivo.Upload()


# DESCARGAR UN ARCHIVO DE DRIVE POR ID
def bajar_archivo_por_id(id_drive, ruta_descarga):
    credenciales = login()
    archivo = credenciales.CreateFile({'id': id_drive})
    nombre_archivo = archivo['title']
    archivo.GetContentFile(ruta_descarga + nombre_archivo)


# LEER ARCHIVO
def leer_archivo(nombre_archivo):
    credenciales = login()
    lista_archivos = credenciales.ListFile({'q': "title = '" + nombre_archivo + "'"}).GetList()
    if not lista_archivos:
        print('No se encontro el archivo: ' + nombre_archivo)
    archivo = lista_archivos[0]
    download_url = archivo['embedLink']
    return download_url


# BUSCAR ARCHIVOS
def busca(query):
    resultado = []
    credenciales = login()
    # Archivos con el nombre 'mooncode': title = 'mooncode'
    # Archivos que contengan 'mooncode' y 'mooncoders': title contains 'mooncode' and title contains 'mooncoders'
    # Archivos que NO contengan 'mooncode': not title contains 'mooncode'
    # Archivos que contengan 'mooncode' dentro del archivo: fullText contains 'mooncode'
    # Archivos en el basurero: trashed=true
    # Archivos que se llamen 'mooncode' y no esten en el basurero: title = 'mooncode' and trashed = false
    lista_archivos = credenciales.ListFile({'q': query}).GetList()
    for f in lista_archivos:
        # ID Drive
        print('ID Drive:', f['id'])
        # Link de visualizacion embebido
        print('Link de visualizacion embebido:', f['embedLink'])
        # Link de descarga
        print('Link de descarga:', f['downloadUrl'])
        # Nombre del archivo
        print('Nombre del archivo:', f['title'])
        # Tipo de archivo
        print('Tipo de archivo:', f['mimeType'])
        # Esta en el basurero
        print('Esta en el basurero:', f['labels']['trashed'])
        # Fecha de creacion
        print('Fecha de creacion:', f['createdDate'])
        # Fecha de ultima modificacion
        print('Fecha de ultima modificacion:', f['modifiedDate'])
        # Version
        print('Version:', f['version'])
        # Tamanio
        print('Tamanio:', f['fileSize'])
        resultado.append(f)

    return resultado


# DESCARGAR UN ARCHIVO DE DRIVE POR NOMBRE
def bajar_archivo_por_nombre(nombre_archivo, ruta_descarga):
    credenciales = login()
    lista_archivos = credenciales.ListFile({'q': "title = '" + nombre_archivo + "'"}).GetList()
    if not lista_archivos:
        print('No se encontro el archivo: ' + nombre_archivo)
    archivo = credenciales.CreateFile({'id': lista_archivos[0]['id']})
    archivo.GetContentFile(ruta_descarga + nombre_archivo)


# BORRAR/RECUPERAR ARCHIVOS
def borrar_recuperar(id_archivo):
    credenciales = login()
    archivo = credenciales.CreateFile({'id': id_archivo})
    # MOVER A BASURERO
    archivo.Trash()
    # SACAR DE BASURERO
    archivo.UnTrash()
    # ELIMINAR PERMANENTEMENTE
    archivo.Delete()


# CREAR CARPETA
def crear_carpeta(nombre_carpeta, id_folder):
    credenciales = login()
    folder = credenciales.CreateFile({'title': nombre_carpeta,
                                      'mimeType': 'application/vnd.google-apps.folder',
                                      'parents': [{"kind": "drive#fileLink", \
                                                   "id": id_folder}]})
    folder.Upload()


# MOVER ARCHIVO
def mover_archivo(id_archivo, id_folder):
    credenciales = login()
    archivo = credenciales.CreateFile({'id': id_archivo})
    propiedades_ocultas = archivo['parents']
    archivo['parents'] = [{'isRoot': False,
                           'kind': 'drive#parentReference',
                           'id': id_folder,
                           'selfLink': 'https://www.googleapis.com/drive/v2/files/' + id_archivo + '/parents/' + id_folder,
                           'parentLink': 'https://www.googleapis.com/drive/v2/files/' + id_folder}]
    archivo.Upload(param={'supportsTeamDrives': True})


# ENLISTAR LOS PERMISOS ACTUALES
def enlistar_permisos_actuales(id_drive):
    drive = login()
    file1 = drive.CreateFile({'id': id_drive})
    permissions = file1.GetPermissions()
    lista_de_permisos = file1['permissions']

    for permiso in lista_de_permisos:
        # ID DEL PERMISO
        print('ID PERMISO: {}'.format(permiso['id']))
        # ROLE = owner | organizer | fileOrganizer | writer | reader
        print('ROLE: {}'.format(permiso['role']))
        # TYPE (A QUIEN SE LE COMPARTIRA LOS PERMISOS) = anyone | group | user
        print('TYPE: {}'.format(permiso['type']))

        # EMAIL
        if permiso.get('emailAddress'):
            print('EMAIL: {}'.format(permiso['emailAddress']))

        # NAME
        if permiso.get('name'):
            print('NAME: {}'.format(permiso['name']))

        print('=====================================================')


# INSERTAR/ OTORGAR PERMISOS
def insertar_permisos(id_drive, type, value, role):
    drive = login()
    file1 = drive.CreateFile({'id': id_drive})
    # VALUE (EMAIL DE A QUIEN SE LE OTORGA EL PERMISO)
    permission = file1.InsertPermission({'type': type, 'value': value, 'role': role})


# ELIMINAR PERMISOS
def eliminar_permisos(id_drive, permission_id=None, email=None):
    drive = login()
    file1 = drive.CreateFile({'id': id_drive})
    permissions = file1.GetPermissions()
    if permission_id:
        file1.DeletePermission(permission_id)
    elif email:
        for permiso in permissions:
            if permiso.get('emailAddress'):
                if permiso.get('emailAddress') == email:
                    file1.DeletePermission(permiso['id'])


if __name__ == "__main__":
    ruta_archivo = '/home/falv/Escritorio/fondo.jpg'
    id_folder = '1Y1DiQFQ5sQi-uod2uQ61Dmenh3GPNO3p'
    # id_drive = '1LVdc-DUwr30kfrA30cVO3K92RVh56pmw'
    # ruta_descarga = '/home/falv/Descargas/'
    # crear_archivo_texto('HolaDrive.txt','Hey MoonCoders',id_folder)
    # subir_archivo(ruta_archivo,id_folder)
    # bajar_archivo_por_id(id_drive,ruta_descarga)
    busca("title = 'relation_matrix.xlsx'")
    # bajar_archivo_por_nombre('Logo_1.png',ruta_descarga)
    # borrar_recuperar('1lHBMFjdyKfAYRa4M57biDZCiDwFhAYTy')
    # crear_carpeta('hola_folder',id_folder)
    # mover_archivo('1PmdkaivVUZKkDwFapSWrXNf6n6pO_YK-', '1uSMaBaoLOt7F7VJiCZkrO4ckvj6ANecQ')

