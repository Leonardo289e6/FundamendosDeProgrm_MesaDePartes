"""Controlador de inventario: registrar productos, consultar y reponer stock."""
from controllers import entradas
from exceptions.errores import ErrorNegocio
from services import auth_service as auth
from services import producto_service as productos
from services import validacion_service as val
from views import consola_view as vista


def registrar():
    try:
        auth.exigir_admin()
        codigo = entradas.leer("Código del producto: ", val.validar_codigo)
        if productos.buscar_producto(codigo) is not None:
            vista.mostrar_error("ya existe un producto con ese código.")
            return
        nombre = entradas.leer("Tipo de maquinaria: ", val.validar_nombre)
        precio = entradas.leer("Precio unitario (S/, sin IGV): ", val.validar_decimal_positivo)
        stock = entradas.leer("Stock inicial: ", val.validar_entero_no_negativo)
        productos.registrar_producto(codigo, nombre, precio, stock)
        vista.mostrar_mensaje("Producto registrado.")
    except ErrorNegocio as error:
        vista.mostrar_error(error)


def listar():
    vista.mostrar_productos(productos.listar_productos())


def consultar():
    codigo = entradas.leer("Código del producto: ", val.validar_codigo)
    producto = productos.buscar_producto(codigo)
    if producto is None:
        vista.mostrar_mensaje("Producto no encontrado.")
    else:
        vista.mostrar_productos([producto + (False,)])


def reponer():
    try:
        auth.exigir_admin()
        codigo = entradas.leer("Código del producto: ", val.validar_codigo)
        cantidad = entradas.leer("Unidades a agregar: ", val.validar_entero_positivo)
        nuevo = productos.reponer_stock(codigo, cantidad)
        vista.mostrar_mensaje(f"Stock actualizado. Disponible: {nuevo} unidad(es).")
    except ErrorNegocio as error:
        vista.mostrar_error(error)
