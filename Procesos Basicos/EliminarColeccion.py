import requests

# Token de acceso API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

# Headers para las solicitudes
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": TOKEN
}

# Función para eliminar una colección manual
def eliminar_coleccion_manual(coleccion_id):
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/custom_collections/{coleccion_id}.json"
    response = requests.delete(url, headers=headers)
    return response

# Función para eliminar una colección automática
def eliminar_coleccion_automatica(coleccion_id):
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/smart_collections/{coleccion_id}.json"
    response = requests.delete(url, headers=headers)
    return response

# Ejemplo de eliminación de colecciones
# coleccion_manual_id = 1234567890  # Reemplaza con el ID de la colección manual a eliminar
# respuesta_manual = eliminar_coleccion_manual(coleccion_manual_id)
# if respuesta_manual.status_code == 200:
#     print("Colección manual eliminada con éxito.")
# else:
#     print("Error al eliminar colección manual:", respuesta_manual.content)

coleccion_automatica_id = 641565163863  # Reemplaza con el ID de la colección automática a eliminar
respuesta_automatica = eliminar_coleccion_automatica(coleccion_automatica_id)
if respuesta_automatica.status_code == 200:
    print("Colección automática eliminada con éxito.")
else:
    print("Error al eliminar colección automática:", respuesta_automatica.content)
