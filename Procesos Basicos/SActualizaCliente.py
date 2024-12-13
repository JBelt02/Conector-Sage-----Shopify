import requests
import pyodbc
import json

SHOPIFY_API_KEY = 'tu_api_key'
SHOPIFY_PASSWORD = 'tu_password'
SHOP_NAME = 'tu_shop_name'
API_VERSION = '2023-10'

# Conexión a la base de datos de Sage 200 (si usas SQL Server)
def get_customers_from_sage():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=tu_servidor;DATABASE=tu_bd_sage;UID=tu_usuario;PWD=tu_contraseña')
    cursor = conn.cursor()
    
    query = """
        SELECT Email FROM Customers
    """
    cursor.execute(query)
    
    customers = cursor.fetchall()
    conn.close()
    
    # Crear un conjunto de emails para buscar más rápido
    customer_emails = {customer[0] for customer in customers}
    return customer_emails

# Obtener todos los clientes de Shopify
def get_customers_from_shopify():
    url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/customers.json"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        customers = response.json()['customers']
        return customers
    else:
        print(f"Error al obtener los clientes: {response.status_code}")
        return []

# Función para crear un cliente en Sage si no existe
def create_customer_in_sage(customer_data):
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=tu_servidor;DATABASE=tu_bd_sage;UID=tu_usuario;PWD=tu_contraseña')
    cursor = conn.cursor()
    
    query = """
        INSERT INTO Customers (FirstName, LastName, Email)
        VALUES (?, ?, ?)
    """
    cursor.execute(query, customer_data['first_name'], customer_data['last_name'], customer_data['email'])
    conn.commit()
    conn.close()

# Función para sincronizar los clientes de Shopify a Sage
def sync_customers_to_sage():
    # Obtener los emails de todos los clientes en Sage
    clientes_sage = get_customers_from_sage()
    
    # Obtener los clientes de Shopify
    clientes_shopify = get_customers_from_shopify()

    # Iterar sobre los clientes de Shopify
    for cliente in clientes_shopify:
        email = cliente['email']
        
        # Si el cliente no existe en Sage, lo creamos
        if email not in clientes_sage:
            print(f"Creando cliente en Sage: {cliente['first_name']} {cliente['last_name']}, Email: {email}")
            create_customer_in_sage(cliente)
        else:
            print(f"Cliente ya existe en Sage: {cliente['first_name']} {cliente['last_name']}, Email: {email}")

# Ejecutar la sincronización de clientes de Shopify a Sage
sync_customers_to_sage()
