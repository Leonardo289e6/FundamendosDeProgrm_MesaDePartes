"""Repositorio: único módulo que lee y escribe los arreglos del modelo."""
from models import venta as m


def guardar(pos, codigo, documento, cliente, maquina, cantidad, precio, total):
    m.codigos[pos] = codigo
    m.documentos[pos] = documento
    m.clientes[pos] = cliente
    m.maquinas[pos] = maquina
    m.cantidades[pos] = cantidad
    m.precios[pos] = precio
    m.totales[pos] = total


def obtener(pos):
    """Devuelve la venta de la posición indicada como una tupla."""
    return (m.codigos[pos], m.documentos[pos], m.clientes[pos], m.maquinas[pos],
            m.cantidades[pos], m.precios[pos], m.totales[pos])


def buscar_por_codigo(n, codigo):
    """Búsqueda lineal. Devuelve la posición o -1 si no existe."""
    for i in range(n):
        if m.codigos[i] == codigo:
            return i
    return -1


def ordenar_por_codigo(n):
    """Ordenamiento burbuja ascendente por código, intercambiando los 7 arreglos."""
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if m.codigos[j] > m.codigos[j + 1]:
                for arr in (m.codigos, m.documentos, m.clientes, m.maquinas,
                            m.cantidades, m.precios, m.totales):
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
