"""Modelo de datos: productos / inventario (arreglos paralelos). Solo declara datos."""
from config.settings import MAX_PRODUCTOS

codigos = [""] * MAX_PRODUCTOS      # código del producto - clave
nombres = [""] * MAX_PRODUCTOS      # tipo de maquinaria
precios = [0.0] * MAX_PRODUCTOS     # precio unitario (sin IGV)
stocks = [0] * MAX_PRODUCTOS        # unidades disponibles
total_registros = 0
