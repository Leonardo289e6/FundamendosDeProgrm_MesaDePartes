"""Puente entre los repositorios (arreglos paralelos) y los almacenes (archivos o PostgreSQL).

Convierte los arreglos en "tablas" (listas de tuplas, una por registro) y viceversa.
Es el único módulo de este paquete que toca los repositorios.
"""
from repositories import (cliente_repository, empleado_repository,
                          producto_repository, venta_repository)

# Orden de las tablas: primero las que otras referencian (clave foránea).
TABLAS = ("empleados", "clientes", "productos", "ventas")

COLUMNAS = {
    "empleados": ("usuario", "password_hash", "sal", "nombres", "rol"),
    "clientes": ("documento", "nombre", "telefono"),
    "productos": ("codigo", "nombre", "precio", "stock"),
    "ventas": ("codigo", "documento_cliente", "codigo_producto", "cantidad",
               "precio_unitario", "total", "usuario_vendedor"),
}


def extraer():
    """Copia los arreglos a un diccionario {tabla: [tupla, tupla, ...]}."""
    empleados = []
    for i in range(empleado_repository.cantidad()):
        usuario, nombre, rol = empleado_repository.obtener(i)
        clave_hash, sal = empleado_repository.obtener_credenciales(i)
        empleados.append((usuario, clave_hash, sal, nombre, rol))
    return {
        "empleados": empleados,
        "clientes": [cliente_repository.obtener(i) for i in range(cliente_repository.cantidad())],
        "productos": [producto_repository.obtener(i) for i in range(producto_repository.cantidad())],
        "ventas": [venta_repository.obtener(i) for i in range(venta_repository.cantidad())],
    }


def cargar(datos):
    """Reemplaza el contenido de los arreglos por las tablas recibidas."""
    for repo in (empleado_repository, cliente_repository, producto_repository, venta_repository):
        repo.vaciar()
    for fila in datos["empleados"]:
        empleado_repository.guardar(*fila)
    for fila in datos["clientes"]:
        cliente_repository.guardar(*fila)
    for fila in datos["productos"]:
        producto_repository.guardar(*fila)
    for fila in datos["ventas"]:
        venta_repository.guardar(*fila)
