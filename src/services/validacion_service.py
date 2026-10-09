"""Servicio de validación: reglas sobre los datos. No lee ni imprime nada."""
from config import settings
from exceptions.errores import DocumentoInvalidoError, ValorInvalidoError


def es_documento_valido(doc):
    """DNI: 8 dígitos. RUC: 11 dígitos que empiezan con 10 o 20."""
    if not doc.isdigit():
        return False
    if len(doc) == settings.LONGITUD_DNI:
        return True
    if len(doc) == settings.LONGITUD_RUC and doc.startswith(settings.PREFIJOS_RUC):
        return True
    return False


def validar_documento(doc):
    doc = doc.strip()
    if not es_documento_valido(doc):
        raise DocumentoInvalidoError()
    return doc


def validar_texto(texto):
    texto = texto.strip()
    if texto == "":
        raise ValorInvalidoError("el campo no puede estar vacío.")
    return texto


def validar_entero_positivo(texto):
    try:
        n = int(texto)
    except ValueError:
        raise ValorInvalidoError("ingrese un número entero mayor a 0.")
    if n <= 0:
        raise ValorInvalidoError("ingrese un número entero mayor a 0.")
    return n


def validar_decimal_positivo(texto):
    try:
        n = float(texto)
    except ValueError:
        raise ValorInvalidoError("ingrese un monto mayor a 0.")
    if n <= 0:
        raise ValorInvalidoError("ingrese un monto mayor a 0.")
    return n
