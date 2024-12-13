import json
import requests

# Token de acceso API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

# ID del producto al que pertenece la variante
product_id = '9650239471959'  # Reemplaza esto con el ID del producto específico

# SKU de la variante que deseas eliminar
sku_variante = 'CHAQUETA-VERDE-M'

# URL de la API de Shopify para obtener las variantes del producto específico
url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products/{product_id}/variants.json"

# Encabezados de la solicitud
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": TOKEN
}

# Realizar la solicitud GET para obtener las variantes del producto específico
response = requests.get(url, headers=headers)

if response.status_code == 200:
    variants = response.json().get("variants", [])
    found_variant = None

    # Buscar la variante con el SKU especificado
    for variant in variants:
        if variant.get("sku") == sku_variante:
            found_variant = variant
            break

    if found_variant:
        variant_id = found_variant["id"]

        # URL para eliminar la variante específica
        delete_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/variants/{variant_id}.json"

        # Realizar la solicitud DELETE para eliminar la variante
        delete_response = requests.delete(delete_url, headers=headers)

        if delete_response.status_code == 200:
            print("Variante eliminada con éxito.")
        else:
            print("Error al eliminar la variante:")
            print(delete_response.status_code)
            print(delete_response.text)
    else:
        print(f"No se encontró ninguna variante con el SKU: {sku_variante} en el producto {product_id}.")
else:
    print("Error al obtener las variantes del producto:")
    print(response.status_code)
    print(response.text)
