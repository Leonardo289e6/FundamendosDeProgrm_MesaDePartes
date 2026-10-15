"""Modelo de datos: empleados (arreglos paralelos). Solo declara datos."""
from config.settings import MAX_EMPLEADOS

usuarios = [""] * MAX_EMPLEADOS     # nombre de usuario (clave)
hashes = [""] * MAX_EMPLEADOS       # hash PBKDF2 de la contraseña
sales = [""] * MAX_EMPLEADOS        # sal aleatoria del hash
nombres = [""] * MAX_EMPLEADOS      # nombres completos
roles = [""] * MAX_EMPLEADOS        # Administrador / Vendedor
total_registros = 0                 # cuántas posiciones están ocupadas
