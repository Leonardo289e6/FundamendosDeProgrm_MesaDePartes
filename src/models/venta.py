"""Modelo de datos: arreglos paralelos.

La posición i de cada arreglo pertenece a la misma venta.
Este módulo solo declara los datos; no contiene lógica.
"""
from config.settings import MAX_VENTAS

codigos = [""] * MAX_VENTAS       # código de venta
documentos = [""] * MAX_VENTAS    # DNI (8 dígitos) o RUC (11 dígitos)
clientes = [""] * MAX_VENTAS      # nombres o razón social
maquinas = [""] * MAX_VENTAS      # tipo de maquinaria vendida
cantidades = [0] * MAX_VENTAS     # unidades vendidas
precios = [0.0] * MAX_VENTAS      # precio unitario (sin IGV)
totales = [0.0] * MAX_VENTAS      # monto total (con IGV)
