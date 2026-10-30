"""Repositorio de ventas: único módulo que lee y escribe los arreglos de ventas.

Él lleva la cuenta de registros (total_registros): los demás módulos no necesitan
saber cuántas posiciones están ocupadas. Así se parece a una base de datos.
"""
from models import venta as m

_VACIOS = ("", "", "", 0, 0.0, 0.0, "")


def _arreglos():
    return (m.codigos, m.documentos, m.productos, m.cantidades,
            m.precios, m.totales, m.vendedores)


def _intercambiar(i, j):
    """Intercambia la posición i con la j en los 7 arreglos paralelos."""
    for arr in _arreglos():
        arr[i], arr[j] = arr[j], arr[i]


def cantidad():
    return m.total_registros


def guardar(codigo, documento, producto, cantidad_vendida, precio, total, vendedor):
    pos = m.total_registros
    m.codigos[pos] = codigo
    m.documentos[pos] = documento
    m.productos[pos] = producto
    m.cantidades[pos] = cantidad_vendida
    m.precios[pos] = precio
    m.totales[pos] = total
    m.vendedores[pos] = vendedor
    m.total_registros += 1


def obtener(pos):
    """Devuelve la venta de la posición indicada como una tupla de 7 campos."""
    return (m.codigos[pos], m.documentos[pos], m.productos[pos], m.cantidades[pos],
            m.precios[pos], m.totales[pos], m.vendedores[pos])


def actualizar(pos, documento, producto, cantidad_vendida, precio, total):
    """Modifica una venta existente. El código y el vendedor no cambian."""
    m.documentos[pos] = documento
    m.productos[pos] = producto
    m.cantidades[pos] = cantidad_vendida
    m.precios[pos] = precio
    m.totales[pos] = total


def eliminar(pos):
    """Elimina la venta de pos desplazando las siguientes una posición a la izquierda."""
    ultimo = m.total_registros - 1
    for i in range(pos, ultimo):
        for arr in _arreglos():
            arr[i] = arr[i + 1]
    for arr, vacio in zip(_arreglos(), _VACIOS):
        arr[ultimo] = vacio
    m.total_registros -= 1


def buscar_por_codigo(codigo):
    """Búsqueda lineal. Devuelve la posición o -1 si no existe."""
    for i in range(m.total_registros):
        if m.codigos[i] == codigo:
            return i
    return -1


def ordenar_por_codigo():
    """Ordenamiento burbuja ascendente por código."""
    n = m.total_registros
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if m.codigos[j] > m.codigos[j + 1]:
                _intercambiar(j, j + 1)


def ordenar_por_total():
    """Ordenamiento por selección descendente por monto total."""
    n = m.total_registros
    for i in range(n - 1):
        mayor = i
        for j in range(i + 1, n):
            if m.totales[j] > m.totales[mayor]:
                mayor = j
        if mayor != i:
            _intercambiar(i, mayor)


def vaciar():
    """Limpia los datos de ventas para recargarlos desde persistencia."""
    for arr, vacio in zip(_arreglos(), _VACIOS):
        arr[:] = [vacio] * len(arr)
    m.total_registros = 0