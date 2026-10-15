"""Ayudas para leer datos por consola. Las comparten todos los controladores."""
from exceptions.errores import ErrorNegocio
from views import consola_view as vista


def leer(mensaje, validador):
    """Repite la pregunta hasta que el validador acepte el dato."""
    while True:
        try:
            return validador(vista.pedir(mensaje))
        except ErrorNegocio as error:
            vista.mostrar_error(error)


def leer_opcional(mensaje, validador, actual):
    """Igual que leer, pero Enter vacío conserva el valor actual."""
    while True:
        texto = vista.pedir(mensaje)
        if texto.strip() == "":
            return actual
        try:
            return validador(texto)
        except ErrorNegocio as error:
            vista.mostrar_error(error)


def confirmar(mensaje):
    """Pregunta Sí/No. Solo 'S' (o 's') cuenta como sí."""
    return vista.pedir(mensaje).strip().upper() == "S"
