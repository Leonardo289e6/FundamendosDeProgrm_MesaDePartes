"""Servicio de clientes: reglas de negocio. Usa el repositorio, nunca los arreglos."""
from almacenamiento import gestor
from config import settings
from exceptions.errores import (CapacidadLlenaError, ClienteDuplicadoError,
                                ClienteNoEncontradoError)
from repositories import cliente_repository as repo
from services import auth_service as auth


def registrar_cliente(documento, nombre, telefono):
    auth.exigir_sesion()
    if repo.cantidad() == settings.MAX_CLIENTES:
        raise CapacidadLlenaError("clientes")
    if repo.buscar_por_documento(documento) != -1:
        raise ClienteDuplicadoError()
    repo.guardar(documento, nombre, telefono)
    gestor.confirmar()


def existe_cliente(documento):
    return repo.buscar_por_documento(documento) != -1


def buscar_cliente(documento):
    """Devuelve (documento, nombre, teléfono) o None."""
    pos = repo.buscar_por_documento(documento)
    if pos == -1:
        return None
    return repo.obtener(pos)


def obtener_cliente(documento):
    cliente = buscar_cliente(documento)
    if cliente is None:
        raise ClienteNoEncontradoError()
    return cliente


def modificar_cliente(documento, nombre, telefono):
    auth.exigir_sesion()
    pos = repo.buscar_por_documento(documento)
    if pos == -1:
        raise ClienteNoEncontradoError()
    repo.actualizar(pos, nombre, telefono)
    gestor.confirmar()


def listar_clientes():
    return [repo.obtener(i) for i in range(repo.cantidad())]
