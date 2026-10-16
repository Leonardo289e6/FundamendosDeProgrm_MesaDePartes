"""Datos de ejemplo para probar el sistema sin persistencia (se desactiva en la versión final).

Carga empleados, clientes y productos directamente en los repositorios.
Las contraseñas de ejemplo son SOLO para demostración:
    admin / admin123      (Administrador)
    vendedor1 / venta123  (Vendedor)
"""
from repositories import cliente_repository, empleado_repository, producto_repository
from utils import seguridad


def _empleado(usuario, clave, nombre, rol):
    sal = seguridad.generar_sal()
    empleado_repository.guardar(usuario, seguridad.generar_hash(clave, sal), sal, nombre, rol)


def cargar():
    _empleado("admin", "admin123", "ADMINISTRADOR DEL SISTEMA", "Administrador")
    _empleado("vendedor1", "venta123", "CARLOS RAMOS", "Vendedor")

    cliente_repository.guardar("47581234", "JUAN PEREZ", "987654321")
    cliente_repository.guardar("20123456789", "CONSTRUCTORA NARVAEZ SAC", "944111222")
    cliente_repository.guardar("20456789012", "MINERA ANDES SAC", "955333444")

    producto_repository.guardar("EXC-01", "EXCAVADORA", 120000.0, 5)
    producto_repository.guardar("RETRO-01", "RETROEXCAVADORA", 98000.0, 3)
    producto_repository.guardar("CARG-01", "CARGADOR FRONTAL", 85000.0, 4)
    producto_repository.guardar("RODI-01", "RODILLO COMPACTADOR", 45000.0, 2)
