"""Controlador de ventas: coordina la vista y los servicios. Atrapa los errores de negocio."""
from config import settings
from controllers import cliente_controller, entradas
from exceptions.errores import ErrorNegocio, StockInsuficienteError
from services import auth_service as auth
from services import producto_service as productos
from services import validacion_service as val
from services import venta_service as ventas
from utils import cadenas
from views import consola_view as vista


def _leer_producto():
    """Pide el código hasta que exista. Enter vacío cancela (devuelve None)."""
    while True:
        texto = vista.pedir("Código del producto (Enter para cancelar): ")
        if texto.strip() == "":
            return None
        try:
            codigo = val.validar_codigo(texto)
            producto = productos.obtener_producto(codigo)
        except ErrorNegocio as error:
            vista.mostrar_error(error)
            continue
        vista.mostrar_productos([producto + (False,)])
        return codigo


def registrar():
    try:
        codigo = val.validar_codigo(vista.pedir("Código de venta: "))
        ventas.validar_codigo_nuevo(codigo)
        documento = entradas.leer("DNI o RUC del cliente: ", val.validar_documento)
        if not cliente_controller.asegurar_cliente(documento):
            vista.mostrar_mensaje("Venta cancelada.")
            return
        cod_producto = _leer_producto()
        if cod_producto is None:
            vista.mostrar_mensaje("Venta cancelada.")
            return
        while True:
            cantidad = entradas.leer("Cantidad: ", val.validar_entero_positivo)
            try:
                total = ventas.registrar_venta(codigo, documento, cod_producto, cantidad)
                break
            except StockInsuficienteError as error:
                vista.mostrar_error(error)
        vista.mostrar_mensaje(f"Venta registrada. Total con IGV: S/ {total:.2f}")
    except ErrorNegocio as error:
        vista.mostrar_error(error)


def registro_rapido():
    """Una sola línea con campos separados por ';' (usa split)."""
    try:
        linea = vista.pedir("Código;DNI/RUC;Código de producto;Cantidad: ")
        campos = cadenas.separar_registro(linea, settings.SEPARADOR_REGISTRO,
                                          settings.CAMPOS_REGISTRO)
        codigo = val.validar_codigo(campos[0])
        documento = val.validar_documento(campos[1])
        cod_producto = val.validar_codigo(campos[2])
        cantidad = val.validar_entero_positivo(campos[3])
        total = ventas.registrar_venta(codigo, documento, cod_producto, cantidad)
        vista.mostrar_mensaje(f"Venta registrada. Total con IGV: S/ {total:.2f}")
    except ErrorNegocio as error:
        vista.mostrar_error(error)


def buscar():
    codigo = entradas.leer("Código a buscar: ", val.validar_codigo)
    venta = ventas.buscar_venta(codigo)
    if venta is None:
        vista.mostrar_mensaje("Código no encontrado.")
    else:
        vista.mostrar_encabezado()
        vista.mostrar_venta(venta)


def buscar_texto():
    texto = entradas.leer("Texto a buscar (cliente o maquinaria): ", val.validar_texto)
    encontradas = ventas.buscar_por_texto(texto)
    if len(encontradas) == 0:
        vista.mostrar_mensaje("Sin coincidencias.")
    else:
        vista.mostrar_coincidencias(encontradas)


def modificar():
    codigo = entradas.leer("Código de la venta a modificar: ", val.validar_codigo)
    venta = ventas.buscar_venta(codigo)
    if venta is None:
        vista.mostrar_mensaje("Código no encontrado.")
        return
    vista.mostrar_encabezado()
    vista.mostrar_venta(venta)
    vista.mostrar_mensaje("Presione Enter para conservar el valor actual.")
    doc = venta[1]
    cantidad_actual = venta[4]
    documento = entradas.leer_opcional(f"DNI o RUC [{doc}]: ", val.validar_documento, doc)
    cod_producto = entradas.leer_opcional("Código del producto [Enter = el mismo]: ",
                                          val.validar_codigo, None)
    cantidad = entradas.leer_opcional(f"Cantidad [{cantidad_actual}]: ",
                                      val.validar_entero_positivo, cantidad_actual)
    try:
        total = ventas.modificar_venta(codigo, documento, cod_producto, cantidad)
        vista.mostrar_mensaje(f"Venta modificada. Nuevo total con IGV: S/ {total:.2f}")
    except ErrorNegocio as error:
        vista.mostrar_error(error)


def eliminar():
    try:
        auth.exigir_admin()   # se avisa antes de pedir datos
    except ErrorNegocio as error:
        vista.mostrar_error(error)
        return
    codigo = entradas.leer("Código de la venta a eliminar: ", val.validar_codigo)
    venta = ventas.buscar_venta(codigo)
    if venta is None:
        vista.mostrar_mensaje("Código no encontrado.")
        return
    vista.mostrar_encabezado()
    vista.mostrar_venta(venta)
    if not entradas.confirmar("¿Eliminar esta venta? (S/N): "):
        vista.mostrar_mensaje("Eliminación cancelada.")
        return
    try:
        ventas.eliminar_venta(codigo)
        vista.mostrar_mensaje("Venta eliminada. Las unidades volvieron al inventario.")
    except ErrorNegocio as error:
        vista.mostrar_error(error)


def ordenar():
    criterio = vista.pedir("Ordenar por: 1) código (burbuja)  2) total mayor a menor (selección): ")
    if criterio.strip() not in ("1", "2"):
        vista.mostrar_mensaje("Criterio no válido.")
        return
    ventas.ordenar_ventas(int(criterio))
    if criterio.strip() == "1":
        vista.mostrar_mensaje("Ventas ordenadas por código.")
    else:
        vista.mostrar_mensaje("Ventas ordenadas por total (mayor a menor).")


def listar():
    lista, suma = ventas.listar_ventas()
    vista.mostrar_listado(lista, suma)


def resumen():
    if len(ventas.listar_ventas()[0]) == 0:
        vista.mostrar_mensaje("No hay ventas registradas.")
        return
    maquinas, matriz = ventas.resumen_unidades()
    vista.mostrar_mensaje("Unidades vendidas por tipo de cliente y maquinaria:")
    vista.mostrar_resumen(maquinas, matriz)
