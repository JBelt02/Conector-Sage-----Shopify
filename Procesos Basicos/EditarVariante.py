import json
import requests

# Token de acceso API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

# URL de la API de Shopify para obtener todas las variantes
variants_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/variants.json"

# Encabezados de la solicitud
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": TOKEN
}

# SKU de la variante que deseas editar
sku_a_editar = "CHAQUETA-VERDE-M" 

# Nuevos valores que deseas establecer
nuevos_datos_variante = {
    "price": "39.99",  
    "inventory_quantity": 25
    
}

# Obtener todas las variantes
response = requests.get(variants_url, headers=headers)

if response.status_code == 200:
    variants = response.json().get("variants", [])
    variante_encontrada = None

    # Buscar la variante por SKU
    for variant in variants:
        if variant["sku"] == sku_a_editar:
            variante_encontrada = variant
            break

    if variante_encontrada:
        # Construir la URL para editar la variante
        variant_id = variante_encontrada["id"]
        update_variant_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/variants/{variant_id}.json"

        # Preparar los datos de la variante para la actualización
        update_payload = {
            "variant": {
                "id": variant_id,
                **nuevos_datos_variante  # Agregar nuevos datos
            }
        }

        # Realizar la solicitud PUT para actualizar la variante
        update_response = requests.put(update_variant_url, headers=headers, json=update_payload)

        if update_response.status_code == 200:
            print(f"Variante actualizada con éxito: {update_response.json()}")
        else:
            print(f"Error al actualizar la variante: {update_response.content}")
    else:
        print(f"No se encontró ninguna variante con SKU: {sku_a_editar}")
else:
    print(f"Error al obtener las variantes: {response.content}")
