"""
modulos/clientes/gestor.py

Lógica del dominio "clientes": validaciones y operaciones sobre el
arreglo (lista) de clientes en memoria. No sabe nada de archivos ni de
menús; solo trabaja con datos.
"""

def validar_dni(dni):
    return dni.isdigit() and len(dni) == 8

def validar_ruc(ruc):
    return ruc.isdigit() and len(ruc) == 11

def validar_nombre(texto):
    return len(texto.strip()) > 0 and not any(caracter.isdigit() for caracter in texto)

def buscar_cliente(lista_clientes, documento):
    """Busca un cliente por su número de documento (DNI o RUC)."""
    for cliente in lista_clientes:
        if cliente.get("documento") == documento or cliente.get("dni") == documento:
            return cliente
    return None

def registrar_cliente(lista_clientes, tipo_doc, documento, nombre, apellido, telefono, email):
    # Validar según el tipo de documento elegido
    if tipo_doc == "DNI":
        if not validar_dni(documento):
            print(" DNI inválido. Debe tener 8 dígitos numéricos.")
            return False
    elif tipo_doc == "RUC":
        if not validar_ruc(documento):
            print(" RUC inválido. Debe tener 11 dígitos numéricos.")
            return False

    if not validar_nombre(nombre) or not validar_nombre(apellido):
        print(" Nombre o apellido inválido.")
        return False

    if buscar_cliente(lista_clientes, documento) is not None:
        print(f" Ya existe un cliente registrado con ese {tipo_doc}.")
        return False

    nuevo_cliente = {
        "tipo_doc": tipo_doc,
        "documento": documento,
        "nombre": nombre,
        "apellido": apellido,
        "telefono": telefono,
        "email": email,
    }
    lista_clientes.append(nuevo_cliente)
    print(" Cliente registrado correctamente.")
    return True

def listar_clientes(lista_clientes):
    if len(lista_clientes) == 0:
        print("No hay clientes registrados todavía.")
        return
    print("\n--- LISTA DE CLIENTES ---")
    for cliente in lista_clientes:
        # Compatibilidad con datos viejos
        t_doc = cliente.get("tipo_doc", "DNI")
        doc = cliente.get("documento", cliente.get("dni", "N/A"))
        print(f"{t_doc}: {doc} | {cliente['nombre']} {cliente['apellido']} "
              f"| Tel: {cliente['telefono']} | Email: {cliente['email']}")