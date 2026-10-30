"""Funciones recursivas (y sus equivalentes iterativos) sobre listas. Son funciones puras.

Dos procesos del sistema, cada uno en versión iterativa y recursiva para compararlos:
  1. Reporte acumulado: sumar los totales de las ventas.
  2. Búsqueda: hallar la posición de una venta por su código.

En cada función recursiva se señalan:
  CASO BASE      : la situación más simple, se responde sin volver a llamarse.
  CASO RECURSIVO : se reduce el problema y la función se llama a sí misma.
  PARADA         : por qué la recursión siempre termina (el problema se achica en cada llamada).
"""


# ---------- 1. acumulado de totales ----------
def sumar_iterativo(valores):
    """Suma con un ciclo: memoria constante, sin riesgo de desbordamiento."""
    suma = 0.0
    for valor in valores:
        suma = suma + valor
    return suma


def sumar_recursivo(valores, n):
    """Suma los primeros n elementos de la lista.

    CASO BASE      : n <= 0  -> no hay elementos, la suma es 0.
    CASO RECURSIVO : valores[n-1] + suma de los n-1 primeros.
    PARADA         : n baja de a 1 en cada llamada, así que llega a 0.
    Profundidad: n llamadas apiladas (Python permite ~1000 por defecto).
    """
    if n <= 0:
        return 0.0
    return valores[n - 1] + sumar_recursivo(valores, n - 1)


def sumar_recursivo_dividir(valores, inicio, fin):
    """Suma valores[inicio:fin] partiendo la lista a la mitad (divide y vencerás).

    CASO BASE      : 0 elementos -> 0.0 ; 1 elemento -> ese elemento.
    CASO RECURSIVO : suma de la mitad izquierda + suma de la mitad derecha.
    PARADA         : cada mitad tiene menos elementos que el tramo original.
    Profundidad: solo log2(n) llamadas apiladas, por eso resiste listas enormes.
    """
    cantidad = fin - inicio
    if cantidad <= 0:
        return 0.0
    if cantidad == 1:
        return valores[inicio]
    medio = (inicio + fin) // 2
    return (sumar_recursivo_dividir(valores, inicio, medio)
            + sumar_recursivo_dividir(valores, medio, fin))


# ---------- 2. búsqueda ----------
def buscar_iterativo(claves, buscado):
    """Búsqueda lineal con ciclo. Devuelve la posición o -1."""
    for i in range(len(claves)):
        if claves[i] == buscado:
            return i
    return -1


def buscar_recursivo(claves, buscado, pos=0):
    """Búsqueda lineal recursiva desde la posición pos. Devuelve la posición o -1.

    CASO BASE 1    : pos >= len(claves) -> se acabó la lista, no está (-1).
    CASO BASE 2    : claves[pos] == buscado -> encontrado, devuelve pos.
    CASO RECURSIVO : buscar en el resto de la lista (pos + 1).
    PARADA         : pos aumenta de a 1 hasta encontrarlo o salirse de la lista.
    """
    if pos >= len(claves):
        return -1
    if claves[pos] == buscado:
        return pos
    return buscar_recursivo(claves, buscado, pos + 1)


