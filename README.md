Conector Sage200 - Shopify

Este repositorio contiene los conectores necesarios para integrar Sage200 con Shopify, permitiendo una sincronización eficiente de datos entre ambas plataformas. El repositorio está dividido en dos partes principales: procesos manuales y operaciones automáticas.

Estructura del Repositorio

Procesos Manuales

La carpeta procesos incluye scripts y herramientas para interactuar manualmente con los diferentes apartados de la API de Shopify:

Categorías: Crear, editar y eliminar categorías manualmente.

Clientes: Gestión de clientes mediante la API.

Productos: Operaciones CRUD (Crear, Leer, Actualizar, Eliminar) sobre productos.

Pedidos: Control y manejo de pedidos.

Estos procesos están diseñados para explorar y entender cómo funcionan los diferentes endpoints de la API de Shopify antes de implementar automatizaciones.

Operaciones Automáticas

La carpeta Conecto_Final contiene scripts para la sincronización automática de datos entre Sage200 y Shopify. Estas operaciones incluyen:

Importación y exportación de datos dinámicos: Sincronización automática de categorías, clientes, productos, stock y pedidos.

Actualización en tiempo real: Mantener los datos actualizados en ambas plataformas.

Optimización de flujos: Minimización de conflictos y errores durante la transferencia de datos.

Características Principales

Gestión de Categorías: Sincronización y mantenimiento de categorías entre Sage200 y Shopify.

Gestión de Clientes: Creación y actualización de clientes de forma automática.

Gestión de Productos:

Sincronización de productos y variantes.

Control de inventario y precios.

Gestión de Pedidos:

Importación de pedidos desde Shopify a Sage200.

Actualización del estado de los pedidos en ambas plataformas.

Sincronización de Stock: Control en tiempo real del inventario.

Instalación

Clona el repositorio:

git clone https://github.com/tuusuario/sage200-shopify-conector.git

Instala las dependencias necesarias utilizando pip:

pip install -r requirements.txt

Configura los parámetros de conexión en el archivo config.json para Sage200 y Shopify.
Requisitos del Sistema

Sage200 configurado y operativo.

Shopify con acceso a la API y credenciales generadas.

Python 3.11.7 o superior.

Contribuciones

¡Las contribuciones son bienvenidas! Si deseas colaborar, por favor, crea un fork del repositorio, realiza tus cambios y envía un pull request.

Contacto

Para preguntas o soporte, contacta a granjuan02@gmail.com .
