"""Punto de entrada. Ejecutar desde la carpeta src:  python -m sistemaventas.main"""
from controllers import venta_controller


def main():
    venta_controller.iniciar()


if __name__ == "__main__":
    main()
