"""Servicio de ventas: reglas de negocio. Usa el repositorio, nunca los arreglos."""
from config import settings
from exceptions.errores import CodigoDuplicadoError, InventarioLlenoError
from repositories import venta_repository as repo


def calcular_total(cantidad, precio_unitario):
    return cantidad * precio_unitario * (1 + settings.IGV)


def validar_codigo_nuevo(n, codigo):
    if n == settings.MAX_VENTAS:
        raise InventarioLlenoError()
    if repo.buscar_por_codigo(n, codigo) != -1:
        raise CodigoDuplicadoError()


def registrar_venta(n, codigo, documento, cliente, maquina, cantidad, precio):
    """Guarda la venta y devuelve la nueva cantidad de registros."""
    validar_codigo_nuevo(n, codigo)
    total = calcular_total(cantidad, precio)
    repo.guardar(n, codigo, documento, cliente, maquina, cantidad, precio, total)
    return n + 1


def buscar_venta(n, codigo):
    """Devuelve la venta encontrada (tupla) o None."""
    pos = repo.buscar_por_codigo(n, codigo)
    if pos == -1:
        return None
    return repo.obtener(pos)


def ordenar_ventas(n):
    repo.ordenar_por_codigo(n)


def listar_ventas(n):
    """Devuelve la lista de ventas y el monto acumulado."""
    ventas = []
    suma = 0.0
    for i in range(n):
        venta = repo.obtener(i)
        ventas.append(venta)
        suma = suma + venta[6]
    return ventas, suma
