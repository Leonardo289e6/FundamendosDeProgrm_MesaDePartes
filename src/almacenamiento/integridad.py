"""Rutina de validación de integridad: revisa los datos leídos ANTES de cargarlos al sistema.

Detecta archivos editados a mano, truncados o de otra versión: formatos inválidos, claves
repetidas, referencias a clientes/productos/vendedores que no existen, números imposibles
y más registros de los que caben en los arreglos.
Si algo falla lanza DatosCorruptosError indicando la tabla y el número de registro.
"""
import math

from config import settings
from exceptions.errores import DatosCorruptosError, ErrorNegocio
from services import validacion_service as val


def _falla(tabla, numero, detalle):
    raise DatosCorruptosError(f"{tabla} (registro {numero})", detalle)


def _es_hex(texto, largo):
    if len(texto) != largo:
        return False
    try:
        int(texto, 16)
    except ValueError:
        return False
    return True


def _numero_valido(valor, tipo):
    """Número finito (sin NaN ni infinito) del tipo esperado."""
    return isinstance(valor, tipo) and not isinstance(valor, bool) and math.isfinite(valor)


def _revisar(tabla, filas, capacidad, regla):
    """Aplica la regla a cada fila y exige claves únicas (la clave es el primer campo)."""
    if len(filas) > capacidad:
        raise DatosCorruptosError(tabla, f"hay {len(filas)} registros y solo caben {capacidad}.")
    vistas = set()
    for numero, fila in enumerate(filas, start=1):
        if fila[0] in vistas:
            _falla(tabla, numero, f"la clave '{fila[0]}' está repetida.")
        vistas.add(fila[0])
        try:
            regla(numero, fila)
        except ErrorNegocio as error:          # error de un validador de validacion_service
            if isinstance(error, DatosCorruptosError):
                raise
            _falla(tabla, numero, str(error))
    return vistas


def validar_tablas(datos):
    """Revisa las 4 tablas. No modifica nada."""
    def empleado(n, fila):
        usuario, clave_hash, sal, nombre, rol = fila
        if val.validar_usuario(usuario) != usuario:
            _falla("empleados", n, f"usuario '{usuario}' no está normalizado.")
        if not _es_hex(clave_hash, 64) or not _es_hex(sal, 32):
            _falla("empleados", n, "hash o sal con formato inválido.")
        if nombre.strip() == "":
            _falla("empleados", n, "el nombre está vacío.")
        if rol not in settings.ROLES:
            _falla("empleados", n, f"rol '{rol}' no existe.")

    def cliente(n, fila):
        documento, nombre, telefono = fila
        if not val.es_documento_valido(documento):
            _falla("clientes", n, f"documento '{documento}' inválido.")
        if nombre.strip() == "" or len(nombre) > settings.LONGITUD_MAX_NOMBRE:
            _falla("clientes", n, "nombre vacío o demasiado largo.")
        val.validar_telefono(telefono)

    def producto(n, fila):
        codigo, nombre, precio, stock = fila
        if codigo.strip() == "" or len(codigo) > settings.LONGITUD_MAX_CODIGO:
            _falla("productos", n, "código vacío o demasiado largo.")
        if nombre.strip() == "" or len(nombre) > settings.LONGITUD_MAX_NOMBRE:
            _falla("productos", n, "nombre vacío o demasiado largo.")
        if not _numero_valido(precio, float) or precio <= 0:
            _falla("productos", n, "el precio debe ser un número mayor a 0.")
        if not _numero_valido(stock, int) or stock < 0:
            _falla("productos", n, "el stock debe ser un entero de 0 o más.")

    usuarios = _revisar("empleados", datos["empleados"], settings.MAX_EMPLEADOS, empleado)
    documentos = _revisar("clientes", datos["clientes"], settings.MAX_CLIENTES, cliente)
    codigos = _revisar("productos", datos["productos"], settings.MAX_PRODUCTOS, producto)

    def venta(n, fila):
        _, documento, cod_producto, cantidad, precio, total, vendedor = fila
        if documento not in documentos:
            _falla("ventas", n, f"el cliente '{documento}' no existe.")
        if cod_producto not in codigos:
            _falla("ventas", n, f"el producto '{cod_producto}' no existe.")
        if vendedor not in usuarios:
            _falla("ventas", n, f"el vendedor '{vendedor}' no existe.")
        if not _numero_valido(cantidad, int) or cantidad <= 0:
            _falla("ventas", n, "la cantidad debe ser un entero mayor a 0.")
        if not _numero_valido(precio, float) or precio <= 0:
            _falla("ventas", n, "el precio unitario debe ser mayor a 0.")
        if not _numero_valido(total, float) or total <= 0:
            _falla("ventas", n, "el total debe ser mayor a 0.")
        if fila[0].strip() == "" or len(fila[0]) > settings.LONGITUD_MAX_CODIGO:
            _falla("ventas", n, "código de venta vacío o demasiado largo.")

    _revisar("ventas", datos["ventas"], settings.MAX_VENTAS, venta)
