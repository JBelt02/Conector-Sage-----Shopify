import json
import requests

# Token de acceso API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

# Código del metafield que deseas usar para eliminar el producto
codigo_metafield = 'CHAQUETA-DEFAULTTT'

# URL de la API de Shopify para obtener todos los productos
url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products.json"

# Encabezados de la solicitud
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": TOKEN
}

# Realizar la solicitud GET para obtener todos los productos
response = requests.get(url, headers=headers)

if response.status_code == 200:
    products = response.json().get("products", [])
    found_product = None

    # Iterar a través de los productos para encontrar el que coincide con el metafield "codigo"
    for product in products:
        # Obtener los metafields del producto
        metafields_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products/{product['id']}/metafields.json"
        metafields_response = requests.get(metafields_url, headers=headers)

        if metafields_response.status_code == 200:
            metafields = metafields_response.json().get("metafields", [])

            # Verificar si algún metafield coincide con "codigo_metafield"
            for metafield in metafields:
                if metafield.get("key") == "codigo" and metafield.get("value") == codigo_metafield:
                    found_product = product
                    break

        if found_product:
            break

    if found_product:
        product_id = found_product["id"]

        # URL para eliminar el producto
        delete_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products/{product_id}.json"
        
        # Realizar la solicitud DELETE para eliminar el producto
        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code == 200:
            print("Producto eliminado con éxito.")
        else:
            print("Error al eliminar el producto:")
            print(delete_response.status_code)
            print(delete_response.text)
    else:
        print(f"No se encontró ningún producto con el código: {codigo_metafield}.")
else:
    print("Error al obtener los productos:")
    print(response.status_code)
    print(response.text)
