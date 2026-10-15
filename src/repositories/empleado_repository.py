"""Repositorio de empleados: único módulo que lee y escribe los arreglos de empleados."""
from models import empleado as m


def cantidad():
    return m.total_registros


def guardar(usuario, clave_hash, sal, nombre, rol):
    pos = m.total_registros
    m.usuarios[pos] = usuario
    m.hashes[pos] = clave_hash
    m.sales[pos] = sal
    m.nombres[pos] = nombre
    m.roles[pos] = rol
    m.total_registros += 1


def buscar_por_usuario(usuario):
    """Búsqueda lineal. Devuelve la posición o -1 si no existe."""
    for i in range(m.total_registros):
        if m.usuarios[i] == usuario:
            return i
    return -1


def obtener(pos):
    """Datos públicos del empleado (sin hash ni sal)."""
    return (m.usuarios[pos], m.nombres[pos], m.roles[pos])


def obtener_credenciales(pos):
    """Hash y sal: solo los usa el servicio de autenticación."""
    return (m.hashes[pos], m.sales[pos])
