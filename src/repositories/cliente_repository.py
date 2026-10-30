"""Repositorio de clientes: único módulo que lee y escribe los arreglos de clientes."""
from models import cliente as m


def cantidad():
    return m.total_registros


def guardar(documento, nombre, telefono):
    pos = m.total_registros
    m.documentos[pos] = documento
    m.nombres[pos] = nombre
    m.telefonos[pos] = telefono
    m.total_registros += 1


def obtener(pos):
    return (m.documentos[pos], m.nombres[pos], m.telefonos[pos])


def buscar_por_documento(documento):
    """Búsqueda lineal. Devuelve la posición o -1 si no existe."""
    for i in range(m.total_registros):
        if m.documentos[i] == documento:
            return i
    return -1


def actualizar(pos, nombre, telefono):
    """Modifica un cliente existente. El documento no cambia."""
    m.nombres[pos] = nombre
    m.telefonos[pos] = telefono


def vaciar():
    """Limpia los datos de clientes para recargarlos desde persistencia."""
    m.documentos[:] = [""] * len(m.documentos)
    m.nombres[:] = [""] * len(m.nombres)
    m.telefonos[:] = [""] * len(m.telefonos)
    m.total_registros = 0
