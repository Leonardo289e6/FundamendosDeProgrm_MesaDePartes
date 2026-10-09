"""Errores propios del sistema. Todos heredan de ErrorNegocio."""


class ErrorNegocio(Exception):
    """Error base: el controlador puede capturar cualquiera de sus hijos."""


class ValorInvalidoError(ErrorNegocio):
    """Dato vacío, no numérico o fuera de rango."""


class DocumentoInvalidoError(ErrorNegocio):
    def __init__(self):
        super().__init__("DNI de 8 dígitos o RUC de 11 dígitos (inicia en 10 o 20).")


class InventarioLlenoError(ErrorNegocio):
    def __init__(self):
        super().__init__("no hay espacio para más ventas.")


class CodigoDuplicadoError(ErrorNegocio):
    def __init__(self):
        super().__init__("ese código de venta ya está registrado.")
