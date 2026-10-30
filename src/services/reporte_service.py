"""Servicio de reportes. No modifica ningún dato.

Tiene dos partes:
  * Reportes de negocio (resumen_general, reporte_por): totales de ventas e inventario que
    usa la pestaña Reportes. Todos los acumulados se calculan con funciones recursivas.
  * Comparación iterativo vs recursivo y pruebas de rendimiento (menú de consola).
"""
import sys
import time

from config import settings
from repositories import venta_repository as repo
from services import producto_service as productos
from services import venta_service as ventas
from utils import recursividad as rec


def _totales():
    return [repo.obtener(i)[5] for i in range(repo.cantidad())]


def _codigos():
    return [repo.obtener(i)[0] for i in range(repo.cantidad())]


def _medir(funcion, repeticiones):
    """Tiempo promedio de una llamada, en microsegundos."""
    inicio = time.perf_counter()
    for _ in range(repeticiones):
        funcion()
    return (time.perf_counter() - inicio) / repeticiones * 1_000_000


def comparar_acumulado():
    """Suma los totales de las ventas reales con las tres versiones y mide cada una.

    Devuelve un diccionario: n, resultados y tiempos (µs) de iterativo, recursivo y dividir.
    """
    totales = _totales()
    n = len(totales)
    funciones = {
        "iterativo": lambda: rec.sumar_iterativo(totales),
        "recursivo": lambda: rec.sumar_recursivo(totales, n),
        "dividir": lambda: rec.sumar_recursivo_dividir(totales, 0, n),
    }
    return {
        "n": n,
        "resultados": {nombre: f() for nombre, f in funciones.items()},
        "tiempos": {nombre: _medir(f, 2000) for nombre, f in funciones.items()},
    }


def comparar_busqueda(codigo):
    """Busca un código de venta con la versión iterativa y la recursiva.

    Devuelve: n, posiciones (-1 si no existe) y tiempos en µs.
    """
    codigos = _codigos()
    funciones = {
        "iterativo": lambda: rec.buscar_iterativo(codigos, codigo),
        "recursivo": lambda: rec.buscar_recursivo(codigos, codigo),
    }
    return {
        "n": len(codigos),
        "codigo": codigo,
        "posiciones": {nombre: f() for nombre, f in funciones.items()},
        "tiempos": {nombre: _medir(f, 2000) for nombre, f in funciones.items()},
    }


def prueba_rendimiento(tamanos=None):
    """Suma listas sintéticas de distinto tamaño con las tres versiones.

    El sistema real tiene pocas ventas (MAX_VENTAS), así que se usan listas artificiales
    para ver el comportamiento con muchos datos. Si la versión recursiva excede el límite
    de recursión de Python se captura RecursionError y su tiempo queda en None.
    Devuelve (límite_de_recursión, filas) con filas = [{n, iterativo, recursivo, dividir}].
    """
    tamanos = tamanos or settings.TAMANOS_PRUEBA_RECURSION
    filas = []
    for n in tamanos:
        valores = [float(i % 50 + 1) for i in range(n)]
        repeticiones = max(3, 20000 // n)
        fila = {"n": n,
                "iterativo": _medir(lambda: rec.sumar_iterativo(valores), repeticiones),
                "dividir": _medir(lambda: rec.sumar_recursivo_dividir(valores, 0, n), repeticiones)}
        try:
            fila["recursivo"] = _medir(lambda: rec.sumar_recursivo(valores, n), repeticiones)
        except RecursionError:
            fila["recursivo"] = None
        filas.append(fila)
    return sys.getrecursionlimit(), filas


# ---------- reportes de negocio (pestaña Reportes) ----------
AGRUPACIONES = {"Vendedor": 7, "Cliente": 1, "Maquinaria": 3}   # posición del dato en la venta


def resumen_general():
    """Cifras clave del negocio, calculadas con recursividad.

    Devuelve un diccionario: n_ventas, monto_total, unidades, venta_mayor (tupla de la venta o
    None), valor_inventario y productos_stock_bajo.
    """
    lista, _ = ventas.listar_ventas()
    totales = [v[6] for v in lista]
    cantidades = [float(v[4]) for v in lista]
    n = len(lista)
    pos_mayor = rec.posicion_mayor(totales, 0, n)

    catalogo = productos.listar_productos()
    valores = [precio * stock for _c, _n, precio, stock, _b in catalogo]
    bajos = [bajo for _c, _n, _p, _s, bajo in catalogo]
    return {
        "n_ventas": n,
        "monto_total": rec.sumar_recursivo_dividir(totales, 0, n),
        "unidades": int(rec.sumar_recursivo_dividir(cantidades, 0, n)),
        "venta_mayor": lista[pos_mayor] if pos_mayor != -1 else None,
        "valor_inventario": rec.sumar_recursivo_dividir(valores, 0, len(valores)),
        "productos_stock_bajo": rec.contar_por_clave(bajos, True, 0, len(bajos)),
    }


def reporte_por(agrupacion):
    """Ventas agrupadas por "Vendedor", "Cliente" o "Maquinaria".

    Devuelve una lista de filas (grupo, n_ventas, unidades, total, porcentaje) ordenada de
    mayor a menor total. Cada total sale de una suma recursiva sobre las ventas del grupo.
    """
    posicion = AGRUPACIONES[agrupacion]
    lista, _ = ventas.listar_ventas()
    n = len(lista)
    claves = [v[1] if posicion == 1 else v[posicion] for v in lista]   # cliente: por documento
    totales = [v[6] for v in lista]
    cantidades = [float(v[4]) for v in lista]
    monto = rec.sumar_recursivo_dividir(totales, 0, n)

    nombres = {}                       # clave -> texto que se muestra (el cliente muestra su nombre)
    for v, clave in zip(lista, claves):
        if clave not in nombres:
            nombres[clave] = v[2] if posicion == 1 else clave
    filas = []
    for clave, nombre in nombres.items():
        total = rec.sumar_por_clave(claves, totales, clave, 0, n)
        filas.append((nombre,
                      rec.contar_por_clave(claves, clave, 0, n),
                      int(rec.sumar_por_clave(claves, cantidades, clave, 0, n)),
                      total,
                      total / monto * 100 if monto else 0.0))
    return sorted(filas, key=lambda fila: fila[3], reverse=True)
