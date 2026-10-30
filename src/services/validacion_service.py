"""Servicio de validación: reglas sobre los datos. No lee ni imprime nada."""
from config import settings
from exceptions.errores import DocumentoInvalidoError, ValorInvalidoError
from utils import cadenas


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


def validar_codigo(texto):
    codigo = cadenas.normalizar_codigo(texto)
    if codigo == "":
        raise ValorInvalidoError("el código no puede estar vacío.")
    if len(codigo) > settings.LONGITUD_MAX_CODIGO:
        raise ValorInvalidoError(
            f"el código no puede superar los {settings.LONGITUD_MAX_CODIGO} caracteres."
        )
    return codigo


def validar_nombre(texto):
    nombre = cadenas.normalizar_nombre(texto)
    if nombre == "":
        raise ValorInvalidoError("el campo no puede estar vacío.")
    if len(nombre) > settings.LONGITUD_MAX_NOMBRE:
        raise ValorInvalidoError(
            f"el nombre no puede superar los {settings.LONGITUD_MAX_NOMBRE} caracteres."
        )
    return nombre


def validar_usuario(texto):
    """3 a 20 caracteres: letras, números o guion bajo."""
    usuario = cadenas.normalizar_usuario(texto)
    if not 3 <= len(usuario) <= 20 or not usuario.replace("_", "").isalnum():
        raise ValorInvalidoError("el usuario debe tener 3 a 20 letras, números o guion bajo.")
    return usuario


def validar_clave(texto):
    if len(texto) < settings.LONGITUD_MIN_CLAVE:
        raise ValorInvalidoError(
            f"la contraseña debe tener al menos {settings.LONGITUD_MIN_CLAVE} caracteres.")
    return texto


def validar_telefono(texto):
    """Celular peruano: 9 dígitos que empiezan con 9."""
    telefono = texto.strip()
    if (not telefono.isdigit() or len(telefono) != settings.LONGITUD_TELEFONO
            or not telefono.startswith("9")):
        raise ValorInvalidoError("celular de 9 dígitos que empieza con 9.")
    return telefono


def validar_rol(texto):
    """Recibe la opción del menú (1 = Administrador, 2 = Vendedor) y devuelve el rol."""
    opcion = texto.strip()
    if opcion not in ("1", "2"):
        raise ValorInvalidoError("elija 1 (Administrador) o 2 (Vendedor).")
    return settings.ROLES[int(opcion) - 1]


def validar_entero_positivo(texto):
    try:
        n = int(texto)
    except ValueError:
        raise ValorInvalidoError("ingrese un número entero mayor a 0.")
    if n <= 0:
        raise ValorInvalidoError("ingrese un número entero mayor a 0.")
    return n


def validar_entero_no_negativo(texto):
    try:
        n = int(texto)
    except ValueError:
        raise ValorInvalidoError("ingrese un número entero (0 o mayor).")
    if n < 0:
        raise ValorInvalidoError("ingrese un número entero (0 o mayor).")
    return n


def validar_decimal_positivo(texto):
    try:
        n = float(texto)
    except ValueError:
        raise ValorInvalidoError("ingrese un monto mayor a 0.")

    if n <= 0:
        raise ValorInvalidoError("ingrese un monto mayor a 0.")

    return round(n, 2)
