"""Preparación y cierre del sistema. Lo comparten la consola y la interfaz gráfica."""
from almacenamiento import gestor
from config import settings
from exceptions.errores import ErrorNegocio


def preparar():
    """Elige el almacén (archivos o PostgreSQL), carga y valida los datos guardados.

    Si todavía no hay empleados, la pantalla de inicio pide crear al administrador.
    Lanza ErrorPersistencia si los datos no se pueden leer o están corruptos
    (en ese caso NO se sobrescribe nada).
    """
    gestor.configurar(settings.PERSISTENCIA)
    gestor.cargar()


def cerrar():
    """Guardado final al salir. Devuelve un texto de error o None si todo salió bien."""
    try:
        gestor.confirmar()
    except ErrorNegocio as error:
        return str(error)
    return None
