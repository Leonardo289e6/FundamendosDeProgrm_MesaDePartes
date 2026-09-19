"""
modulos/clientes/almacenamiento.py

Persistencia del dominio "clientes" en un archivo de texto plano
(separador "|"). Toda la lectura/escritura de archivos de clientes
vive aquí, separada de la lógica de negocio (gestor.py).
"""

RUTA_CLIENTES = "datos/clientes.txt"


def guardar_clientes(lista_clientes, ruta=RUTA_CLIENTES):
    """Escribe todos los clientes en el archivo de texto (sobrescribe)."""
    with open(ruta, "w", encoding="utf-8") as archivo:
        for cliente in lista_clientes:
            linea = f"{cliente['dni']}|{cliente['nombre']}|{cliente['apellido']}|" \
                    f"{cliente['telefono']}|{cliente['email']}\n"
            archivo.write(linea)


def cargar_clientes(ruta=RUTA_CLIENTES):
    """Lee el archivo de clientes y reconstruye la lista de diccionarios."""
    lista_clientes = []
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if linea == "":
                    continue
                dni, nombre, apellido, telefono, email = linea.split("|")
                lista_clientes.append({
                    "dni": dni,
                    "nombre": nombre,
                    "apellido": apellido,
                    "telefono": telefono,
                    "email": email,
                })
    except FileNotFoundError:
        pass  # Si el archivo no existe todavía, se empieza con lista vacía
    return lista_clientes
