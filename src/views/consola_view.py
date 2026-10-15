"""Vista de consola: solo muestra información y pide texto. No aplica reglas."""
import getpass

from utils import cadenas


def pedir(mensaje):
    return input(mensaje)


def pedir_clave(mensaje):
    """Pide la contraseña sin mostrarla en pantalla."""
    return getpass.getpass(mensaje)


def mostrar_mensaje(texto):
    print(texto)


def mostrar_error(texto):
    print(f"  Error: {texto}")


def mostrar_menu(titulo, opciones, texto_cero="Volver"):
    """opciones: lista de (número, texto). La opción 0 siempre es salir del menú."""
    print(f"\n===== {titulo} =====")
    for numero, texto in opciones:
        print(f"{numero}. {texto}")
    print(f"0. {texto_cero}")


def mostrar_sesion(empleado):
    usuario, nombre, rol = empleado
    print(f"\nSesión iniciada: {nombre} ({rol})")


# ---------- ventas ----------
def mostrar_encabezado():
    print(f"{'CÓDIGO':<8}{'DOCUMENTO':<13}{'CLIENTE':<26}"
          f"{'MAQUINARIA':<20}{'CANT':>4}  {'TOTAL':>12}  VENDEDOR")


def mostrar_venta(venta):
    codigo, documento, cliente, maquina, cantidad, _precio, total, vendedor = venta
    documento = cadenas.enmascarar_documento(documento)
    cliente = cadenas.abreviar(cliente, 25)
    maquina = cadenas.abreviar(maquina, 19)
    print(f"{codigo:<8}{documento:<13}{cliente:<26}"
          f"{maquina:<20}{cantidad:>4}  S/ {total:>9.2f}  {vendedor}")


def mostrar_listado(ventas, suma):
    if len(ventas) == 0:
        print("No hay ventas registradas.")
        return
    mostrar_encabezado()
    for venta in ventas:
        mostrar_venta(venta)
    print(f"Ventas registradas: {len(ventas)} | Monto acumulado: S/ {suma:.2f}")


def mostrar_coincidencias(ventas):
    mostrar_encabezado()
    for venta in ventas:
        mostrar_venta(venta)
    print(f"Coincidencias: {len(ventas)}")


def mostrar_resumen(maquinas, matriz):
    """Imprime la matriz 2D: filas = tipo de cliente, columnas = maquinaria."""
    etiquetas = ("Persona (DNI)", "Empresa (RUC)")
    print(f"{'':<15}" + "".join(f"{cadenas.abreviar(mq, 13):>14}" for mq in maquinas))
    for fila in range(2):
        print(f"{etiquetas[fila]:<15}" + "".join(f"{u:>14}" for u in matriz[fila]))


# ---------- clientes ----------
def mostrar_cliente(cliente):
    documento, nombre, telefono = cliente
    print(f"{cadenas.tipo_documento(documento):<5}{cadenas.enmascarar_documento(documento):<13}"
          f"{cadenas.abreviar(nombre, 31):<32}{telefono}")


def mostrar_clientes(clientes):
    if len(clientes) == 0:
        print("No hay clientes registrados.")
        return
    print(f"{'TIPO':<5}{'DOCUMENTO':<13}{'NOMBRE / RAZÓN SOCIAL':<32}TELÉFONO")
    for cliente in clientes:
        mostrar_cliente(cliente)
    print(f"Clientes registrados: {len(clientes)}")


# ---------- inventario ----------
def mostrar_producto(producto):
    codigo, nombre, precio, stock = producto[:4]
    aviso = "  <- STOCK BAJO" if len(producto) > 4 and producto[4] else ""
    print(f"{codigo:<12}{cadenas.abreviar(nombre, 25):<26}S/ {precio:>10.2f}{stock:>8}{aviso}")


def mostrar_productos(productos):
    if len(productos) == 0:
        print("No hay productos registrados.")
        return
    print(f"{'CÓDIGO':<12}{'MAQUINARIA':<26}{'PRECIO (sin IGV)':>13}{'STOCK':>8}")
    for producto in productos:
        mostrar_producto(producto)


# ---------- empleados ----------
def mostrar_empleados(empleados):
    print(f"{'USUARIO':<22}{'NOMBRE':<32}ROL")
    for usuario, nombre, rol in empleados:
        print(f"{usuario:<22}{cadenas.abreviar(nombre, 31):<32}{rol}")
