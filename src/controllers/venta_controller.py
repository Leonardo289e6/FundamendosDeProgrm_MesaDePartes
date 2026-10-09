"""Controlador: coordina la vista y los servicios. Atrapa los errores de negocio."""
from exceptions.errores import ErrorNegocio
from services import validacion_service as val
from services import venta_service as ventas
from views import consola_view as vista


def _leer(mensaje, validador):
    """Repite la pregunta hasta que el validador acepte el dato."""
    while True:
        try:
            return validador(vista.pedir(mensaje))
        except ErrorNegocio as error:
            vista.mostrar_error(error)


def registrar(n):
    try:
        codigo = val.validar_texto(vista.pedir("Código de venta: ")).upper()
        ventas.validar_codigo_nuevo(n, codigo)
        documento = _leer("DNI o RUC del cliente: ", val.validar_documento)
        cliente = _leer("Nombres / Razón social: ", val.validar_texto)
        maquina = _leer("Tipo de maquinaria: ", val.validar_texto)
        cantidad = _leer("Cantidad: ", val.validar_entero_positivo)
        precio = _leer("Precio unitario (S/): ", val.validar_decimal_positivo)
        total = ventas.calcular_total(cantidad, precio)
        n = ventas.registrar_venta(n, codigo, documento, cliente, maquina, cantidad, precio)
        vista.mostrar_mensaje(f"Venta registrada. Total con IGV: S/ {total:.2f}")
    except ErrorNegocio as error:
        vista.mostrar_error(error)
    return n


def buscar(n):
    codigo = _leer("Código a buscar: ", val.validar_texto).upper()
    venta = ventas.buscar_venta(n, codigo)
    if venta is None:
        vista.mostrar_mensaje("Código no encontrado.")
    else:
        vista.mostrar_venta(venta)
    return n


def ordenar(n):
    ventas.ordenar_ventas(n)
    vista.mostrar_mensaje("Ventas ordenadas por código.")
    return n


def listar(n):
    lista, suma = ventas.listar_ventas(n)
    vista.mostrar_listado(lista, suma)
    return n


def iniciar():
    """Ciclo del menú principal. Cada opción es una función del diccionario."""
    opciones = {1: registrar, 2: buscar, 3: ordenar, 4: listar}
    n = 0
    opcion = -1
    while opcion != 0:
        vista.mostrar_menu()
        try:
            opcion = int(vista.pedir("Opción: "))
        except ValueError:
            opcion = -1
        if opcion in opciones:
            n = opciones[opcion](n)
        elif opcion != 0:
            vista.mostrar_mensaje("Opción no válida.")
    vista.mostrar_mensaje("Programa finalizado.")
