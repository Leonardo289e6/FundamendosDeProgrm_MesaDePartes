"""Punto de entrada. Ejecutar desde la carpeta src:

    python main.py             interfaz gráfica (Tkinter)
    python main.py --consola   menú por consola
"""
import sys

import arranque
from almacenamiento import gestor
from exceptions.errores import ErrorNegocio


def _consola():
    from controllers import menu_controller
    menu_controller.iniciar()
    aviso = arranque.cerrar()
    if aviso:
        print(f"Aviso al guardar: {aviso}")


def main():
    try:
        arranque.preparar()
    except ErrorNegocio as error:
        print(f"No se pudo iniciar el sistema: {error}")
        return
    print(f"Datos: {gestor.descripcion()}")
    if "--consola" in sys.argv[1:]:
        _consola()
        return
    try:
        from gui import app
    except ModuleNotFoundError as error:
        if error.name != "tkinter":
            raise
        print("No se encontró Tkinter (en Linux: sudo apt install python3-tk). Se abre la consola.")
        _consola()
        return
    app.iniciar()           # la ventana hace el guardado final al cerrarse


if __name__ == "__main__":
    main()
