import json
import requests

# Token de acceso API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

# URL de la API de Shopify para crear un cliente
url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/customers.json"

# Datos del nuevo cliente (Shopify tiene validacion por si existe un usuario con el mismo email o telefono) 
nuevo_cliente = {
    "customer": {
        "first_name": "Juanitooo",  # Nombre
        "last_name": "Pérez",  # Apellido
        "email": "juan.perez03@example.com",  # Correo electrónico
        "phone": "744608671",  # Teléfono
        "addresses": [
            {
                "address1": "123 Calle Principal",  # Dirección
                "city": "Madrid",  # Ciudad
                "province": "Madrid",  # Provincia
                "country": "Spain",  # País
                "zip": "28001"  # Código postal
            }
        ]
    }
}

# Convertir el nuevo cliente a JSON
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": TOKEN
}

# Realizar la solicitud POST para crear el nuevo cliente
response = requests.post(url, headers=headers, json=nuevo_cliente)

if response.status_code == 201:
    cliente_creado = response.json()["customer"]
    print(cliente_creado['id'])
    print(f"Cliente creado con éxito:")
else:
    # Imprimir la respuesta completa para depuración
    print(f"Error al crear el cliente: {response.status_code}")
    print(response.json())  # Esto mostrará el mensaje de error y la información devuelta por la API


