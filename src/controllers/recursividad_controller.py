"""Controlador de recursividad: muestra y compara las versiones iterativa y recursiva."""
from controllers import entradas
from services import reporte_service as reportes
from services import validacion_service as val
from services import venta_service as ventas
from views import consola_view as vista
from views import texto_reportes as textos


def explicacion():
    vista.mostrar_mensaje(textos.EXPLICACION)


def acumulado():
    vista.mostrar_mensaje(textos.texto_acumulado(reportes.comparar_acumulado()))


def busqueda():
    codigo = entradas.leer("Código de venta a buscar: ", val.validar_codigo)
    vista.mostrar_mensaje(textos.texto_busqueda(reportes.comparar_busqueda(codigo)))
    venta = ventas.buscar_venta_recursiva(codigo)
    if venta is not None:
        vista.mostrar_encabezado()
        vista.mostrar_venta(venta)


def rendimiento():
    vista.mostrar_mensaje("Calculando, puede tardar unos segundos...")
    limite, filas = reportes.prueba_rendimiento()
    vista.mostrar_mensaje(textos.texto_rendimiento(limite, filas))
