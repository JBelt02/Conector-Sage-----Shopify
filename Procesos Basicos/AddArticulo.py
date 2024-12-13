import json
import requests

# Token de acceso API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

# URL de la API de Shopify para crear un producto
url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products.json"

producto = {
    "product": {
        "title": "Chaqueta de Invierno",  # Nombre del producto
        "body_html": "<strong>Chaqueta acolchada ideal para el invierno.</strong>",  # Descripción
        "vendor": "Moda Invierno",  # Vendedor
        "product_type": "Chaquetas",  # Tipo de producto
        "tags": "invierno, chaqueta, moda",  # Etiquetas
        "variants": [
            {
                "option1": "Rojo",  
                "option2": "S",  
                "price": "49.99", 
                "sku": "CHAQUETA-ROJA-S",  
                "inventory_quantity": 20, 
                "requires_shipping": True,  
                "taxable": True  
            },
            {
                "option1": "Rojo",  
                "option2": "M",  
                "price": "49.99",  
                "sku": "CHAQUETA-ROJA-M",  
                "inventory_quantity": 15,  
                "requires_shipping": True,  
                "taxable": True  
            },
            {
                "option1": "Rojo",  
                "option2": "L",  
                "price": "49.99",  
                "sku": "CHAQUETA-ROJA-L",  
                "inventory_quantity": 15,  
                "requires_shipping": True,  
                "taxable": True  
            },
            {
                "option1": "Negro",  
                "option2": "L",  
                "price": "49.99",  
                "sku": "CHAQUETA-NEGRA-L",  
                "inventory_quantity": 10, 
                "requires_shipping": True,  
                "taxable": True  
            },
            {
                "option1": "Rosa",  
                "option2": "M", 
                "price": "49.99",  
                "sku": "CHAQUETA-ROSA-M",  
                "inventory_quantity": 5,  
                "requires_shipping": True,  
                "taxable": True  
            }
        ],
        "options": [
            {
                "name": "Color",  
                "values": ["Rojo", "Negro", "Rosa"]  
            },
            {
                "name": "Talla",  
                "values": ["S", "M", "L"]  
            }
        ],
        "images": [
            {
                "src": "https://m.media-amazon.com/images/I/61dORinHNsL.jpg"  # portada
            },
            {
                "src": "https://m.media-amazon.com/images/I/51mVp1pc69L._AC_SX679_.jpg",  # URL de la imagen roja
                "alt": "Rojo"  # Atributo que indica el color
            },
            {
                "src": "https://m.media-amazon.com/images/I/519B4irw7OL._AC_SX679_.jpg",  # URL de la imagen negra
                "alt": "Negro"  # Atributo que indica el color
            },
            {
                "src": "https://m.media-amazon.com/images/I/815Ga1enziL._AC_SX569_.jpg",  # URL de la imagen rosa
                "alt": "Rosa"  # Atributo que indica el color
            }
        ],
    }
}

# Convertir el producto a JSON
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": TOKEN
}

# Valor del nuevo código que se va a añadir al metafield
codigo_metafield = "CHAQUETA-DEFAULTTT"

# URL para obtener todos los productos
products_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products.json"

# Realizar la solicitud GET para obtener todos los productos
response = requests.get(products_url, headers=headers)

if response.status_code == 200:
    products = response.json().get("products", [])
    producto_existente = False

    # Verificar si ya existe un producto con el mismo valor en el metafield "codigo"
    for product in products:
        # Obtener los metafields del producto
        metafields_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products/{product['id']}/metafields.json"
        metafields_response = requests.get(metafields_url, headers=headers)

        if metafields_response.status_code == 200:
            metafields = metafields_response.json().get("metafields", [])

            for metafield in metafields:
                if metafield.get("key") == "codigo" and metafield.get("value") == codigo_metafield:
                    producto_existente = True
                    break

        if producto_existente:
            break

    if producto_existente:
        print(f"El producto con el código '{codigo_metafield}' ya existe. No se creará un nuevo producto.")
    else:
        # Realizar la solicitud POST para crear el nuevo producto
        response = requests.post(url, headers=headers, json=producto)

        if response.status_code == 201:
            producto_creado = response.json()["product"]
            product_id = producto_creado["id"]
            images = producto_creado["images"]  # Obtiene las imágenes del producto

            # Añadir un metafield con el nombre "codigo" y el valor del código
            metafield_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products/{product_id}/metafields.json"
            metafield_payload = {
                "metafield": {
                    "namespace": "custom",
                    "key": "codigo",
                    "value": codigo_metafield,
                    "type": "single_line_text_field"
                }
            }

            metafield_response = requests.post(metafield_url, headers=headers, data=json.dumps(metafield_payload))
            print(producto_creado)

            if metafield_response.status_code == 201:
                print(f"Metafield 'codigo' añadido al producto {product_id} con éxito.")
            else:
                print(f"Error al añadir el metafield: {metafield_response.content}")

            # Verifica que hay imágenes disponibles
            if len(images) > 1:
                # Asigna la primera imagen como la imagen de portada
                cover_image_id = images[0]["id"]

                # Crea un diccionario para asignar imágenes por color
                color_image_mapping = {
                    "Rojo": images[1]["id"],  # Imagen para el color rojo
                    "Negro": images[2]["id"],  # Imagen para el color negro
                    "Rosa": images[3]["id"],  # Imagen para el color rosa
                }

                # Asigna la imagen de portada al producto
                update_product_payload = {
                    "product": {
                        "id": product_id,
                        "image_id": cover_image_id  # Asigna la imagen de portada
                    }
                }
                update_product_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/products/{product_id}.json"
                update_product_response = requests.put(update_product_url, json=update_product_payload, headers=headers)

                if update_product_response.status_code == 200:
                    print(f"Imagen de portada asignada al producto {product_id} con éxito.")
                else:
                    print(f"Error al asignar imagen de portada: {update_product_response.content}")

                # Asignar image_id a cada variante según el color
                for variant in producto_creado["variants"]:
                    variant_color = variant["option1"]  # Asumiendo que option1 es el color
                    variant_id = variant["id"]
                    image_id = color_image_mapping.get(variant_color)  # Obtener la imagen según el color

                    if image_id:
                        # Actualiza la variante con el image_id
                        update_variant_payload = {
                            "variant": {
                                "id": variant_id,
                                "image_id": image_id  # Asigna la imagen a la variante
                            }
                        }
                        update_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/variants/{variant_id}.json"
                        update_response = requests.put(update_url, json=update_variant_payload, headers=headers)

                        if update_response.status_code == 200:
                            print(f"Imagen asignada a la variante {variant_id} con éxito.")
                        else:
                            print(f"Error al asignar imagen a la variante {variant_id}: {update_response.content}")

        else:
            print(f"Error al crear el producto: {response.content}")
else:
    print("Error al obtener la lista de productos existentes.")
