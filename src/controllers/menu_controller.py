"""Controlador del menú: login, menú principal y submenús. Solo navega; no tiene reglas."""
from controllers import auth_controller, cliente_controller, producto_controller
from controllers import recursividad_controller, venta_controller
from services import auth_service as auth
from views import consola_view as vista


def _ejecutar_menu(titulo, opciones, texto_cero="Volver"):
    """opciones: lista de (número, texto, función). Repite hasta elegir 0."""
    while True:
        vista.mostrar_menu(titulo, [(num, texto) for num, texto, _ in opciones], texto_cero)
        try:
            opcion = int(vista.pedir("Opción: "))
        except ValueError:
            opcion = -1
        if opcion == 0:
            return
        for numero, _, funcion in opciones:
            if numero == opcion:
                funcion()
                break
        else:
            vista.mostrar_mensaje("Opción no válida.")


def _menu_ventas():
    _ejecutar_menu("VENTAS", [
        (1, "Registrar venta", venta_controller.registrar),
        (2, "Buscar por código", venta_controller.buscar),
        (3, "Ordenar", venta_controller.ordenar),
        (4, "Listar ventas", venta_controller.listar),
        (5, "Modificar venta", venta_controller.modificar),
        (6, "Eliminar venta (solo administrador)", venta_controller.eliminar),
        (7, "Buscar por texto (cliente o maquinaria)", venta_controller.buscar_texto),
        (8, "Resumen de unidades (tipo de cliente x maquinaria)", venta_controller.resumen),
        (9, "Registro rápido (campos separados por ;)", venta_controller.registro_rapido),
    ])


def _menu_clientes():
    _ejecutar_menu("CLIENTES", [
        (1, "Registrar cliente", cliente_controller.registrar),
        (2, "Buscar por documento", cliente_controller.buscar),
        (3, "Modificar cliente", cliente_controller.modificar),
        (4, "Listar clientes", cliente_controller.listar),
    ])


def _menu_inventario():
    _ejecutar_menu("INVENTARIO", [
        (1, "Listar inventario", producto_controller.listar),
        (2, "Consultar producto", producto_controller.consultar),
        (3, "Registrar producto (solo administrador)", producto_controller.registrar),
        (4, "Reponer stock (solo administrador)", producto_controller.reponer),
    ])


def _menu_empleados():
    _ejecutar_menu("EMPLEADOS", [
        (1, "Registrar empleado", auth_controller.registrar_empleado),
        (2, "Listar empleados", auth_controller.listar_empleados),
    ])


def _menu_recursividad():
    _ejecutar_menu("RECURSIVIDAD (iterativo vs recursivo)", [
        (1, "Explicación: caso base, caso recursivo y parada", recursividad_controller.explicacion),
        (2, "Acumulado de ventas (iterativo vs recursivo)", recursividad_controller.acumulado),
        (3, "Buscar venta por código (iterativo vs recursivo)", recursividad_controller.busqueda),
        (4, "Prueba de rendimiento y desbordamiento", recursividad_controller.rendimiento),
    ])


def _menu_principal():
    opciones = [
        (1, "Ventas", _menu_ventas),
        (2, "Clientes", _menu_clientes),
        (3, "Inventario", _menu_inventario),
        (4, "Recursividad", _menu_recursividad),
    ]
    if auth.es_admin():
        opciones.append((5, "Empleados", _menu_empleados))
    _ejecutar_menu("MAQUINARIAS NARVÁEZ S.A.C. - MENÚ PRINCIPAL", opciones, "Cerrar sesión")


def iniciar():
    """Flujo completo: primer uso (si hace falta) -> login -> menú -> cerrar sesión."""
    vista.mostrar_mensaje("===== MAQUINARIAS NARVÁEZ S.A.C. - CONTROL DE VENTAS =====")
    if not auth.hay_empleados():
        auth_controller.primer_arranque()
    while auth_controller.login():
        vista.mostrar_sesion(auth.empleado_actual())
        _menu_principal()
        auth.cerrar_sesion()
        vista.mostrar_mensaje("Sesión cerrada.")
    vista.mostrar_mensaje("Programa finalizado.")
