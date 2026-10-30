"""Errores propios del sistema. Todos heredan de ErrorNegocio."""


class ErrorNegocio(Exception):
    """Error base: el controlador puede capturar cualquiera de sus hijos."""


class ValorInvalidoError(ErrorNegocio):
    """Dato vacío, no numérico o fuera de rango."""


class DocumentoInvalidoError(ErrorNegocio):
    def __init__(self):
        super().__init__("DNI de 8 dígitos o RUC de 11 dígitos (inicia en 10 o 20).")


class CapacidadLlenaError(ErrorNegocio):
    def __init__(self, entidad):
        super().__init__(f"no hay espacio para más {entidad}.")


# --- sesión y permisos ---
class CredencialesInvalidasError(ErrorNegocio):
    def __init__(self):
        super().__init__("usuario o contraseña incorrectos.")


class SesionRequeridaError(ErrorNegocio):
    def __init__(self):
        super().__init__("debe iniciar sesión.")


class PermisoDenegadoError(ErrorNegocio):
    def __init__(self):
        super().__init__("su rol no tiene permiso para esta acción.")


class UsuarioDuplicadoError(ErrorNegocio):
    def __init__(self):
        super().__init__("ese usuario ya existe.")


# --- clientes ---
class ClienteDuplicadoError(ErrorNegocio):
    def __init__(self):
        super().__init__("ya existe un cliente con ese documento.")


class ClienteNoEncontradoError(ErrorNegocio):
    def __init__(self):
        super().__init__("el cliente no está registrado.")


# --- inventario ---
class ProductoDuplicadoError(ErrorNegocio):
    def __init__(self):
        super().__init__("ya existe un producto con ese código.")


class ProductoNoEncontradoError(ErrorNegocio):
    def __init__(self):
        super().__init__("el producto no está registrado.")


class StockInsuficienteError(ErrorNegocio):
    def __init__(self, disponible):
        super().__init__(f"stock insuficiente. Disponible: {disponible} unidad(es).")


# --- ventas ---
class CodigoDuplicadoError(ErrorNegocio):
    def __init__(self):
        super().__init__("ese código de venta ya está registrado.")


class VentaNoEncontradaError(ErrorNegocio):
    def __init__(self):
        super().__init__("no existe una venta con ese código.")




class InventarioLlenoError(ErrorNegocio):
    def __init__(self):
        super().__init__("no hay espacio para más ventas.")


# --- persistencia ---
class ErrorPersistencia(ErrorNegocio):
    """No se pudieron leer o guardar los datos (archivo, permisos, conexión...)."""


class DatosCorruptosError(ErrorPersistencia):
    """Los datos leídos no cumplen las reglas de integridad."""
    def __init__(self, origen, detalle):
        super().__init__(f"datos inválidos en {origen}: {detalle}")

