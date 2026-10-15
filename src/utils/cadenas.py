"""Procesamiento de cadenas. Funciones puras: no leen ni imprimen nada.

Equivale a lo que hacen DataMasker y ValidadorDatos en el proyecto Java.
"""
from exceptions.errores import ValorInvalidoError

_TILDES = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ü", "u"), ("ñ", "n"))


def normalizar_codigo(texto):
    """Quita espacios (strip + replace) y pasa a mayúsculas: ' v 001 ' -> 'V001'."""
    return texto.strip().replace(" ", "").upper()


def normalizar_nombre(texto):
    """Colapsa espacios repetidos (split + join) y pasa a mayúsculas."""
    return " ".join(texto.split()).upper()


def normalizar_usuario(texto):
    """Los usuarios se guardan en minúsculas y sin espacios en los extremos."""
    return texto.strip().lower()


def quitar_tildes(texto):
    """Reemplaza vocales con tilde y la ñ para comparar sin acentos."""
    for con_tilde, sin_tilde in _TILDES:
        texto = texto.replace(con_tilde, sin_tilde).replace(con_tilde.upper(), sin_tilde.upper())
    return texto


def contiene(texto, buscado):
    """Búsqueda textual tipo IndexOf: ignora mayúsculas y tildes."""
    texto = quitar_tildes(texto).lower()
    buscado = quitar_tildes(buscado).lower()
    return texto.find(buscado) != -1


def tipo_documento(documento):
    """Clasifica por longitud: 8 dígitos = DNI, 11 dígitos = RUC."""
    return "DNI" if len(documento) == 8 else "RUC"


def enmascarar_documento(documento):
    """Substring: deja visibles solo los 2 últimos dígitos (47581234 -> ******34)."""
    if len(documento) <= 2:
        return documento
    return "*" * (len(documento) - 2) + documento[-2:]


def abreviar(texto, maximo):
    """Substring: recorta un texto largo para que quepa en la columna."""
    if len(texto) <= maximo:
        return texto
    return texto[:maximo - 3] + "..."


def separar_registro(linea, separador, esperados):
    """Split: convierte 'V001;47581234;EXC-01;2' en una lista de campos limpios."""
    campos = [campo.strip() for campo in linea.split(separador)]
    if len(campos) != esperados:
        raise ValorInvalidoError(
            f"se esperaban {esperados} campos separados por '{separador}' "
            f"y se recibieron {len(campos)}.")
    return campos
