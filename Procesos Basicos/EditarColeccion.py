import requests

# Token de acceso API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

# Headers para las solicitudes
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": TOKEN
}

# Función para editar una colección manual
def editar_coleccion_manual(coleccion_id, **datos):
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/custom_collections/{coleccion_id}.json"
    data = {
        "custom_collection": {}
    }
    
    # Agregar todos los campos proporcionados al diccionario data
    data["custom_collection"].update(datos)
    
    response = requests.put(url, headers=headers, json=data)
    return response

# Función para editar una colección automática
def editar_coleccion_automatica(coleccion_id, **datos):
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/smart_collections/{coleccion_id}.json"
    data = {
        "smart_collection": {}
    }
    
    # Agregar todos los campos proporcionados al diccionario data
    data["smart_collection"].update(datos)
    
    response = requests.put(url, headers=headers, json=data)
    return response

# Ejemplo de edición de una colección manual
coleccion_manual_id = 1234567890  
# respuesta_manual = editar_coleccion_manual(
#     coleccion_manual_id, 
#     title="Nuevo Título para la Colección", 
#     body_html="<strong>Descripción actualizada de la colección.</strong>", 
#     handle="nuevo-handle", 
#     published=True, 
#     template_suffix="nuevo-template"
# )
# if respuesta_manual.status_code == 200:
#     print("Colección manual editada con éxito:", respuesta_manual.json())
# else:
#     print("Error al editar colección manual:", respuesta_manual.content)

# Ejemplo de edición de una colección automática
coleccion_automatica_id = 641565163863 
nuevas_reglas = [
    {"column": "tag", "relation": "equals", "condition": "Hombre"},
    {"column": "tag", "relation": "equals", "condition": "Nuevas Llegadas"}
]
respuesta_automatica = editar_coleccion_automatica(
    coleccion_automatica_id, 
    title="Colección Automática Actualizada", 
    rules=nuevas_reglas, 
    sort_order="manual", 
    disjunctive=True, 
    published=True, 
    template_suffix="nuevo-template-automatico"
)
if respuesta_automatica.status_code == 200:
    print("Colección automática editada con éxito:", respuesta_automatica.json())
else:
    print("Error al editar colección automática:", respuesta_automatica.content)
