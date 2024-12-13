import json
import requests

# Token de acceso API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

# ID del cliente que deseas editar
cliente_id = '8406927573335'  # Reemplaza con el ID real del cliente

# URL de la API de Shopify para editar un cliente
url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/customers/{cliente_id}.json"

# Datos del cliente a editar(Importante , email y phone no se pueden editar si no los cambias , ya que detectara como que quieres añadir lo mismo que ya tiene 
# y te dira que ya existe )
datos_cliente_editados = {
    "customer": {
        "first_name": "PEPE",  # Nuevo nombre
        "last_name": "Pérez",  # Nuevo apellido
        # "email": "juan.perez03@example.com",  # Nuevo correo electrónico
        # "phone": "744608670",  # Nuevo teléfono
        "addresses": [
            {
                "address1": "123 Calle Principal",  # Nueva dirección
                "city": "Madrid",  # Nueva ciudad
                "province": "Madrid",  # Nueva provincia
                "country": "Spain",  # Nuevo país
                "zip": "28001"  # Nuevo código postal
            }
        ]
    }
}

# Convertir los datos del cliente a JSON
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": TOKEN
}

# Realizar la solicitud PUT para editar el cliente
response = requests.put(url, headers=headers, json=datos_cliente_editados)

if response.status_code == 200:
    cliente_editado = response.json()["customer"]
    print(f"Cliente editado con éxito:")
else:
    # Imprimir la respuesta completa para depuración
    print(f"Error al editar el cliente: {response.status_code}")
    print(response.json())  # Esto mostrará el mensaje de error y la información devuelta por la API
