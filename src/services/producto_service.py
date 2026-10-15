"""Servicio de inventario: productos y stock. Usa el repositorio, nunca los arreglos."""
from config import settings
from exceptions.errores import (CapacidadLlenaError, ProductoDuplicadoError,
                                ProductoNoEncontradoError, StockInsuficienteError)
from repositories import producto_repository as repo
from services import auth_service as auth


def registrar_producto(codigo, nombre, precio, stock):
    auth.exigir_admin()
    if repo.cantidad() == settings.MAX_PRODUCTOS:
        raise CapacidadLlenaError("productos")
    if repo.buscar_por_codigo(codigo) != -1:
        raise ProductoDuplicadoError()
    repo.guardar(codigo, nombre, precio, stock)


def buscar_producto(codigo):
    """Devuelve (código, nombre, precio, stock) o None."""
    pos = repo.buscar_por_codigo(codigo)
    if pos == -1:
        return None
    return repo.obtener(pos)


def obtener_producto(codigo):
    producto = buscar_producto(codigo)
    if producto is None:
        raise ProductoNoEncontradoError()
    return producto


def reponer_stock(codigo, cantidad):
    """Suma unidades al stock y devuelve el nuevo stock."""
    auth.exigir_admin()
    pos = repo.buscar_por_codigo(codigo)
    if pos == -1:
        raise ProductoNoEncontradoError()
    nuevo = repo.obtener(pos)[3] + cantidad
    repo.actualizar_stock(pos, nuevo)
    return nuevo


def listar_productos():
    """Devuelve (código, nombre, precio, stock, stock_bajo) de cada producto."""
    productos = []
    for i in range(repo.cantidad()):
        codigo, nombre, precio, stock = repo.obtener(i)
        productos.append((codigo, nombre, precio, stock, stock <= settings.STOCK_MINIMO))
    return productos


def descontar_stock(codigo, cantidad):
    """Resta unidades del stock. Lanza StockInsuficienteError si no alcanza."""
    pos = repo.buscar_por_codigo(codigo)
    if pos == -1:
        raise ProductoNoEncontradoError()
    stock = repo.obtener(pos)[3]
    if cantidad > stock:
        raise StockInsuficienteError(stock)
    repo.actualizar_stock(pos, stock - cantidad)


def devolver_stock(codigo, cantidad):
    """Suma unidades al stock (por venta modificada o eliminada)."""
    pos = repo.buscar_por_codigo(codigo)
    if pos == -1:
        raise ProductoNoEncontradoError()
    repo.actualizar_stock(pos, repo.obtener(pos)[3] + cantidad)
