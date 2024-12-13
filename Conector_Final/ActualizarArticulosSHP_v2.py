import pyodbc
import requests
import time

# Shopify API Configuración
SHOP_NAME = "hx8nsv-30"
API_TOKEN = "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"
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": API_TOKEN
}

# Conexión a SQL Server
def obtener_conexion_sql():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=VESAGE01;"
        "DATABASE=VEBD;"
        "UID=logic;"
        "PWD=#Obelix*.99"
    )
    return conn

# Obtener datos de artículos
def obtener_datos_articulos():
    query = """
    SELECT TOP 5
        a.CodigoArticulo AS SKU,
        a.DescripcionArticulo AS NombreArticulo,
        a.PrecioVenta,
        a.PrecioVentaconIVA1,
        a.CodigoFamilia,
        a.CodigoSubfamilia,
        UPPER(a.CodigoSubfamilia) AS SubfamiliaMayusculas,
        f.Descripcion AS NombreFamilia
    FROM Articulos a
    LEFT JOIN Familias f 
        ON a.CodigoFamilia = f.CodigoFamilia 
        AND f.CodigoSubfamilia = '**********'
        AND f.CodigoEmpresa = a.CodigoEmpresa
    WHERE a.CodigoEmpresa = 997
    """
    conn = obtener_conexion_sql()
    cursor = conn.cursor()
    cursor.execute(query)
    datos = cursor.fetchall()
    conn.close()
    return datos

# Obtener combinaciones de tallas y colores
def obtener_combinaciones_articulo(sku):
    combinaciones = []
    try:
        conn = obtener_conexion_sql()
        cursor = conn.cursor()

        query = """
        SELECT 
            a.CodigoArticulo, 
            c.Color_ AS NombreColor, 
            a.CodigoTalla01_, 
            SUM(a.UnidadSaldo) AS UnidadSaldo
        FROM 
            AcumuladoStock a
        LEFT JOIN 
            Colores_ c ON a.CodigoColor_ = c.CodigoColor_
        WHERE 
            a.CodigoEmpresa = 997 
            AND a.Periodo = 99 
            AND a.Ejercicio = YEAR(GETDATE()) 
            AND a.CodigoArticulo = ?
        GROUP BY 
            a.CodigoArticulo, 
            a.CodigoColor_, 
            c.Color_, 
            a.CodigoTalla01_
        HAVING 
            SUM(a.UnidadSaldo) > 0
        """
        cursor.execute(query, sku)
        combinaciones = [
            {
                "color": fila[1],
                "talla": fila[2],
                "stock": int(fila[3])
            }
            for fila in cursor.fetchall()
        ]
        conn.close()
    except pyodbc.Error as e:
        print(f"Error al obtener combinaciones para el artículo {sku}: {e}")
    return combinaciones

# Crear un producto en Shopify
def crear_producto_shopify(datos_producto, variantes):
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products.json"

    # Crear etiquetas (familia y subfamilia)
    etiquetas = [datos_producto['NombreFamilia']]
    if datos_producto['SubfamiliaMayusculas']:
        etiquetas.append(datos_producto['SubfamiliaMayusculas'])

    # Crear el payload para el producto
    payload = {
        "product": {
            "title": datos_producto['NombreArticulo'],
            "body_html": datos_producto['NombreArticulo'],
            "vendor": "Automático",
            "product_type": "General",
            "tags": etiquetas,
            "options": [
                {"name": "Color", "values": list({variante["color"] for variante in variantes})},
                {"name": "Talla", "values": list({variante["talla"] for variante in variantes})}
            ],
            "variants": [
                {
                    "option1": variante["color"],
                    "option2": variante["talla"],
                    "price": float(datos_producto['PrecioVentaconIVA1']),
                    "sku": f"{datos_producto['SKU']}-{variante['color']}-{variante['talla']}",
                    "inventory_quantity": variante["stock"],
                    "inventory_management": "shopify"
                }
                for variante in variantes
            ]
        }
    }

    # Enviar la solicitud
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        print(f"Producto '{datos_producto['NombreArticulo']}' creado exitosamente.")
        return True
    else:
        print(f"Error al crear el producto '{datos_producto['NombreArticulo']}': {response.status_code} - {response.text}")
        return False

# Verificar si el producto ya existe en Shopify
def verificar_producto_existente(sku):
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products.json?fields=id,variants&limit=250"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        productos = response.json().get('products', [])
        for producto in productos:
            for variante in producto.get('variants', []):
                if variante['sku'] == sku:
                    return True
    return False

# Proceso Principal
def subir_productos_a_shopify():
    datos_articulos = obtener_datos_articulos()

    for articulo in datos_articulos:
        datos_producto = {
            "SKU": articulo[0],
            "NombreArticulo": articulo[1],
            "PrecioVenta": articulo[2],
            "PrecioVentaconIVA1": articulo[3],
            "CodigoFamilia": articulo[4],
            "CodigoSubfamilia": articulo[5],
            "SubfamiliaMayusculas": articulo[6],
            "NombreFamilia": articulo[7]
        }

        # Verificar si el producto ya existe
        if verificar_producto_existente(datos_producto['SKU']):
            print(f"El producto con SKU '{datos_producto['SKU']}' ya existe en Shopify. Se omite.")
            continue

        # Obtener variantes del artículo (tallas y colores)
        combinaciones = obtener_combinaciones_articulo(datos_producto['SKU'])

        # Crear el producto
        if combinaciones:
            creado = crear_producto_shopify(datos_producto, combinaciones)
            if creado:
                print(f"Producto '{datos_producto['NombreArticulo']}' subido exitosamente con variantes.")
            else:
                print(f"Error al subir el producto '{datos_producto['NombreArticulo']}' con variantes.")
        else:
            print(f"El producto '{datos_producto['NombreArticulo']}' no tiene variantes disponibles. Se omite.")

        # Pausa para evitar límite de API (2 requests por segundo)
        time.sleep(0.6)

# Ejecutar el proceso
if __name__ == "__main__":
    subir_productos_a_shopify()
