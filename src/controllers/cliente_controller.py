"""Controlador de clientes: registrar, buscar, modificar y listar."""
from controllers import entradas
from exceptions.errores import ErrorNegocio
from services import cliente_service as clientes
from services import validacion_service as val
from views import consola_view as vista


def registrar():
    try:
        documento = entradas.leer("DNI o RUC: ", val.validar_documento)
        if clientes.existe_cliente(documento):
            vista.mostrar_error("ya existe un cliente con ese documento.")
            return
        nombre = entradas.leer("Nombres / Razón social: ", val.validar_nombre)
        telefono = entradas.leer("Celular (9 dígitos): ", val.validar_telefono)
        clientes.registrar_cliente(documento, nombre, telefono)
        vista.mostrar_mensaje("Cliente registrado.")
    except ErrorNegocio as error:
        vista.mostrar_error(error)


def asegurar_cliente(documento):
    """Se usa al vender: si el cliente no existe, ofrece registrarlo. True si ya existe."""
    if clientes.existe_cliente(documento):
        return True
    vista.mostrar_mensaje("El cliente no está registrado.")
    if not entradas.confirmar("¿Registrarlo ahora? (S/N): "):
        return False
    try:
        nombre = entradas.leer("Nombres / Razón social: ", val.validar_nombre)
        telefono = entradas.leer("Celular (9 dígitos): ", val.validar_telefono)
        clientes.registrar_cliente(documento, nombre, telefono)
        vista.mostrar_mensaje("Cliente registrado.")
        return True
    except ErrorNegocio as error:
        vista.mostrar_error(error)
        return False


def buscar():
    documento = entradas.leer("DNI o RUC a buscar: ", val.validar_documento)
    cliente = clientes.buscar_cliente(documento)
    if cliente is None:
        vista.mostrar_mensaje("Cliente no encontrado.")
    else:
        vista.mostrar_clientes([cliente])


def modificar():
    documento = entradas.leer("DNI o RUC del cliente a modificar: ", val.validar_documento)
    cliente = clientes.buscar_cliente(documento)
    if cliente is None:
        vista.mostrar_mensaje("Cliente no encontrado.")
        return
    vista.mostrar_clientes([cliente])
    vista.mostrar_mensaje("Presione Enter para conservar el valor actual.")
    _, nombre_actual, telefono_actual = cliente
    nombre = entradas.leer_opcional(f"Nombres / Razón social [{nombre_actual}]: ",
                                    val.validar_nombre, nombre_actual)
    telefono = entradas.leer_opcional(f"Celular [{telefono_actual}]: ",
                                      val.validar_telefono, telefono_actual)
    try:
        clientes.modificar_cliente(documento, nombre, telefono)
        vista.mostrar_mensaje("Cliente modificado.")
    except ErrorNegocio as error:
        vista.mostrar_error(error)


def listar():
    vista.mostrar_clientes(clientes.listar_clientes())
