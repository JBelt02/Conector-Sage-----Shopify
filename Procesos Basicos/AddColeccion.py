import json
import requests

# Token de acceso API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

# Headers para las solicitudes
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": TOKEN
}

# Función para crear colecciones manuales
def crear_coleccion_manual(titulo, descripcion, handle):
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/custom_collections.json"
    data = {
        "custom_collection": {
            "title": titulo,
            "body_html": descripcion,
            "handle": handle,
            "published": True
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response

# Función para crear colecciones automáticas
def crear_coleccion_automatica(titulo, reglas):
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/smart_collections.json"
    data = {
        "smart_collection": {
            "title": titulo,
            "rules": reglas,
            "published": True
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response

# # Ejemplo de creación de colecciones
# coleccion_manual = crear_coleccion_manual("Nuevas Llegadas", "<strong>Descubre las últimas tendencias.</strong>", "nuevas-llegadas")
# if coleccion_manual.status_code == 201:
#     print("Colección manual creada con éxito:", coleccion_manual.json())
# else:
#     print("Error al crear colección manual:", coleccion_manual.content)

reglas_automatica = [
    {
        "column": "tag",
        "relation": "equals",
        "condition": "Hombre"
    }
]
coleccion_automatica = crear_coleccion_automatica("Ropa de Hombre", reglas_automatica)
if coleccion_automatica.status_code == 201:
    print("Colección automática creada con éxito:", coleccion_automatica.json())
else:
    print("Error al crear colección automática:", coleccion_automatica.content)
