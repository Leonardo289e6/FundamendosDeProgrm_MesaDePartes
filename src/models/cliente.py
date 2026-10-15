"""Modelo de datos: clientes (arreglos paralelos). Solo declara datos."""
from config.settings import MAX_CLIENTES

documentos = [""] * MAX_CLIENTES    # DNI (8 dígitos) o RUC (11 dígitos) - clave
nombres = [""] * MAX_CLIENTES       # nombres o razón social
telefonos = [""] * MAX_CLIENTES     # celular de 9 dígitos
total_registros = 0
