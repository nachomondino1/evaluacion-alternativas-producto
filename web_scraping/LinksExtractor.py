from selenium.webdriver.common.by import By

def getPublicationsUrl(driver):
    # Podria intentar que sirva no solo para mercadolibre.com sino tambien para otras como amazon.com o Ebay.com
    # Nota: estan en un div#class=ui-search-result__image
    links = driver.find_elements(By.XPATH, '//div[@class="ui-search-result__image"]/a')
    links_pagina = []

    for link in links:
        links_pagina.append(link.get_attribute("href"))
    return links_pagina


def getHomePageUrl(busqueda):
    # La busqueda ya esta validada (es decir, pertenece a una categoria de producto especifica)
    # las url son de la forma https://listado.mercadolibre.com.ar/banco-de-pesa#D[A:banco%20de%20pesa]
    # Ej: https://listado.mercadolibre.com.ar/ropero#D[A:ropero]
    # Esta hecha solo para meli, podria agregar flexibilidad.

    a = busqueda.replace(" ", "-")
    b = busqueda.replace(" ", "%20")
    url = 'https://listado.mercadolibre.com.ar/' + a + "#D[A:" + b + "]"
    return url


def getPaginacionUrl(driver):
    """

    :return:
    Nota: Habiendo visitado MercadoLibre.com Amazon.com, Ebay.com noto que cada pagina tiene el link en un tag distinto
    pero todos ellos tienen el atributo role="navigation"
    Pero hay muchos tags con role=navigation...

    En Ebay, hay un tag nav que es el unico que tiene como pagination como atributo class aunque hay otros que tienen dicho texto como parte de su atributo class

    Regla que cumplen en comun. Puedo ubicar container de paginacion segun el tag (pues no todos tienen el mismo) cuyos atributos
    - class contains "pagination"
    - role = navigation
    Como tal vez necesito un tag... podri ser: dentro de una clase div cuyo atributo class contiene s-pagination o search-pagination

    Luego, para encontrar el link de la siguiente pagina:
    tag a cuyo alguno de sus atributos contiene pagination__next o next o siguiente o Siguiente
    Meli es el problema porque su tag a no tiene el atributo class con las palabras pagination-next o pagination_next como los otros aunque solo hay un tag a a diferencia de los otros.

    Intente hacerlo flexible pero son paginas muy distintas (falla en meli pues en paginas ≠ a la 1, hay dos a que tienen pagination__link... y vuelve a la pag anterior:
    # Ubico container de paginacion
    pagination_container = driver.find_element_by_xpath('.//div[contains(@class,"search-pagination") '
                                                        'or contains(@class,"s-pagination")]')

    # Ubico link de siguiente pagina
    link_paginacion = pagination_container.find_element_by_xpath('.//a[contains(@class,"pagination-next") '
                                                                 'or contains(@class,"pagination__link")]').get_attribute('href')

    Lo hago para meli y dsp vere de hacerlo mas flexible
    """

    # Ubico link de siguiente pagina
    link_paginacion = driver.find_element_by_xpath('.//li[@class="andes-pagination__button andes-pagination__button--next"]/a').get_attribute('href')
    return link_paginacion


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
    driver.get(getHomePageUrl(busqueda))

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