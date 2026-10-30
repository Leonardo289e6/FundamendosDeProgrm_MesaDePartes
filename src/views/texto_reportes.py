"""Textos de los reportes de recursividad. Devuelven cadenas: los usan la consola y la GUI."""

EXPLICACION = """\
RECURSIVIDAD EN EL SISTEMA
Una función recursiva se llama a sí misma sobre un problema más pequeño.

1) SUMA RECURSIVA de los totales de ventas      utils/recursividad.py: sumar_recursivo
   Caso base      : n <= 0 (no quedan ventas)  ->  0
   Caso recursivo : total de la venta n  +  suma de las n-1 anteriores
   Parada         : n baja de a 1 en cada llamada hasta llegar a 0

2) SUMA RECURSIVA DIVIDIENDO a la mitad          utils/recursividad.py: sumar_recursivo_dividir
   Caso base      : 0 elementos -> 0  |  1 elemento -> ese valor
   Caso recursivo : suma de la mitad izquierda + suma de la mitad derecha
   Parada         : cada mitad es más corta que el tramo original (profundidad log2 n)

3) BÚSQUEDA RECURSIVA de una venta por código    utils/recursividad.py: buscar_recursivo
   Caso base 1    : se acabó la lista  ->  -1 (no existe)
   Caso base 2    : la venta de esta posición tiene el código  ->  esa posición
   Caso recursivo : buscar en la posición siguiente
   Parada         : la posición avanza de a 1 hasta encontrarla o salirse de la lista
"""

_NOMBRES = {"iterativo": "Iterativa", "recursivo": "Recursiva",
            "dividir": "Recursiva (dividir)"}


def texto_acumulado(r):
    if r["n"] == 0:
        return "No hay ventas registradas para sumar."
    lineas = [f"ACUMULADO DE VENTAS ({r['n']} ventas)",
              f"{'Versión':<22}{'Resultado (S/)':>16}{'Tiempo (µs)':>14}"]
    for clave in ("iterativo", "recursivo", "dividir"):
        lineas.append(f"{_NOMBRES[clave]:<22}{r['resultados'][clave]:>16,.2f}"
                      f"{r['tiempos'][clave]:>14.2f}")
    coinciden = max(r["resultados"].values()) - min(r["resultados"].values()) < 0.005
    lineas.append("Las tres versiones coinciden." if coinciden else "ATENCIÓN: los resultados difieren.")
    return "\n".join(lineas)


def texto_busqueda(r):
    pos = r["posiciones"]
    estado = "NO encontrada" if pos["iterativo"] == -1 else f"encontrada en la posición {pos['iterativo']}"
    lineas = [f"BÚSQUEDA DEL CÓDIGO {r['codigo']} entre {r['n']} ventas: {estado}",
              f"{'Versión':<22}{'Posición':>10}{'Tiempo (µs)':>14}"]
    for clave in ("iterativo", "recursivo"):
        lineas.append(f"{_NOMBRES[clave]:<22}{pos[clave]:>10}{r['tiempos'][clave]:>14.2f}")
    return "\n".join(lineas)


def texto_rendimiento(limite, filas):
    lineas = ["PRUEBA DE RENDIMIENTO (suma de n números, tiempo promedio en µs)",
              f"Límite de recursión de Python: {limite} llamadas apiladas",
              f"{'n':>8}{'Iterativa':>14}{'Recursiva':>16}{'Recursiva (dividir)':>22}"]
    for fila in filas:
        recursivo = ("DESBORDAMIENTO" if fila["recursivo"] is None
                     else f"{fila['recursivo']:.2f}")
        lineas.append(f"{fila['n']:>8}{fila['iterativo']:>14.2f}{recursivo:>16}"
                      f"{fila['dividir']:>22.2f}")
    lineas.append("")
    lineas.append("DESBORDAMIENTO = RecursionError: la recursión lineal necesita n llamadas "
                  "apiladas y supera el límite.")
    lineas.append("La versión que divide a la mitad solo apila ~log2(n) y no se desborda.")
    return "\n".join(lineas)
