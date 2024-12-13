import json
import requests

# Token de acceso API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

# ID del cliente que deseas eliminar
cliente_id = '8406962897239'  # Reemplaza con el ID real del cliente

# URL de la API de Shopify para eliminar un cliente
url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/customers/{cliente_id}.json"

# Realizar la solicitud DELETE para eliminar el cliente
response = requests.delete(url, headers={"X-Shopify-Access-Token": TOKEN})

if response.status_code == 200:
    print(f"Cliente con ID {cliente_id} eliminado con éxito.")
else:
    # Imprimir la respuesta completa para depuración
    print(f"Error al eliminar el cliente: {response.status_code}")
    print(response.json())  # Esto mostrará el mensaje de error y la información devuelta por la API
