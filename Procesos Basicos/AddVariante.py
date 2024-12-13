import json
import requests

# Token de acceso API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

# Encabezados de la solicitud
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": TOKEN
}

def crear_variante(product_id, nueva_variante):
    # URL de la API de Shopify para añadir una variante a un producto
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products/{product_id}/variants.json"
    
    # Realizar la solicitud POST para añadir la nueva variante
    response = requests.post(url, headers=headers, json=nueva_variante)
    
    if response.status_code == 201:
        variante_creada = response.json()["variant"]
        print(f"Variante creada con éxito: {variante_creada}")
        return variante_creada
    else:
        print(f"Error al crear la variante: {response.status_code}")
        print(response.json())
        return None

def subir_imagen_producto(product_id, image_src):
    # Subir la imagen al producto
    image_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products/{product_id}/images.json"
    data = {
        "image": {
            "src": image_src
        }
    }
    response = requests.post(image_url, json=data, headers=headers)
    if response.status_code == 201:
        nueva_imagen = response.json()["image"]
        print(f"Imagen subida con éxito. ID de la imagen: {nueva_imagen['id']}")
        return nueva_imagen
    else:
        print(f"Error al subir la imagen: {response.content}")
        return None

def asignar_imagen_a_variante(variant_id, image):
    # Asignar la imagen a la variante (actualizando los variant_ids)
    update_image_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products/{image['product_id']}/images/{image['id']}.json"
    
    # Los variant_ids se pasan como una lista que contiene el ID de la variante
    data = {
        "image": {
            "id": image["id"],
            "variant_ids": [variant_id]  # Asignar la imagen a la variante
        }
    }
    response = requests.put(update_image_url, json=data, headers=headers)
    if response.status_code == 200:
        print(f"Imagen asignada a la variante {variant_id} con éxito.")
    else:
        print(f"Error al asignar la imagen a la variante: {response.content}")

def agregar_variante_con_imagen(product_id, nueva_variante, image_src):
    # Crear la variante
    variante = crear_variante(product_id, nueva_variante)
    if not variante:
        return

    # Subir la imagen si es necesario
    image = subir_imagen_producto(product_id, image_src)
    if image:
        # Asignar la imagen a la variante recién creada
        asignar_imagen_a_variante(variante["id"], image)

# Datos de la nueva variante
nueva_variante = {
    "variant": {
        "option1": "Verde",  # Color u opción 1
        "option2": "M",  # Talla u opción 2
        "price": "49.99",
        "sku": "CHAQUETA-VERDE-M",
        "inventory_quantity": 10,
        "requires_shipping": True,  # Si requiere envío
        "taxable": True  # Si es sujeto a impuestos
    }
}

# ID del producto al que deseas añadir la variante
product_id = "9650239471959"  # Reemplaza esto con el ID del producto

# URL de la imagen para la nueva variante
image_src = "https://m.media-amazon.com/images/I/71vFrglxgrL.jpg"  # URL de la imagen para el color verde

# Llamar a la función para agregar la variante y asociar la imagen
agregar_variante_con_imagen(product_id, nueva_variante, image_src)
