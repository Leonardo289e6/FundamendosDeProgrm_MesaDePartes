"""Vista de consola: solo muestra información y pide texto. No aplica reglas."""


def pedir(mensaje):
    return input(mensaje)


def mostrar_mensaje(texto):
    print(texto)


def mostrar_error(texto):
    print(f"  Error: {texto}")


def mostrar_menu():
    print("\n===== MAQUINARIAS NARVÁEZ S.A.C. - CONTROL DE VENTAS =====")
    print("1. Registrar venta   2. Buscar por código")
    print("3. Ordenar por código   4. Listar ventas   0. Salir")


def mostrar_venta(venta):
    codigo, documento, cliente, maquina, cantidad, _precio, total = venta
    print(f"{codigo:<8}{documento:<13}{cliente:<26}"
          f"{maquina:<20}{cantidad:>4}  S/ {total:>9.2f}")


def mostrar_listado(ventas, suma):
    if len(ventas) == 0:
        print("No hay ventas registradas.")
        return
    print(f"{'CÓDIGO':<8}{'DOCUMENTO':<13}{'CLIENTE':<26}"
          f"{'MAQUINARIA':<20}{'CANT':>4}  {'TOTAL':>12}")
    for venta in ventas:
        mostrar_venta(venta)
    print(f"Ventas registradas: {len(ventas)} | Monto acumulado: S/ {suma:.2f}")
