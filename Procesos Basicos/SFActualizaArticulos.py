import requests
import pyodbc
import json

SHOPIFY_API_KEY = 'tu_api_key'
SHOPIFY_PASSWORD = 'tu_password'
SHOP_NAME = 'tu_shop_name'
API_VERSION = '2023-10'
# Ejemplo de URL de Shopify para interactuar con productos
SHOPIFY_URL = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products.json"


# Conexión a la base de datos de Sage 200 (si usas SQL Server)
def get_products_from_sage():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=tu_servidor;DATABASE=tu_bd_sage;UID=tu_usuario;PWD=tu_contraseña')
    cursor = conn.cursor()
    
    query = """
        SELECT ProductID, ProductName, Price, StockLevel, SKU
        FROM Products
    """
    cursor.execute(query)
    
    products = cursor.fetchall()
    conn.close()
    
    return products


# Obtenemos los productos de Sage
productos_sage = get_products_from_sage()

# Mostrar productos
for producto in productos_sage:
    print(producto)


# Función para crear producto en Shopify
def create_product_in_shopify(product_data):
    url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products.json"
    
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=product_data)
    
    if response.status_code == 201:
        print(f"Producto creado exitosamente: {product_data['product']['title']}")
    else:
        print(f"Error al crear el producto: {response.json()}")

# Mapea los datos del producto de Sage a los datos que espera Shopify
def map_product_sage_to_shopify(product_sage):
    return {
        "product": {
            "title": product_sage.ProductName,
            "body_html": "<p>Descripción del producto aquí.</p>",
            "vendor": "Tu Marca",
            "product_type": "Categoría",
            "variants": [
                {
                    "price": str(product_sage.Price),
                    "sku": product_sage.SKU,
                    "inventory_quantity": product_sage.StockLevel
                }
            ]
        }
    }


# Actualiza un producto en Shopify
def update_product_in_shopify(product_id, product_data):
    url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products/{product_id}.json"
    
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.put(url, headers=headers, json=product_data)
    
    if response.status_code == 200:
        print(f"Producto actualizado exitosamente: {product_data['product']['title']}")
    else:
        print(f"Error al actualizar el producto: {response.json()}")


def get_all_shopify_products():
    url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products.json"
    headers = {
        "Content-Type": "application/json"
    }
    
    products = []
    params = {
        "limit": 250  # Shopify permite un máximo de 250 productos por página
    }
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            products.extend(data["products"])
            
            # Verificamos si hay más páginas de productos
            if "next" in response.links:
                url = response.links["next"]["url"]
            else:
                break
        else:
            print(f"Error al obtener los productos: {response.json()}")
            break
    
    # Crear un diccionario de productos donde la clave es el SKU
    products_dict = {variant['sku']: product for product in products for variant in product['variants']}
    
    return products_dict

# Obtener todos los productos de Shopify y almacenarlos por SKU
productos_shopify = get_all_shopify_products()


def sync_products_to_shopify(product_sage):
    sku = product_sage.SKU
    
    # Si el producto ya existe en Shopify, lo actualizamos
    if sku in productos_shopify:
        product_shopify = productos_shopify[sku]
        product_id = product_shopify['id']
        
        # Mapea los datos de Sage al formato esperado por Shopify
        product_data = map_product_sage_to_shopify(product_sage)
        
        # Actualizamos el producto existente
        update_product_in_shopify(product_id, product_data)
    else:
        # Si no existe, lo creamos
        product_data = map_product_sage_to_shopify(product_sage)
        create_product_in_shopify(product_data)

# Iterar sobre los productos de Sage y sincronizarlos con Shopify
for product_sage in productos_sage:
    sync_products_to_shopify(product_sage)