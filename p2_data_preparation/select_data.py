def select_attributes(df_alt):
    """
    Elimino atributos que fueron extraidos exclusivamente para ser mostrados al cliente, es decir, importantes a la hora
    de elegir entre alternativas pero no para el analisis.
    :param df_alt: Dataframe. Unidad de analisis: alternativa del producto. Columnas id_alternativa, precio y campos
    especificos segun el producto.
    :return: Dataframe. Unidad de analisis: alternativa del producto. Columnas id_alternativa, precio y campos
    especificos segun el producto pero solo aquellos campos relevantes para el analisis
    """
    # Defino variables
    l_attr_remove = []
    l_attr_not_remove = ['id_alternativa', 'precio', 'Marca', 'Modelo']  # Atributos que no hay que eliminar

    # POR ATRIBUTO
    for atributo in df_alt.columns:

        # SI NO ES DE LOS QUE HAY QUE EVITAR ELIMINAR
        if atributo not in l_attr_not_remove:
            print(atributo.center(120))

            # Obtengo lista de frecuencia de sus valores
            l_unique_values = list(df_alt[atributo].dropna().unique())  # dropna para evitar que NaN sea una valor unico
            n_possible_unique_values = len(df_alt[atributo].dropna())
            n_opt_unique_values = int(len(df_alt[atributo].dropna()) ** 0.5)  # raiz de numero de datos
            n_nan_values = (len(df_alt) - n_possible_unique_values) / len(df_alt)

            # Si toma muchos valores distintos
            if len(l_unique_values) > n_opt_unique_values:
                print("CUIDADO! Tiene mas valores unicos que lo recomendado que es {}".format(n_opt_unique_values))
                print("Nºvalores: {} ; Nºvalores unicos: {}".format(n_possible_unique_values, len(l_unique_values)))

            # Si tiene muchos valores NaN
            if n_nan_values > 0.5:
                print("CUIDADO! Toma muchos valores NaN, un {:1f}%".format(n_nan_values*100))

            # Mientras la carga sea invalida
            while True:
                try:
                    # Solicito 0 o 1 para determinar si el atributo sera considerado o no
                    bool = int(input("Tendra en cuenta el elemento '{}' (0 o 1): ".format(atributo.upper())))

                    # Si el ingreso es valido (0 o 1)
                    if bool == 0 or bool == 1:

                        # Si el atributo no sera considerado
                        if bool == 0:
                            # Remuevo el atributo
                            l_attr_remove.append(atributo)
                        break

                except ValueError:  # si el input no es un numero entero
                    pass

    # ELIMINO ATRIBUTOS NO RELEVANTES DE DATAFRAME ALTERNATIVAS
    df_alt = df_alt.drop(l_attr_remove, axis=1)
    return df_alt

