import pyodbc
import os
import json
from PIL import Image
import hashlib
from ftplib import FTP
from woocommerce import API
import time
import requests

# Aumentar el tiempo de espera predeterminado
DEFAULT_TIMEOUT = 15

def get_wc_api():
    try:
        wc_api = API(
            url="https://stylomoda.es/",
            consumer_key="ck_2bad2947a3398e50e4300346a41e243081886a4e",
            consumer_secret="cs_2508f2cda83d14009a0996fe54f24ffcdcfd02f3",
            wp_api=True,
            version="wc/v3",
            timeout=DEFAULT_TIMEOUT
        )
        return wc_api
    except Exception as e:
        print("Error de conexion:", e)
        return None
    
    

def obtener_articulos_woocommerce(wc_api):
    try:
        page = 1
        all_products = []

        while True:
            response = wc_api.get("products", params={"page": page, "per_page": 100})
            if response.status_code != 200:
                print("Error al obtener los productos:", response.json())
                return None

            categories = response.json()
            all_products.extend(categories)

            headers = response.headers
            if not headers.get("X-WP-TotalPages") or page >= int(headers["X-WP-TotalPages"]):
                break

            page += 1

        return all_products
    except Exception as e:
        print("Error al obtener productos:", e)
        return None



def obtener_cod_arancelario(cod_articulo):
    server = '192.168.200.32'
    database = 'VEBD'
    username = 'logic'
    password = '#Obelix*.99'

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = conn.cursor()

        consulta1 = (f"SELECT CodigoSubfamilia FROM Articulos WHERE CodigoEmpresa = 997"
                        f" AND CodigoArticulo = '{cod_articulo}'")

        cursor.execute(consulta1)

        datos_desde_bd = cursor.fetchone()

        for subfamilia in datos_desde_bd:
            if subfamilia == "":
                cursor.execute("SELECT f.CodigoArancelario FROM Familias f INNER JOIN Articulos a "
                                "ON f.CodigoFamilia = a.CodigoFamilia WHERE f.CodigoEmpresa = 997 "
                                f"AND CodigoArticulo = '{cod_articulo}' AND f.CodigoSubfamilia = '**********'")
                cod_arancelario = cursor.fetchone()
            else:
                cursor.execute("SELECT f.CodigoArancelario FROM Familias f INNER JOIN Articulos a "
                                "ON f.CodigoSubfamilia = a.CodigoSubfamilia WHERE f.CodigoEmpresa = 997"
                                f" AND CodigoArticulo = '{cod_articulo}'")
                cod_arancelario = cursor.fetchone()

            if cod_arancelario:
                return cod_arancelario[0]

    except pyodbc.Error as e:
        print(e)
        return None


def obtener_articulos_bd():
    server = '192.168.200.32'
    database = 'VEBD'
    username = 'logic'
    password = '#Obelix*.99'

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = conn.cursor()

        consulta1 = (f"""
                        SELECT CodigoArticulo, DescripcionArticulo, DescripcionLinea, ComentarioArticulo,
                        CodigoArancelario, PrecioVenta, CodigoSubfamilia, CodigoFamilia, CodigoAlternativo
                        FROM Articulos
                        WHERE CodigoEmpresa = 997 and PublicarInternet = -1
                    """)

        cursor.execute(consulta1)

        datos_desde_bd = cursor.fetchall()

        datos_json = []
        for fila in datos_desde_bd:
            if fila[6] == "":
                fila_json = {
                    "codAlternativo": fila[8] if fila[8] else "",
                    "sku": fila[0] if fila[0] else "",
                    "name": fila[1] if fila[1] else "",
                    "type": "variable",
                    "description": fila[2] if fila[2] else "",
                    "short_description": fila[3] if fila[3] else "",
                    "categories": [
                        {
                            "id": int(fila[4]) if fila[4].isdigit() else 0,
                        }
                    ],
                    "regular_price": str(fila[5]) if fila[5] else "0"
                    # "src": fila[9] if fila[9] else ""  # Comentado para deshabilitar imágenes
                }
            else:
                consulta2 = (f"""SELECT CodigoArancelario FROM Familias
                                WHERE CodigoFamilia = '{fila[7]}'
                                AND CodigoEmpresa = 997 AND CodigoSubfamilia = '**********'
                            """)
                cursor.execute(consulta2)
                subfamilia = cursor.fetchall()

                for fila1 in subfamilia:
                    fila_json = {
                        "codAlternativo": fila[8] if fila[8] else "",
                        "sku": fila[0] if fila[0] else "",
                        "name": fila[1] if fila[1] else "",
                        "type": "variable",
                        "description": fila[2] if fila[2] else "",
                        "short_description": fila[3] if fila[3] else "",
                        "categories": [
                            {
                                "id": int(fila[4]) if fila[4].isdigit() else 0
                            },
                            {
                                "id": int(fila1[0]) if fila1[0].isdigit() else 0
                            }
                        ],
                        "regular_price": str(fila[5]) if fila[5] else "0"
                        # "src": fila[9] if fila[9] else ""  # Comentado para deshabilitar imágenes
                    }

            datos_json.append(fila_json)

        conn.close()
        return datos_json
    except pyodbc.Error as e:
        print(e)
        return None


def obtener_atributos_bd():
    server = '192.168.200.32'
    database = 'VEBD'
    username = 'logic'
    password = '#Obelix*.99'

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = conn.cursor()

        consulta = "SELECT DescripcionGrupoTalla_ FROM GrupoTallas_ WHERE CodigoEmpresa = 997;"

        cursor.execute(consulta)

        # Obtener los datos seleccionados
        datos_desde_bd = cursor.fetchall()

        # Convertir los datos a una lista de diccionarios
        datos_json = []
        for fila in datos_desde_bd:
            datos_json.append({"name": fila[0]})

        # Agregar el atributo "COLORES" a la lista de diccionarios
        datos_json.append({"name": "COLORES"})

        # Cerrar la conexión después de obtener todos los datos
        conn.close()
        return datos_json

    except pyodbc.Error as e:
        print(e)
        return None


def obtener_terms_colores_bd():
    server = '192.168.200.32'
    database = 'VEBD'
    username = 'logic'
    password = '#Obelix*.99'

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = conn.cursor()

        consulta = "SELECT Color_ FROM Colores_ WHERE CodigoEmpresa = 997;"

        cursor.execute(consulta)

        datos_desde_bd = cursor.fetchall()

        datos_json = []
        for fila in datos_desde_bd:
            datos_json.append({"name": fila[0]})

        conn.close()
        return datos_json

    except pyodbc.Error as e:
        print(e)
        return None


def obtener_terms_tallas_bd(grupo_talla):
    server = '192.168.200.32'
    database = 'VEBD'
    username = 'logic'
    password = '#Obelix*.99'

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = conn.cursor()

        consulta = "SELECT * FROM GrupoTallas_ WHERE CodigoEmpresa = 997 AND DescripcionGrupoTalla_ = ?;"
        cursor.execute(consulta, grupo_talla)

        datos_desde_bd = cursor.fetchall()

        if not datos_desde_bd:
            print(f"No se encontraron datos para el grupo de tallas {grupo_talla}.")
            return None

        numero_tallas = int(datos_desde_bd[0][3])

        tallas = []
        for i in range(4, 4 + (numero_tallas * 3), 3):
            talla = datos_desde_bd[0][i]
            tallas.append({"name": talla})

        conn.close()
        return tallas

    except pyodbc.Error as e:
        print(e)
        return None


def obtener_colores_de_articulos_bd():
    server = '192.168.200.32'
    database = 'VEBD'
    username = 'logic'
    password = '#Obelix*.99'

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = conn.cursor()

        consulta = ("""
                        SELECT DISTINCT c.Color_ ,a.CodigoAlternativo FROM MovimientoStock ms
                        INNER JOIN Colores_ c ON ms.CodigoColor_ = c.CodigoColor_
                        INNER JOIN Articulos a ON ms.CodigoArticulo = a.CodigoArticulo
                        WHERE ms.CodigoEmpresa = 997
                    """)

        cursor.execute(consulta)

        datos_desde_bd = cursor.fetchall()

        datos_json = []
        for fila in datos_desde_bd:
            datos_json.append({
                "codAlternativo": fila[1],
                "nombreAtrib": "COLORES",
                "name": fila[0]
            })

        conn.close()
        return datos_json

    except pyodbc.Error as e:
        print(e)
        return None


def obtener_tallas_de_articulos_bd():
    server = '192.168.200.32'
    database = 'VEBD'
    username = 'logic'
    password = '#Obelix*.99'

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = conn.cursor()

        # consulta = (f"""
        #                 SELECT DISTINCT gt.DescripcionGrupoTalla_, ms.CodigoTalla01_, a.CodigoAlternativo
        #                 FROM MovimientoStock ms
        #                 INNER JOIN Articulos a 
        #                     ON ms.CodigoArticulo = a.CodigoArticulo
        #                     AND a.CodigoEmpresa = ms.CodigoEmpresa
        #                 INNER JOIN GrupoTallas_ gt 
        #                     ON ms.GrupoTalla_ = gt.GrupoTalla_
        #                     AND gt.CodigoEmpresa = ms.CodigoEmpresa
        #                 WHERE ms.CodigoEmpresa = 997 and a.CodigoAlternativo <> ''
        #             """)
        
        consulta = (f"""
                    SELECT DISTINCT gt.DescripcionGrupoTalla_, ms.CodigoTalla01_, a.CodigoAlternativo,
                        CASE WHEN gt.DescripcionGrupoTalla_ = 'TALLAJE LETRAS' 
                            THEN 
                                CASE ms.CodigoTalla01_
                                    WHEN 'XS' THEN 1
                                    WHEN 'S' THEN 2
                                    WHEN 'SM' THEN 3
                                    WHEN 'M' THEN 4
                                    WHEN 'ML' THEN 5
                                    WHEN 'L' THEN 6
                                    WHEN 'LXL' THEN 7
                                    WHEN 'XL' THEN 8
                                    WHEN '2XL' THEN 9
                                    WHEN '3XL' THEN 10
                                    WHEN '4XL' THEN 11
                                    WHEN '5XL' THEN 12
                                    WHEN '6XL' THEN 13
                                    WHEN '7XL' THEN 14
                                    WHEN '8XL' THEN 15
                                    WHEN '9XL' THEN 16
                                    WHEN '10XL' THEN 17
                                    WHEN '11XL' THEN 18
                                    WHEN '12XL' THEN 19
                                    WHEN '13XL' THEN 20
                                    ELSE 21
                                END 
                            ELSE TRY_CAST(ms.CodigoTalla01_ AS INT)
                        END AS OrdenTalla
                    FROM MovimientoStock ms
                    INNER JOIN Articulos a ON ms.CodigoArticulo = a.CodigoArticulo AND a.CodigoEmpresa = ms.CodigoEmpresa
                    INNER JOIN GrupoTallas_ gt ON ms.GrupoTalla_ = gt.GrupoTalla_ AND gt.CodigoEmpresa = ms.CodigoEmpresa
                    WHERE ms.CodigoEmpresa = 997 AND a.CodigoAlternativo <> ''
                    ORDER BY gt.DescripcionGrupoTalla_,OrdenTalla,ms.CodigoTalla01_
                    """)

        cursor.execute(consulta)

        datos_desde_bd = cursor.fetchall()

        datos_json = []
        for fila in datos_desde_bd:
            #nombre_atributo = obtener_nombre_atributo(fila[0])
            datos_json.append({
                "codAlternativo": fila[2],
                "nombreAtrib": fila[0],
                "color": fila[1]
            })
        # print(f"""************* datos_json: {datos_json}""")
        conn.close()
        return datos_json

    except pyodbc.Error as e:
        print(e)
        return None


def obtener_stock_variaciones_bd():
    server = '192.168.200.32'
    database = 'VEBD'
    username = 'logic'
    password = '#Obelix*.99'

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = conn.cursor()

        consulta = (f"""
				SELECT a.CodigoAlternativo, Color_ ,CodigoTalla01_, a.PrecioVenta, sum(acs.UnidadSaldo)
                FROM AcumuladoStock acs INNER JOIN Articulos a ON acs.CodigoArticulo = a.CodigoArticulo 
                INNER JOIN Colores_ c ON acs.CodigoColor_ = c.CodigoColor_ WHERE acs.CodigoEmpresa = 997 
                AND Ejercicio=year(getdate()) AND Periodo=99
                and a.CodigoAlternativo <> '' and UnidadSaldo > 0
				group by a.CodigoAlternativo, Color_ ,CodigoTalla01_, a.PrecioVenta
            """)

        cursor.execute(consulta)

        datos_desde_bd = cursor.fetchall()

        datos_json = []
        for fila in datos_desde_bd:
            datos_json.append({
                "codAlternativo": safe_int(fila[0]),
                "codTalla": fila[2],
                "color": fila[1],
                "unidades": str(fila[4]),
                "precio": str(fila[3])
            })

        conn.close()
        return datos_json

    except pyodbc.Error as e:
        print(e)
        return None


def safe_int(value):
    if value and value.isdigit():
        return int(value)
    else:
        return None


# Función principal para importar atributos
def importar_atributos(wc_api):
    if wc_api is None:
        print("No se pudo obtener la API de WooCommerce. Verifica la conexión.")
        return

    atributos_bd = obtener_atributos_bd()

    if atributos_bd == None:
        print("No se pudo obtener los atributos de la base de datos.")
        return

    atributos_wooc = get_with_retries('products/attributes', wc_api)

    for atributo_bd in atributos_bd:
        nombre_atributo_bd = atributo_bd['name']
        existe_en_woocomerce = any(atributo_wooc["name"] == nombre_atributo_bd for atributo_wooc in atributos_wooc)

        if existe_en_woocomerce:
            print(f'El atributo "{nombre_atributo_bd}" ya existe en WooCommerce.')
            atributo_id = next((atributo_wooc["id"] for atributo_wooc in atributos_wooc if
                                atributo_wooc["name"] == nombre_atributo_bd), None)
        else:
            respuesta_creacion = wc_api.post('products/attributes', atributo_bd)

            if respuesta_creacion.status_code == 201:
                atributo_id = respuesta_creacion.json().get("id")
                print(f'Atributo "{nombre_atributo_bd}" creado exitosamente con ID {atributo_id}.')
            else:
                print(f'Error al crear el atributo "{nombre_atributo_bd}": {respuesta_creacion.json()}')
                continue

        nombre_atributo = atributo_bd.get("name")
        if nombre_atributo == "COLORES":
            importar_terms(wc_api, atributo_id, obtener_terms_colores_bd())
        elif nombre_atributo in ["TALLAJE LETRAS", "PANTALONES", "CINTURONES", "CAMISAS DE VESTIR", "CAMISAS SPORT", "TRAJES", "UNICA"]:
            importar_terms(wc_api, atributo_id, obtener_terms_tallas_bd(nombre_atributo))
        else:
            print(f'Tipo de atributo "{nombre_atributo_bd}" no compatible.')


# Función para importar términos
def importar_terms(wc_api, id_atributo_wooc, terms_bd):
    if wc_api is None:
        print("No se pudo obtener la API de WooCommerce. Verifica la conexión.")
        return

    if terms_bd is None:
        print("No se pudieron obtener los términos de la base de datos.")
        return

    def obtener_todos_los_terminos(api, id_atributo):
        page = 1
        per_page = 100
        all_terms = []

        while True:
            url = f'products/attributes/{id_atributo}/terms?per_page={per_page}&page={page}'
            terms = get_with_retries(url, api)

            if not terms:
                break

            all_terms.extend(terms)
            page += 1

        return all_terms

    terms_wooc = obtener_todos_los_terminos(wc_api, id_atributo_wooc)

    for term in terms_bd:
        nombre_term_bd = term['name']
        existe_en_woocomerce = any(term_wooc["name"] == nombre_term_bd for term_wooc in terms_wooc)

        if existe_en_woocomerce:
            print(f'El término "{nombre_term_bd}" ya existe en WooCommerce.')
        else:
            respuesta_creacion = wc_api.post(f'products/attributes/{id_atributo_wooc}/terms', term)

            if respuesta_creacion.status_code == 201:
                print(f'Término "{nombre_term_bd}" creado exitosamente.')
            else:
                print(f'Error al crear el término "{nombre_term_bd}": {respuesta_creacion.json()}')


# def comprobar_hash(ruta_imagen, ruta_log):
#     with Image.open(ruta_imagen) as img:
#         img_bytes = img.tobytes()
#         hash_obj = hashlib.sha256()
#         hash_obj.update(img_bytes)
#         img_hash = hash_obj.hexdigest()
#
#     if os.path.exists(ruta_log) and os.path.getsize(ruta_log) > 0:
#         with open(ruta_log, 'r') as log_file:
#             try:
#                 log_data = json.load(log_file)
#             except json.JSONDecodeError:
#                 log_data = {}
#     else:
#         log_data = {}
#
#     if img_hash in log_data:
#         print("El hash de la imagen ya está en el log")
#         return True, None
#     else:
#         log_data[img_hash] = ruta_imagen
#         with open(ruta_log, 'w') as log_file:
#             json.dump(log_data, log_file, indent=4)
#
#         url_ftp = subida_img_ftp(ruta_imagen)
#         return False, url_ftp


# def subida_img_ftp(ruta_imagen):
#     servidor_ftp = "sage200cprestashop.com"
#     usuario = "sage200c"
#     contras = "Ty*_q=G4!z2%1"
#     directorio = "/web/wp/img_sage"
#
#     nombre_archivo = os.path.basename(ruta_imagen)
#
#     ftp_path = f"{directorio}/{nombre_archivo}"
#
#     with FTP(servidor_ftp) as ftp:
#         ftp.login(user=usuario, passwd=contras)
#         with open(ruta_imagen, 'rb') as file:
#             ftp.storbinary(f'STOR {ftp_path}', file)
#
#     return f'https://{servidor_ftp}/wp/img_sage/{nombre_archivo}'


def importar_articulos1(wc_api):
    server = '192.168.200.32'
    database = 'VEBD'
    username = 'logic'
    password = '#Obelix*.99'

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password
        )
        cursor = conn.cursor()
        articulos_bd = obtener_articulos_bd()

        if wc_api is None:
            print("No se pudo obtener la API de WooCommerce. Verifica la conexión.")
            return

        if articulos_bd is None:
            print("No se pudieron obtener los artículos de la base de datos.")
            return

        if conn:
            try:
                articulos_wooc = obtener_articulos_woocommerce(wc_api)
                sku_to_id_mapping = {articulo['sku']: articulo['id'] for articulo in articulos_wooc}
                # print(articulos_wooc)

                for articulo1 in articulos_bd:
                    # ruta_imagen = articulo1.get('src')  # Comentado para deshabilitar imágenes
                    # if ruta_imagen:
                    #     if not os.path.exists(ruta_imagen):
                    #         print(f"Archivo no encontrado: {ruta_imagen}")
                    #         continue
                    #
                    #     existe_en_registro, url_imagen = comprobar_hash(ruta_imagen, r'C:\ConectorWoo\log.json')
                    #     if not existe_en_registro and url_imagen:
                    #         url_imagen_ftp = subida_img_ftp(ruta_imagen)
                    #         image_data = {"src": url_imagen_ftp}
                    #         if 'images' not in articulo1:
                    #             articulo1['images'] = []
                    #         articulo1['images'].append(image_data)

                    sku = articulo1['sku']
                    print("SKUUUUUU: " + sku)

                    if sku in sku_to_id_mapping:
                        print(f"El producto '{articulo1['name']}' ya existe en WooCommerce.")
                        continue
                    
                    print(articulo1)
                    response = wc_api.post("products", articulo1)
                    if response.status_code == 201:
                        print(f"Producto '{articulo1['name']}' insertado con éxito.")
                        nuevo_producto = response.json()
                        woocommerce_id = nuevo_producto['id']
                        sku_to_id_mapping[sku] = woocommerce_id
                        print(F"""
                              UPDATE Articulos SET CodigoAlternativo = '{woocommerce_id}',
                                CodigoArancelario = '{obtener_cod_arancelario(sku)}' 
                                WHERE CodigoArticulo = '{sku}' AND CodigoEmpresa = 997
                            """)
                        cursor.execute(f"""
                                UPDATE Articulos SET CodigoAlternativo = '{woocommerce_id}',
                                CodigoArancelario = '{obtener_cod_arancelario(sku)}' 
                                WHERE CodigoArticulo = '{sku}' AND CodigoEmpresa = 997
                            """
                        )
                    else:
                        print(
                            f"Error al insertar el producto '{articulo1['name']}'. Código de estado: {response.status_code}")

                conn.commit()
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)


def set_atributos_articulos(wc_api):
    if wc_api is None:
        print("No se pudo obtener la API de WooCommerce. Verifica la conexión.")
        return

    colores_articulos = obtener_colores_de_articulos_bd()
    tallas_articulos = obtener_tallas_de_articulos_bd()

    if colores_articulos is None:
        print("No se pudieron obtener los colores asignados al artículo en la base de datos.")
        return
    if tallas_articulos is None:
        print("No se pudieron obtener las tallas asignadas al artículo en la base de datos.")
        return

    atributos_wooc = wc_api.get('products/attributes/').json()

    for color in colores_articulos:
        id_articulo_wooc = color['codAlternativo']
        nombre_color = color['name']
        nombre_atrib = color['nombreAtrib']

        atributo_existente = next((atributo for atributo in atributos_wooc if atributo["name"] == nombre_atrib), None)

        if atributo_existente:
            id_atrib = atributo_existente["id"]

            producto = wc_api.get(f'products/{id_articulo_wooc}').json()

            atributo_color = next((attr for attr in producto['attributes'] if attr['id'] == id_atrib), None)

            if atributo_color:
                opciones_color = atributo_color['options']
                if nombre_color not in opciones_color:
                    opciones_color.append(nombre_color)
                    respuesta_actualizacion = wc_api.put(f'products/{id_articulo_wooc}',
                                                            {"attributes": producto['attributes']})
                    if respuesta_actualizacion.status_code == 200:
                        print(f'Atributo de color \'{nombre_color}\' añadido al artículo con id {id_articulo_wooc}')
                    else:
                        print(f'Error al añadir el atributo de color al artículo con id {id_articulo_wooc}')
                else:
                    print(
                        f'La variacion de color \'{nombre_color}\' ya está añadida al artículo con id {id_articulo_wooc}')
            else:
                nuevo_atributo = {
                    "id": id_atrib,
                    "name": nombre_atrib,
                    "visible": True,
                    "variation": True,
                    "options": [nombre_color]
                }
                producto['attributes'].append(nuevo_atributo)
                respuesta_actualizacion = wc_api.put(f'products/{id_articulo_wooc}',
                                                        {"attributes": producto['attributes']})
                if respuesta_actualizacion.status_code == 200:
                    print(f'Atributo de color \'{nombre_color}\' añadido al artículo con id {id_articulo_wooc}')
                else:
                    print(f'Error al añadir el atributo de color al artículo con id {id_articulo_wooc}')
        else:
            print(f'No existe el atributo de color con nombre {nombre_atrib}')

    for talla in tallas_articulos:
        id_articulo_wooc = talla['codAlternativo']
        nombre_talla = talla['color']
        nombre_atrib = talla['nombreAtrib']

        atributo_existente = next((atributo for atributo in atributos_wooc if atributo["name"] == nombre_atrib), None)

        if atributo_existente:
            id_atrib = atributo_existente["id"]

            producto = wc_api.get(f'products/{id_articulo_wooc}').json()

            atributo_talla = next((attr for attr in producto['attributes'] if attr['id'] == id_atrib), None)

            if atributo_talla:
                opciones_talla = atributo_talla['options']
                if nombre_talla not in opciones_talla:
                    opciones_talla.append(nombre_talla)
                    respuesta_actualizacion = wc_api.put(f'products/{id_articulo_wooc}',
                                                            {"attributes": producto['attributes']})
                    if respuesta_actualizacion.status_code == 200:
                        print(f'Atributo de talla \'{nombre_talla}\' añadido al artículo con id {id_articulo_wooc}')
                    else:
                        print(f'Error al añadir el atributo de talla al artículo con id {id_articulo_wooc}')
                else:
                    print(
                        f'La variacion de talla \'{nombre_talla}\' ya está añadida al artículo con id {id_articulo_wooc}')
            else:
                nuevo_atributo = {
                    "id": id_atrib,
                    "name": nombre_atrib,
                    "visible": True,
                    "variation": True,
                    "options": [nombre_talla]
                }
                producto['attributes'].append(nuevo_atributo)
                respuesta_actualizacion = wc_api.put(f'products/{id_articulo_wooc}',
                                                        {"attributes": producto['attributes']})
                if respuesta_actualizacion.status_code == 200:
                    print(f'Atributo de talla \'{nombre_talla}\' añadido al artículo con id {id_articulo_wooc}')
                else:
                    print(
                        f'Error al añadir el atributo de talla \'{nombre_talla}\' al artículo con id {id_articulo_wooc}')
        else:
            print(f'No existe el atributo de talla con nombre {nombre_atrib}')


def set_atributos_articulos2(wc_api):
    if wc_api is None:
        print("No se pudo obtener la API de WooCommerce. Verifica la conexión.")
        return

    colores_articulos = obtener_colores_de_articulos_bd()
    tallas_articulos = obtener_tallas_de_articulos_bd()
    # print(tallas_articulos)
    
    if colores_articulos is None:
        print("No se pudieron obtener los colores asignados al artículo en la base de datos.")
        return
    if tallas_articulos is None:
        print("No se pudieron obtener las tallas asignadas al artículo en la base de datos.")
        return

    atributos_wooc = wc_api.get('products/attributes/').json()

    atributos_wooc_dict = {atributo['name']: atributo for atributo in atributos_wooc}

    productos_para_actualizar = {}

    def procesar_atributo(articulo, nombre_atributo, nombre_opcion):
        id_articulo_wooc = articulo['codAlternativo']

        if id_articulo_wooc not in productos_para_actualizar:
            productos_para_actualizar[id_articulo_wooc] = wc_api.get(f'products/{id_articulo_wooc}').json()

        producto = productos_para_actualizar[id_articulo_wooc]

        if 'attributes' not in producto:
            print(f"El producto {id_articulo_wooc} no tiene atributos definidos.")
            return

        atributo_existente = atributos_wooc_dict.get(nombre_atributo)

        if atributo_existente:
            id_atrib = atributo_existente["id"]
            atributo_producto = next((attr for attr in producto['attributes'] if attr['id'] == id_atrib), None)

            if atributo_producto:
                opciones = atributo_producto['options']
                if nombre_opcion not in opciones:
                    opciones.append(nombre_opcion)
            else:
                nuevo_atributo = {
                    "id": id_atrib,
                    "name": nombre_atributo,
                    "visible": True,
                    "variation": True,
                    "options": [nombre_opcion]
                }
                producto['attributes'].append(nuevo_atributo)
        else:
            print(f"No existe el atributo con nombre {nombre_atributo}. Creando nuevo atributo...")

            nuevo_atributo_data = {
                "name": nombre_atributo,
                "type": "select",
                "order_by": "menu_order",
                "has_archives": False
            }

            respuesta_nuevo_atributo = wc_api.post('products/attributes', nuevo_atributo_data)

            if respuesta_nuevo_atributo.status_code == 201:
                nuevo_atributo_id = respuesta_nuevo_atributo.json().get('id')
                nuevo_atributo = {
                    "id": nuevo_atributo_id,
                    "name": nombre_atributo,
                    "visible": True,
                    "variation": True,
                    "options": [nombre_opcion]
                }
                producto['attributes'].append(nuevo_atributo)
                print(f"Atributo '{nombre_atributo}' creado y añadido al producto.")
            else:
                print(f"Error al crear el nuevo atributo '{nombre_atributo}': {respuesta_nuevo_atributo.json()}")

    def asignar_variacion_por_defecto(producto):
        default_attributes = []
        for atributo in producto.get('attributes', []):
            if 'options' in atributo and atributo['options']:
                default_attributes.append({
                    "id": atributo['id'],
                    "option": atributo['options'][0]  # Asigna la primera opción como predeterminada
                })
        return default_attributes

    for color in colores_articulos:
        procesar_atributo(color, color['nombreAtrib'], color['name'])

    for talla in tallas_articulos:
        procesar_atributo(talla, talla['nombreAtrib'], talla['color'])

    for id_articulo_wooc, producto in productos_para_actualizar.items():
        if 'attributes' not in producto:
            print(f"El producto {id_articulo_wooc} no tiene atributos definidos.")
            continue

        # Asigna la variación por defecto antes de actualizar el producto
        producto['default_attributes'] = asignar_variacion_por_defecto(producto)

        respuesta_actualizacion = wc_api.put(f'products/{id_articulo_wooc}', {
            "attributes": producto['attributes'],
            "default_attributes": producto['default_attributes']  # Incluye las variaciones por defecto
        })

        if respuesta_actualizacion.status_code == 200:
            print(f'Atributos actualizados para el artículo con id {id_articulo_wooc}')
        else:
            print(f'Error al actualizar los atributos para el artículo con id {id_articulo_wooc}')



def set_precio_stock_variaciones(wc_api):
    if wc_api is None:
        print("No se pudo obtener la API de WooCommerce. Verifica la conexión.")
        return

    stock_variaciones_bd = obtener_stock_variaciones_bd()

    if stock_variaciones_bd is None:
        print("No se pudieron obtener los datos de stock y precio de las variaciones desde la base de datos.")
        return

    for variacion_bd in stock_variaciones_bd:
        id_articulo_wooc = variacion_bd['codAlternativo']

        atributos_producto = wc_api.get(f'products/{id_articulo_wooc}').json()['attributes']
        id_color = next((attr['id'] for attr in atributos_producto if attr['name'] == 'COLORES'), None)
        id_talla = next((attr['id'] for attr in atributos_producto if attr['name'] == 'TALLAJE LETRAS'), None)

        cod_talla = variacion_bd['codTalla']
        color = variacion_bd['color']
        unidades = float(variacion_bd['unidades'])
        precio = float(variacion_bd['precio'])

        variaciones_woocommerce = wc_api.get(f'products/{id_articulo_wooc}/variations?per_page=100').json()
        variacion_existente = next((var for var in variaciones_woocommerce if
                                    var['attributes'][0]['option'] == color and var['attributes'][1][
                                        'option'] == cod_talla), None)

        if variacion_existente:
            if float(variacion_existente['regular_price']) != precio or int(
                    variacion_existente['stock_quantity']) != unidades:
                variacion_id = variacion_existente['id']
                variacion_data = {
                    "regular_price": str(precio),
                    "manage_stock": True,
                    "stock_quantity": int(unidades)
                }
                respuesta_actualizacion = wc_api.put(f'products/{id_articulo_wooc}/variations/{variacion_id}', variacion_data)

                if respuesta_actualizacion.status_code == 200:
                    print(
                        f'Variación actualizada correctamente para el artículo {id_articulo_wooc} con talla {cod_talla} y color {color}')
                else:
                    print(
                        f'Error al actualizar la variación para el artículo {id_articulo_wooc} con talla {cod_talla} y color {color}')
                    print(f'Detalle del error: {respuesta_actualizacion.json()}')
            else:
                print(
                    f'El precio y el stock de la variación para el artículo {id_articulo_wooc} con talla {cod_talla} y color {color} son iguales. No se realiza ninguna actualización.')
        else:
            nueva_variacion_data = {
                "regular_price": str(precio),
                "manage_stock": True,
                "stock_quantity": int(unidades),
                "attributes": [
                    {
                        "id": id_color,
                        "name": "COLORES",
                        "option": color
                    },
                    {
                        "id": id_talla,
                        "name": "TALLAJE LETRAS",
                        "option": cod_talla
                    }
                ]
            }
            respuesta_creacion = wc_api.post(f'products/{id_articulo_wooc}/variations?per_page=100', nueva_variacion_data)

            if respuesta_creacion.status_code == 201:
                print(
                    f'Nueva variación creada para el artículo {id_articulo_wooc} con talla {cod_talla} y color {color}')
            else:
                print(
                    f'Error al crear una nueva variación para el artículo {id_articulo_wooc} con talla {cod_talla} y color {color}')
                print(f'Detalle del error: {respuesta_creacion.json()}')


def obtener_grupo_talla_desde_bd(codigo_alternativo):
    server = '192.168.200.32'
    database = 'VEBD'
    username = 'logic'
    password = '#Obelix*.99'

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = conn.cursor()

        consulta = f"""
                        SELECT DISTINCT gt.DescripcionGrupoTalla_
                        FROM Articulos a
                        INNER JOIN MovimientoStock ms ON a.CodigoArticulo = ms.CodigoArticulo
                        INNER JOIN GrupoTallas_ gt ON ms.GrupoTalla_ = gt.GrupoTalla_
                        WHERE gt.CodigoEmpresa = 997
                        AND a.CodigoAlternativo = '{codigo_alternativo}'
                    """

        cursor.execute(consulta)
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]
        else:
            return None

    except pyodbc.Error as e:
        print(e)
        return None
    
def get_with_retries(url, wc_api, retries=3):
    for attempt in range(retries):
        try:
            response = wc_api.get(url)  # No pasar timeout aquí
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ReadTimeout:
            if attempt < retries - 1:
                time.sleep(10)  # Espera 10 segundos antes de reintentar
            else:
                raise
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud: {e}")
            if response.status_code == 404:
                return {}  # Retornar un diccionario vacío si no se encuentra el recurso
            break
    return None  # Retornar None si la solicitud falla después de todos los intentos

        
        
def obtener_variaciones_woocommerce(wc_api, id_articulo_wooc):
    try:
        page = 1
        all_variations = []

        while True:
            response = wc_api.get(f"products/{id_articulo_wooc}/variations", params={"page": page, "per_page": 100})
            if response.status_code != 200:
                print(f"Error al obtener las variaciones del producto {id_articulo_wooc}:", response.json())
                return None

            variations = response.json()
            all_variations.extend(variations)

            headers = response.headers
            if not headers.get("X-WP-TotalPages") or page >= int(headers["X-WP-TotalPages"]):
                break

            page += 1

        return all_variations
    except Exception as e:
        print("Error al obtener variaciones:", e)
        return None


def set_precio_stock_variaciones2(wc_api):
    if wc_api is None:
        print("No se pudo obtener la API de WooCommerce. Verifica la conexión.")
        return

    stock_variaciones_bd = obtener_stock_variaciones_bd()

    if stock_variaciones_bd is None:
        print("No se pudieron obtener los datos de stock y precio de las variaciones desde la base de datos.")
        return

    variaciones_por_articulo = {}
    for variacion in stock_variaciones_bd:
        id_articulo_wooc = variacion['codAlternativo']
        if id_articulo_wooc not in variaciones_por_articulo:
            variaciones_por_articulo[id_articulo_wooc] = []
        variaciones_por_articulo[id_articulo_wooc].append(variacion)

    for id_articulo_wooc, variaciones in variaciones_por_articulo.items():
        producto = get_with_retries(f'products/{id_articulo_wooc}', wc_api)
        if producto is None:
            print(f"Error al obtener el producto {id_articulo_wooc}.")
            continue

        if 'message' in producto:
            print(f"Error al obtener el producto {id_articulo_wooc}: {producto.get('message', 'Desconocido')}")
            continue

        if 'attributes' not in producto:
            print(f"El producto {id_articulo_wooc} no tiene atributos definidos.")
            continue

        id_color = next((attr['id'] for attr in producto['attributes'] if attr['name'] == 'COLORES'), None)

        grupo_talla = obtener_grupo_talla_desde_bd(id_articulo_wooc)
        if grupo_talla is None:
            print(f"No se pudo determinar el grupo de talla para el artículo {id_articulo_wooc}.")
            continue

        id_talla = next((attr['id'] for attr in producto['attributes'] if attr['name'] == grupo_talla), None)

        if id_color is None or id_talla is None:
            print(f"El producto {id_articulo_wooc} no tiene los atributos de color o talla definidos.")
            continue

        # Obtener todas las variaciones con paginación
        variaciones_woocommerce = obtener_variaciones_woocommerce(wc_api, id_articulo_wooc)
        if variaciones_woocommerce is None:
            print(f"Error al obtener las variaciones del producto {id_articulo_wooc}.")
            continue

        variaciones_woocommerce_dict = {}
        for var in variaciones_woocommerce:
            atributos = tuple((attr['name'], attr['option']) for attr in var['attributes'])
            variaciones_woocommerce_dict[atributos] = var
                
        for variacion_bd in variaciones:
            cod_talla = variacion_bd['codTalla']
            color = variacion_bd['color']
            unidades = float(variacion_bd['unidades'])
            precio = float(variacion_bd['precio'])

            clave_variacion = (('COLORES', color), (grupo_talla, cod_talla))

            print(f"CLAVE VARIACION: {clave_variacion}")

            variacion_existente = variaciones_woocommerce_dict.get(clave_variacion)
            
            if variacion_existente:
                if float(variacion_existente['regular_price']) != precio or int(variacion_existente['stock_quantity']) != int(unidades):
                    variacion_id = variacion_existente['id']
                    variacion_data = {
                        "regular_price": str(precio),
                        "manage_stock": True,
                        "stock_quantity": int(unidades)
                    }
                    respuesta_actualizacion = wc_api.put(f'products/{id_articulo_wooc}/variations/{variacion_id}', variacion_data)
                    if respuesta_actualizacion.status_code == 200:
                        print(f'Variación actualizada correctamente para el artículo {id_articulo_wooc} con talla {cod_talla} y color {color}')
                    else:
                        print(f'Error al actualizar la variación para el artículo {id_articulo_wooc} con talla {cod_talla} y color {color}')
                        print(f'Detalle del error: {respuesta_actualizacion.json()}')
                else:
                    print(f'El precio y el stock de la variación para el artículo {id_articulo_wooc} con talla {cod_talla} y color {color} son iguales. No se realiza ninguna actualización.')
            else:
                nueva_variacion_data = {
                    "regular_price": str(precio),
                    "manage_stock": True,
                    "stock_quantity": int(unidades),
                    "attributes": [
                        {
                            "id": int(id_color),  # Asegurarse de que el ID es entero
                            "name": "COLORES",
                            "option": color
                        },
                        {
                            "id": int(id_talla),  # Asegurarse de que el ID es entero
                            "name": grupo_talla,
                            "option": cod_talla
                        }
                    ]
                }
                respuesta_creacion = wc_api.post(f'products/{id_articulo_wooc}/variations', nueva_variacion_data)

                if respuesta_creacion.status_code == 201:
                    print(f'Nueva variación creada para el artículo {id_articulo_wooc} con talla {cod_talla} y color {color}')
                else:
                    print(f'Error al crear una nueva variación para el artículo {id_articulo_wooc} con talla {cod_talla} y color {color}')
                    print(f'Detalle del error: {respuesta_creacion.json()}')



def actualizar_articulos(wc_api):
    server = '192.168.200.32'
    database = 'VEBD'
    username = 'logic'
    password = '#Obelix*.99'

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

        cursor = conn.cursor()
        articulos_sage = obtener_articulos_bd()

        if not articulos_sage:
            print("No se pudieron obtener los artículos de Sage.")
            return

        for articulo_sage in articulos_sage:
            cod_articulo_sage = int(articulo_sage["codAlternativo"])
            nombre_sage = articulo_sage["name"]
            precio_sage = articulo_sage["regular_price"]
            descripcion_sage = articulo_sage["description"]
            descripcion_corta_sage = articulo_sage["short_description"]
            url_sage = articulo_sage["src"]

            print("url_sage: " + url_sage)

            try:
                response = wc_api.get(f"products/{cod_articulo_sage}")

                if response.status_code == 200:
                    articulo_wooc = response.json()
                else:
                    print(f"El producto con ID {cod_articulo_sage} no existe en WooCommerce.")
                    continue

                id_subfamilia_bd = obtener_cod_arancelario(articulo_sage["sku"])

                print(id_subfamilia_bd)

                cursor.execute(f"""
                    SELECT TOP 1 CodigoArancelario FROM Familias WHERE CodigoSubfamilia = '**********'  
                    AND CodigoEmpresa = 997 AND CodigoArancelario = (
                        SELECT TOP 1 CodigoArancelario FROM Familias WHERE CodigoFamilia = (
                            SELECT TOP 1 CodigoFamilia FROM Familias 
                            WHERE CodigoArancelario = '{id_subfamilia_bd}' AND CodigoEmpresa = 997
                        ) AND CodigoSubfamilia = '**********' AND CodigoEmpresa = 997)
                    """
                )

                id_familia_bd = cursor.fetchone()

                id_familia_bd = id_familia_bd[0] if id_familia_bd else None

                id_wooc = articulo_wooc.get("id")
                nombre_wooc = articulo_wooc.get("name")
                precio_wooc = articulo_wooc.get("regular_price")
                descripcion_wooc = articulo_wooc.get("description")
                descripcion_corta_wooc = articulo_wooc.get("short_description")
                familias_wooc = articulo_wooc.get("categories")
                id_familia_wooc = familias_wooc[0].get("id")

                if len(familias_wooc) >= 2:
                    id_subfamilia_wooc = familias_wooc[1].get("id")
                else:
                    id_subfamilia_wooc = 0

                if (id_wooc == cod_articulo_sage and nombre_wooc != nombre_sage or precio_wooc != precio_sage or
                        descripcion_wooc != descripcion_sage or descripcion_corta_wooc != descripcion_corta_sage or
                        id_familia_wooc != id_familia_bd and id_subfamilia_wooc != id_subfamilia_bd):
                    try:
                        # Filtrar categorías no válidas
                        categorias_validas = []
                        if id_familia_bd and isinstance(id_familia_bd, int):
                            categorias_validas.append({"id": id_familia_bd})
                        if id_subfamilia_bd and isinstance(id_subfamilia_bd, int):
                            categorias_validas.append({"id": id_subfamilia_bd})

                        articulo_data = {
                            "name": nombre_sage, "slug": nombre_sage,
                            "regular_price": precio_sage, "description": descripcion_sage,
                            "short_description": descripcion_corta_sage,
                            "categories": categorias_validas
                        }

                        # Control de la imagen
                        # existe_en_registro, url_imagen = comprobar_hash(url_sage, r'C:\ConectorWoo\log.json')
                        # if existe_en_registro:
                        #     # Si el hash ya existe, usar la URL existente en el log
                        #     url_imagen_ftp = subida_img_ftp(url_sage)
                        # else:
                        #     # Si el hash no existe, subir la imagen y obtener la nueva URL
                        #     url_imagen_ftp = url_imagen
                        # print(url_imagen_ftp)
                        # if url_imagen_ftp:
                        #     image_data = {
                        #         "src": url_imagen_ftp,
                        #     }
                        #     articulo_data["images"] = [image_data]

                        response_put = wc_api.put(f"products/{cod_articulo_sage}", articulo_data)
                        if response_put.status_code == 200:
                            print(f"Artículo actualizado en WooCommerce: {nombre_sage}")
                        else:
                            print(
                                f"Error al actualizar el artículo en WooCommerce. Código de estado: {response_put.status_code}")
                            print(f"Detalle del error: {response_put.json()}")
                    except Exception as e:
                        print(f"Error al actualizar el artículo en WooCommerce: {e}")
            except Exception as e:
                print(f"Error al obtener el artículo de WooCommerce con ID {cod_articulo_sage}: {e}")
    except Exception as e:
        print(e)


# while True:
importar_articulos1(get_wc_api())
print("TERMINA 1")
importar_atributos(get_wc_api())
print("TERMINA 2")
set_atributos_articulos2(get_wc_api())
print("TERMINA 3")
set_precio_stock_variaciones2(get_wc_api())
print("TERMINA 4")
actualizar_articulos(get_wc_api())
print("TERMINA 5")