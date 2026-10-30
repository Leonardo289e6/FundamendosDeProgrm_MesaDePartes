"""Repositorio de productos: único módulo que lee y escribe los arreglos del inventario."""
from models import producto as m


def cantidad():
    return m.total_registros


def guardar(codigo, nombre, precio, stock):
    pos = m.total_registros
    m.codigos[pos] = codigo
    m.nombres[pos] = nombre
    m.precios[pos] = precio
    m.stocks[pos] = stock
    m.total_registros += 1


def obtener(pos):
    return (m.codigos[pos], m.nombres[pos], m.precios[pos], m.stocks[pos])


def buscar_por_codigo(codigo):
    """Búsqueda lineal. Devuelve la posición o -1 si no existe."""
    for i in range(m.total_registros):
        if m.codigos[i] == codigo:
            return i
    return -1


def actualizar_stock(pos, stock):
    m.stocks[pos] = stock


def vaciar():
    """Limpia los datos de productos para recargarlos desde persistencia."""
    m.codigos[:] = [""] * len(m.codigos)
    m.nombres[:] = [""] * len(m.nombres)
    m.precios[:] = [0.0] * len(m.precios)
    m.stocks[:] = [0] * len(m.stocks)
    m.total_registros = 0
