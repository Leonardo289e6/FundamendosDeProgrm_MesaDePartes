"""
Sistema de Registro de Usuarios y Ventas
Maquinarias Narváez SAC (Trujillo, La Libertad)

Por ahora solo incluye el registro y guardado de CLIENTES.
El módulo de ventas se agregará después en modulos/ventas/.

Ejecutar con: python main.py
"""

from modulos.clientes import gestor as clientes_gestor
from modulos.clientes import almacenamiento as clientes_almacenamiento


def mostrar_menu():
    print("\n=========================================")
    print(" SISTEMA - MAQUINARIAS NARVAEZ SAC")
    print("=========================================")
    print("1. Registrar cliente")
    print("2. Listar clientes")
    print("3. Buscar cliente por DNI")
    print("4. Salir y guardar")
    print("=========================================")


def main():
    # Carga de datos al iniciar (persistencia con archivos)
    lista_clientes = clientes_almacenamiento.cargar_clientes()

    opcion = ""
    while opcion != "4":
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()
        if opcion == "1":
            while True:
                identifi = input("Identificación del cliente (1.DNI / 2.RUC): ").strip()
                if identifi == "1":
                    tipo_doc = "DNI"
                    documento = input("Ingrese DNI: ").strip()
                    break
                elif identifi == "2":
                    tipo_doc = "RUC"
                    documento = input("Ingrese RUC: ").strip()
                    break
                else:
                    print("Ingrese una opción válida.")
                    
            nombre = input("Nombres: ").strip()
            apellido = input("Apellidos: ").strip()
            telefono = input("Teléfono: ").strip()
            email = input("Email: ").strip()
            
            clientes_gestor.registrar_cliente(lista_clientes, tipo_doc, documento, nombre, apellido, telefono, email)
            
        elif opcion == "2":
            clientes_gestor.listar_clientes(lista_clientes)
            
        elif opcion == "3":
            # Actualizado para buscar tanto DNI como RUC
            doc_buscar = input("Documento (DNI/RUC) a buscar: ").strip()
            encontrado = clientes_gestor.buscar_cliente(lista_clientes, doc_buscar)
            print(encontrado if encontrado else "Cliente no encontrado.")
        elif opcion == "4":
            clientes_almacenamiento.guardar_clientes(lista_clientes)
            print("Datos guardados. ¡Hasta luego!")

        else:
            print(" Opción no válida, intenta de nuevo.")


if __name__ == "__main__":
    main()
