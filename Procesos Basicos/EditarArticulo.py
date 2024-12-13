import json
import requests

# Token de acceso API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

# Código del artículo que deseas editar
codigo_articulo = 'CHAQUETA-DEFAULT'

# Encabezados de la solicitud
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": TOKEN
}

# URL de la API de Shopify para obtener los productos con sus metafields
url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products.json?fields=id"

# Realizar la solicitud GET para obtener todos los productos
response = requests.get(url, headers=headers)

if response.status_code == 200:
    products = response.json().get("products", [])
    found_product = None

    # Iterar a través de los productos para buscar el que tenga el metafield "codigo"
    for product in products:
        product_id = product["id"]

        # Obtener los metafields del producto
        metafields_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products/{product_id}/metafields.json"
        metafields_response = requests.get(metafields_url, headers=headers)

        if metafields_response.status_code == 200:
            metafields = metafields_response.json().get("metafields", [])

            # Buscar el metafield con key "codigo" y valor "CHAQUETA-DEFAULT"
            for metafield in metafields:
                if metafield.get("key") == "codigo" and metafield.get("value") == codigo_articulo:
                    found_product = product
                    break

        # Si encontramos el producto, salimos del bucle
        if found_product:
            break

    if found_product:
        product_id = found_product["id"]  # ID del producto que se va a editar

        # Aquí puedes hacer las modificaciones necesarias en el producto
        updated_product_payload = {
            "product": {
                "id": product_id,
                "title": "Nueva Chaqueta de Inviernooo",  # Nuevo título del producto
                "body_html": "<strong>Chaqueta acolchada ideal para el invierno actualizada.</strong>",  # Nueva descripción
                "vendor": "Moda Invierno Actualizada",  # Nuevo vendedor
                "product_type": "Chaquetas",  # Tipo de producto (opcional)
                # "tags": "invierno, chaqueta, moda, nueva"  # Nuevas etiquetas
                # Puedes agregar más campos según sea necesario
            }
        }

        # URL para actualizar el producto
        update_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products/{product_id}.json"
        
        # Realizar la solicitud PUT para actualizar el producto
        update_response = requests.put(update_url, json=updated_product_payload, headers=headers)

        if update_response.status_code == 200:
            print("Producto actualizado con éxito.")
            print(update_response.json()) 
        else:
            print("Error al actualizar el producto:")
            print(update_response.status_code)
            print(update_response.text)
    else:
        print(f"No se encontró ningún producto con el codigo: {codigo_articulo}.")
else:
    print("Error al obtener los productos:")
    print(response.status_code)
    print(response.text)
