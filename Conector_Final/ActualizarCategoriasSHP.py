import pyodbc
import requests
import socket
import time  # Importamos para manejar las pausas

# Obtener el nombre del equipo
hostname = socket.gethostname()

# Configuración de conexión a la base de datos
if hostname == "DESKTOP-6ES4A5L":
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=VESAGE01;"
        "DATABASE=VEBD;"
        "UID=logic;"
        "PWD=#Obelix*.99"
    )
else:
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=VESAGE01;"
        "DATABASE=VEBD;"
        "UID=logic;"
        "PWD=#Obelix*.99"
    )

cursor = conn.cursor()

# Configuración API de Shopify
TOKEN = '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'
SHOP_NAME = 'hx8nsv-30'

headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": TOKEN
}

# Función para comprobar si una colección ya existe
def existe_coleccion(titulo):
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/smart_collections.json"
    params = {"title": titulo}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        colecciones = response.json().get('smart_collections', [])
        for coleccion in colecciones:
            if coleccion['title'] == titulo:
                return True
    return False

# Función para crear colecciones inteligentes en Shopify
def crear_coleccion_automatica(titulo, reglas):
    if existe_coleccion(titulo):
        print(f"Colección '{titulo}' ya existe. No se creará nuevamente.")
        return

    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-01/smart_collections.json"
    data = {
        "smart_collection": {
            "title": titulo,
            "rules": reglas,
            "published": True
        }
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"Colección '{titulo}' creada con éxito.")
    elif response.status_code == 429:  # Manejar específicamente el error 429
        print(f"Error al crear la colección '{titulo}': {response.status_code} - {response.content}")
        time.sleep(2)  # Pausa adicional en caso de error 429
    else:
        print(f"Error al crear la colección '{titulo}': {response.status_code} - {response.content}")

# Consulta SQL para obtener familias y subfamilias
consulta_sql = """
SELECT 
    CodigoFamilia, 
    Descripcion AS NombreFamilia, 
    CodigoSubfamilia, 
    (CASE WHEN CodigoSubfamilia = '**********' THEN 1 ELSE 0 END) AS EsFamilia
FROM Familias
WHERE CodigoEmpresa = '997'
ORDER BY CodigoFamilia, CodigoSubfamilia
"""
cursor.execute(consulta_sql)

# Procesar las familias y subfamilias
familias = {}
for row in cursor.fetchall():
    codigo_familia = row[0]
    nombre_familia = row[1].strip()
    codigo_subfamilia = row[2]
    es_familia = row[3]

    if es_familia:  # Es una familia
        familias[codigo_familia] = {"nombre": nombre_familia, "subfamilias": []}
    else:  # Es una subfamilia
        if codigo_familia in familias:
            familias[codigo_familia]["subfamilias"].append(nombre_familia)

# Crear colecciones en Shopify
for codigo_familia, datos in familias.items():
    nombre_familia = datos["nombre"]

    # Crear colección para la familia
    reglas_familia = [{"column": "tag", "relation": "equals", "condition": nombre_familia}]
    crear_coleccion_automatica(nombre_familia, reglas_familia)

    # Pausa entre solicitudes
    time.sleep(0.5)

    # Crear colecciones para las subfamilias
    for nombre_subfamilia in datos["subfamilias"]:
        reglas_subfamilia = [
            {"column": "tag", "relation": "equals", "condition": nombre_familia},
            {"column": "tag", "relation": "equals", "condition": nombre_subfamilia}
        ]
        titulo_subfamilia = f"{nombre_familia} > {nombre_subfamilia}"
        crear_coleccion_automatica(titulo_subfamilia, reglas_subfamilia)

        # Pausa entre solicitudes
        time.sleep(0.5)

# Cerrar la conexión a la base de datos
cursor.close()
conn.close()
