"""Punto de entrada. Ejecutar desde la carpeta src:  python main.py"""
import datos_demo
from config import settings
from controllers import menu_controller


def main():
    if settings.CARGAR_DATOS_DEMO:
        datos_demo.cargar()
    menu_controller.iniciar()


if __name__ == "__main__":
    main()
