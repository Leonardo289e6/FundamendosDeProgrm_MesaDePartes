"""Modelo de datos ventas (arreglos paralelos).

La posición i de cada arreglo pertenece a la misma venta. La venta guarda solo
las CLAVES del cliente, del producto y del vendedor (como claves foráneas en una BD).
"""
from config.settings import MAX_VENTAS

codigos = [""] * MAX_VENTAS         # código de venta - clave
documentos = [""] * MAX_VENTAS      # documento del cliente (-> clientes)
productos = [""] * MAX_VENTAS       # código del producto (-> productos)
cantidades = [0] * MAX_VENTAS       # unidades vendidas
precios = [0.0] * MAX_VENTAS        # precio unitario al momento de la venta (sin IGV)
totales = [0.0] * MAX_VENTAS        # monto total (con IGV)
vendedores = [""] * MAX_VENTAS      # usuario que registró la venta (-> empleados)
total_registros = 0
