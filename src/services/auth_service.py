"""Servicio de autenticación: empleados, sesión activa y permisos por rol."""
from config import settings
from exceptions.errores import (CapacidadLlenaError, CredencialesInvalidasError,
                                PermisoDenegadoError, SesionRequeridaError,
                                UsuarioDuplicadoError)
from repositories import empleado_repository as repo
from utils import seguridad

_sesion = None   # (usuario, nombre, rol) del empleado que inició sesión


def _crear(usuario, clave, nombre, rol):
    if repo.cantidad() == settings.MAX_EMPLEADOS:
        raise CapacidadLlenaError("empleados")
    if repo.buscar_por_usuario(usuario) != -1:
        raise UsuarioDuplicadoError()
    sal = seguridad.generar_sal()
    repo.guardar(usuario, seguridad.generar_hash(clave, sal), sal, nombre, rol)


def hay_empleados():
    return repo.cantidad() > 0


def crear_primer_administrador(usuario, clave, nombre):
    """Solo se permite cuando todavía no existe ningún empleado (primer arranque)."""
    if hay_empleados():
        raise PermisoDenegadoError()
    _crear(usuario, clave, nombre, settings.ROL_ADMIN)


def registrar_empleado(usuario, clave, nombre, rol):
    exigir_admin()
    _crear(usuario, clave, nombre, rol)


def iniciar_sesion(usuario, clave):
    """Mismo mensaje para usuario inexistente y contraseña errónea (no revela cuál falló)."""
    global _sesion
    pos = repo.buscar_por_usuario(usuario)
    if pos == -1:
        raise CredencialesInvalidasError()
    clave_hash, sal = repo.obtener_credenciales(pos)
    if not seguridad.verificar_clave(clave, sal, clave_hash):
        raise CredencialesInvalidasError()
    _sesion = repo.obtener(pos)
    return _sesion


def cerrar_sesion():
    global _sesion
    _sesion = None


def empleado_actual():
    return _sesion


def hay_sesion():
    return _sesion is not None


def es_admin():
    return _sesion is not None and _sesion[2] == settings.ROL_ADMIN


def exigir_sesion():
    if _sesion is None:
        raise SesionRequeridaError()


def exigir_admin():
    exigir_sesion()
    if not es_admin():
        raise PermisoDenegadoError()


def listar_empleados():
    exigir_admin()
    return [repo.obtener(i) for i in range(repo.cantidad())]
