"""Servicio de ventas: reglas de negocio. Une ventas con clientes, inventario y sesión."""
from almacenamiento import gestor
from config import settings
from exceptions.errores import (CapacidadLlenaError, CodigoDuplicadoError,
                                StockInsuficienteError, VentaNoEncontradaError)
from repositories import venta_repository as repo
from services import auth_service as auth
from services import cliente_service as clientes
from services import producto_service as productos
from utils import cadenas
from utils import recursividad


def calcular_total(cantidad, precio_unitario):
    return round(cantidad * precio_unitario * (1 + settings.IGV), 2)   # 2 decimales: igual que en archivo y BD


def _detalle(venta):
    """Convierte la venta guardada (con claves) en una tupla legible, con nombres.

    Devuelve (código, documento, cliente, maquinaria, cantidad, precio, total, vendedor).
    """
    codigo, documento, cod_producto, cantidad, precio, total, vendedor = venta
    cliente = clientes.obtener_cliente(documento)[1]
    maquinaria = productos.obtener_producto(cod_producto)[1]
    return (codigo, documento, cliente, maquinaria, cantidad, precio, total, vendedor)


def validar_codigo_nuevo(codigo):
    if repo.cantidad() == settings.MAX_VENTAS:
        raise CapacidadLlenaError("ventas")
    if repo.buscar_por_codigo(codigo) != -1:
        raise CodigoDuplicadoError()


def registrar_venta(codigo, documento, cod_producto, cantidad):
    """Registra la venta, descuenta el stock y devuelve el total con IGV."""
    auth.exigir_sesion()
    validar_codigo_nuevo(codigo)
    clientes.obtener_cliente(documento)
    precio = productos.obtener_producto(cod_producto)[2]
    productos.descontar_stock(cod_producto, cantidad)
    total = calcular_total(cantidad, precio)
    repo.guardar(codigo, documento, cod_producto, cantidad, precio, total,
                 auth.empleado_actual()[0])
    gestor.confirmar()      # venta + stock descontado se guardan juntos
    return total


def buscar_venta(codigo):
    """Devuelve la venta con nombres (tupla de 8) o None."""
    pos = repo.buscar_por_codigo(codigo)
    if pos == -1:
        return None
    return _detalle(repo.obtener(pos))


def buscar_venta_recursiva(codigo):
    """Igual que buscar_venta, pero la posición se halla con búsqueda recursiva."""
    codigos = [repo.obtener(i)[0] for i in range(repo.cantidad())]
    pos = recursividad.buscar_recursivo(codigos, codigo)
    if pos == -1:
        return None
    return _detalle(repo.obtener(pos))


def monto_acumulado_recursivo():
    """Monto total de todas las ventas, sumado con recursividad."""
    totales = [repo.obtener(i)[5] for i in range(repo.cantidad())]
    return recursividad.sumar_recursivo(totales, len(totales))


def modificar_venta(codigo, documento, cod_producto, cantidad):
    """Cambia cliente, producto o cantidad. Ajusta el stock y recalcula el total.

    cod_producto = None conserva el producto que ya tenía la venta.
    """
    auth.exigir_sesion()
    pos = repo.buscar_por_codigo(codigo)
    if pos == -1:
        raise VentaNoEncontradaError()
    _, _, prod_anterior, cant_anterior, precio_anterior, _, _ = repo.obtener(pos)
    if cod_producto is None:
        cod_producto = prod_anterior
    clientes.obtener_cliente(documento)
    producto = productos.obtener_producto(cod_producto)
    productos.devolver_stock(prod_anterior, cant_anterior)
    try:
        productos.descontar_stock(cod_producto, cantidad)
    except StockInsuficienteError:
        productos.descontar_stock(prod_anterior, cant_anterior)   # deshace la devolución
        raise
    precio = precio_anterior if cod_producto == prod_anterior else producto[2]
    total = calcular_total(cantidad, precio)
    repo.actualizar(pos, documento, cod_producto, cantidad, precio, total)
    gestor.confirmar()
    return total


def eliminar_venta(codigo):
    """Solo administradores. Devuelve las unidades al inventario."""
    auth.exigir_admin()
    pos = repo.buscar_por_codigo(codigo)
    if pos == -1:
        raise VentaNoEncontradaError()
    _, _, cod_producto, cantidad, _, _, _ = repo.obtener(pos)
    productos.devolver_stock(cod_producto, cantidad)
    repo.eliminar(pos)
    gestor.confirmar()


def buscar_por_texto(texto):
    """Devuelve las ventas cuyo cliente o maquinaria contiene el texto."""
    encontradas = []
    for i in range(repo.cantidad()):
        venta = _detalle(repo.obtener(i))
        if cadenas.contiene(venta[2], texto) or cadenas.contiene(venta[3], texto):
            encontradas.append(venta)
    return encontradas


def ordenar_ventas(criterio):
    """criterio 1: código (burbuja). criterio 2: total descendente (selección)."""
    if criterio == 1:
        repo.ordenar_por_codigo()
    else:
        repo.ordenar_por_total()


def listar_ventas():
    """Devuelve la lista de ventas (con nombres) y el monto acumulado."""
    ventas = []
    suma = 0.0
    for i in range(repo.cantidad()):
        venta = _detalle(repo.obtener(i))
        ventas.append(venta)
        suma = suma + venta[6]
    return ventas, suma


def resumen_unidades():
    """Arreglo bidimensional: unidades vendidas por tipo de cliente (filas) y maquinaria (columnas).

    Fila 0 = clientes con DNI, fila 1 = clientes con RUC. Devuelve (maquinas, matriz).
    """
    detalle = [_detalle(repo.obtener(i)) for i in range(repo.cantidad())]
    maquinas = []
    for venta in detalle:
        if venta[3] not in maquinas:
            maquinas.append(venta[3])
    matriz = [[0] * len(maquinas) for _ in range(2)]
    for venta in detalle:
        fila = 0 if cadenas.tipo_documento(venta[1]) == "DNI" else 1
        matriz[fila][maquinas.index(venta[3])] += venta[4]
    return maquinas, matriz
