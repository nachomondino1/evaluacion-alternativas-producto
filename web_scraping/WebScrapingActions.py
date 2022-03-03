from time import sleep
import random
import LinksExtractor as le
from selenium.webdriver.common.by import By


# Podria implementar cosas como ingresar un usuario, hacer un kampachatca, cerrrar un ad, etc

def ScrollDown(driver):
    # Get scroll height
    # Defino tiempo de pausa aleatorio entre 1 y 2 segundos para evitar banneo de IP
    SCROLL_PAUSE_TIME = random.uniform(1, 2)

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height


def validacionBusqueda(driver, busqueda):
    """
    Requiero una busqueda que tenga categoria de producto pues sino la busqueda es muy amplia (muchos publicaciones)
    y el costo computacional seria muy alto para una busqueda sin sentido

    :param driver: web browser automatico
    :param busqueda: Producto que quiere comprar el cliente
    :return: True si mercadolibre encuentra categoria a la busqueda o False en caso contrario

    Nota:
    Cuando alguien hace una busqueda en meli, hay dos casos:
    1.- Meli encuentra la categoria del producto buscado. Por ej, busqueda "discos de pesa"
    2.- Si meli NO encuentra la categoria del producto buscado. Por ej, busqueda "discos"--> busqueda muy amplia.
    La diferencia entre 1 y 2 se da en que dentro del div#class"=ui-search-breadcrumb" los 1 tienen el tag ol#class="andes-breadcrumb" y los 2 no

    Esta hecha solo para usar el buscador de meli, podria agregar flexibilidad haciendo que sirva para otras paginas como amazon por ej.
    """

    # Ingreso a URL semilla (en este caso, la pagina principal de mercado libre)
    driver.get(le.getHomePageUrl(busqueda))

    try:
        driver.find_element(By.XPATH, '//div[@class="ui-search-breadcrumb"]/ol[@class="andes-breadcrumb"]')
        return True
    except:
        return False

    """
    # implementado con ciclo --> en lugar de poner el ciclo en el main (no tiene return)
    bool = True

    while bool:
        # Ingreso a URL semilla (en este caso, la pagina principal de mercado libre)
        driver.get(le.getHomePageUrl(busqueda))

        try:
            driver.find_element(By.XPATH, '//div[@class="ui-search-breadcrumb"]/ol[@class="andes-breadcrumb"]')

            # solo llega a esta linea sino crashea en la busqueda anterior
            bool = False

        except:
            print("Por favor sea mas especifico en su busqueda")
            busqueda = str(input("Ingrese busqueda:"))
    return 
    """