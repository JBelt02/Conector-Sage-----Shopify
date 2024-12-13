import requests
import pyodbc
import json

SHOPIFY_API_KEY = 'tu_api_key'
SHOPIFY_PASSWORD = 'tu_password'
SHOP_NAME = 'tu_shop_name'
API_VERSION = '2023-10'


# Función para obtener los pedidos desde Shopify
def get_orders_from_shopify():
    url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/orders.json"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        orders = response.json()['orders']
        return orders
    else:
        print(f"Error al obtener los pedidos: {response.status_code}")
        return []

# Función para obtener todos los OrderID de Sage (pedidos ya sincronizados)
def get_existing_orders_from_sage():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=tu_servidor;DATABASE=tu_bd_sage;UID=tu_usuario;PWD=tu_contraseña')
    cursor = conn.cursor()
    
    query = """
        SELECT OrderID FROM Orders
    """
    cursor.execute(query)
    
    # Obtener todos los OrderID ya registrados en Sage y guardarlos en un conjunto
    orders = cursor.fetchall()
    conn.close()
    
    # Convertir la lista de tuplas en un conjunto de IDs para una búsqueda rápida
    existing_order_ids = {order[0] for order in orders}
    return existing_order_ids

# Función para crear un pedido en Sage
def create_order_in_sage(order_data):
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=tu_servidor;DATABASE=tu_bd_sage;UID=tu_usuario;PWD=tu_contraseña')
    cursor = conn.cursor()
    
    query = """
        INSERT INTO Orders (OrderID, CustomerName, TotalAmount)
        VALUES (?, ?, ?)
    """
    cursor.execute(query, order_data['id'], order_data['customer']['first_name'], order_data['total_price'])
    conn.commit()
    conn.close()

# Función para sincronizar pedidos de Shopify a Sage
def sync_orders_to_sage():
    # Obtener los pedidos ya existentes en Sage
    existing_orders_in_sage = get_existing_orders_from_sage()
    
    # Obtener los pedidos desde Shopify
    pedidos_shopify = get_orders_from_shopify()

    # Iterar sobre los pedidos de Shopify
    for pedido in pedidos_shopify:
        order_id = pedido['id']
        
        # Si el pedido no está en Sage, lo creamos
        if order_id not in existing_orders_in_sage:
            print(f"Creando pedido en Sage: Pedido #{order_id} de {pedido['customer']['first_name']}")
            create_order_in_sage(pedido)
        else:
            print(f"El pedido #{order_id} ya existe en Sage.")

# Ejecutar la sincronización de pedidos de Shopify a Sage
sync_orders_to_sage()
