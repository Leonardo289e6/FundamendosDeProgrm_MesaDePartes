"""Gestor de persistencia: decide dónde viven los datos y los carga / confirma.

    configurar("archivos" | "postgresql" | "memoria")   elige el almacén
    cargar()      al iniciar: lee, VALIDA la integridad y llena los arreglos
    confirmar()   después de cada cambio: guarda; si falla, devuelve los arreglos al último
                  estado guardado para que memoria y almacén nunca queden distintos

Mientras no se llame configurar() el modo es "memoria" (no guarda nada): así las pruebas
automáticas no escriben archivos.
"""
from almacenamiento import integridad
from almacenamiento import tablas as puente
from almacenamiento.archivos import AlmacenArchivos
from almacenamiento.postgres import AlmacenPostgres
from exceptions.errores import ErrorPersistencia, ValorInvalidoError

_almacen = None   # None = memoria


def configurar(modo=None, almacen=None):
    """modo: 'archivos', 'postgresql' o 'memoria'. 'almacen' permite inyectar uno propio."""
    global _almacen
    if almacen is not None:
        _almacen = almacen
    elif modo == "memoria":
        _almacen = None
    elif modo == "archivos":
        _almacen = AlmacenArchivos()
    elif modo == "postgresql":
        _almacen = AlmacenPostgres()
    else:
        raise ValorInvalidoError(f"modo de persistencia desconocido: '{modo}'.")


def modo_activo():
    return "memoria" if _almacen is None else _almacen.nombre


def descripcion():
    return "solo memoria (no se guarda nada)" if _almacen is None else _almacen.descripcion()


def cargar():
    """Lee el almacén, valida la integridad y llena los arreglos. Lanza ErrorPersistencia."""
    if _almacen is None:
        return
    datos = _almacen.leer()
    integridad.validar_tablas(datos)      # si algo está mal NO se carga nada
    puente.cargar(datos)


def confirmar():
    """Guarda el estado actual. Si falla, restaura los arreglos desde el almacén y avisa."""
    if _almacen is None:
        return
    try:
        _almacen.guardar(puente.extraer())
    except ErrorPersistencia as error:
        try:
            cargar()                       # revierte la memoria al último estado guardado
        except ErrorPersistencia:
            pass                           # si tampoco se puede leer, ya se informa el error original
        raise ErrorPersistencia(f"{error} El cambio NO se guardó.")
