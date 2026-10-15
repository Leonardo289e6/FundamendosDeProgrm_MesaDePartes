"""Controlador de acceso: login, primer administrador y gestión de empleados."""
from config import settings
from controllers import entradas
from exceptions.errores import ErrorNegocio
from services import auth_service as auth
from services import validacion_service as val
from utils import cadenas
from views import consola_view as vista


def _leer_clave_nueva():
    """Pide la contraseña dos veces hasta que coincidan y sea válida."""
    while True:
        try:
            clave = val.validar_clave(vista.pedir_clave("Contraseña: "))
        except ErrorNegocio as error:
            vista.mostrar_error(error)
            continue
        if clave == vista.pedir_clave("Repita la contraseña: "):
            return clave
        vista.mostrar_error("las contraseñas no coinciden.")


def primer_arranque():
    """No hay empleados: se crea el primer administrador."""
    vista.mostrar_mensaje("\nPrimer uso: cree la cuenta del administrador.")
    usuario = entradas.leer("Usuario: ", val.validar_usuario)
    nombre = entradas.leer("Nombres completos: ", val.validar_nombre)
    clave = _leer_clave_nueva()
    try:
        auth.crear_primer_administrador(usuario, clave, nombre)
        vista.mostrar_mensaje("Administrador creado.")
    except ErrorNegocio as error:
        vista.mostrar_error(error)


def login():
    """Hasta 3 intentos. Devuelve True si inició sesión; False si salió o agotó intentos."""
    for intento in range(1, settings.MAX_INTENTOS_LOGIN + 1):
        usuario = cadenas.normalizar_usuario(vista.pedir("\nUsuario (Enter para salir): "))
        if usuario == "":
            return False
        clave = vista.pedir_clave("Contraseña: ")
        try:
            auth.iniciar_sesion(usuario, clave)
            return True
        except ErrorNegocio as error:
            vista.mostrar_error(f"{error} (intento {intento}/{settings.MAX_INTENTOS_LOGIN})")
    vista.mostrar_mensaje("Se agotaron los intentos.")
    return False


def registrar_empleado():
    try:
        auth.exigir_admin()
        usuario = entradas.leer("Usuario: ", val.validar_usuario)
        nombre = entradas.leer("Nombres completos: ", val.validar_nombre)
        rol = entradas.leer("Rol (1 = Administrador, 2 = Vendedor): ", val.validar_rol)
        clave = _leer_clave_nueva()
        auth.registrar_empleado(usuario, clave, nombre, rol)
        vista.mostrar_mensaje("Empleado registrado.")
    except ErrorNegocio as error:
        vista.mostrar_error(error)


def listar_empleados():
    try:
        vista.mostrar_empleados(auth.listar_empleados())
    except ErrorNegocio as error:
        vista.mostrar_error(error)
