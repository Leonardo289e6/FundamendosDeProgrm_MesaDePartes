"""Almacén en archivos de texto plano: un archivo por tabla dentro de la carpeta de datos.

Formato (UTF-8): un registro por línea, campos separados por ';'. La primera línea es el
encabezado con los nombres de las columnas. Se usa el módulo csv porque protege un ';'
que aparezca dentro de un nombre. Ejemplo de productos.txt:

    codigo;nombre;precio;stock
    EXC-01;EXCAVADORA;120000.00;5

Escritura segura: primero se escriben archivos temporales (.tmp) y solo cuando los cuatro
quedaron completos se reemplazan los originales, así un corte de luz a mitad de camino
no deja un archivo a medias.
"""
import csv
import os

from almacenamiento import tablas as puente
from config import settings
from exceptions.errores import DatosCorruptosError, ErrorPersistencia

# Columnas numéricas: el resto se guarda como texto.
_CONVERSIONES = {"precio": float, "stock": int, "cantidad": int,
                 "precio_unitario": float, "total": float}


class AlmacenArchivos:
    nombre = "archivos"

    def __init__(self, carpeta=None):
        self.carpeta = carpeta or settings.CARPETA_DATOS

    def descripcion(self):
        return f"archivos de texto en {self.carpeta}"

    def _ruta(self, tabla):
        return os.path.join(self.carpeta, tabla + ".txt")

    # ---------- escritura ----------
    def guardar(self, datos):
        """Guarda las 4 tablas. Lanza ErrorPersistencia si no se puede escribir."""
        temporales = []
        try:
            os.makedirs(self.carpeta, exist_ok=True)
            for tabla in puente.TABLAS:
                temporales.append((self._ruta(tabla) + ".tmp", self._ruta(tabla)))
                self._escribir(temporales[-1][0], tabla, datos[tabla])
            for temporal, definitivo in temporales:
                os.replace(temporal, definitivo)
        except OSError as error:
            for temporal, _ in temporales:          # no dejar basura si algo falló
                if os.path.exists(temporal):
                    os.remove(temporal)
            raise ErrorPersistencia(f"no se pudo escribir en '{self.carpeta}': {error}.")

    @staticmethod
    def _escribir(ruta, tabla, filas):
        with open(ruta, "w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo, delimiter=settings.SEPARADOR_ARCHIVO, lineterminator="\n")
            escritor.writerow(puente.COLUMNAS[tabla])
            for fila in filas:
                escritor.writerow([f"{valor:.2f}" if isinstance(valor, float) else valor
                                   for valor in fila])

    # ---------- lectura ----------
    def leer(self):
        """Lee las 4 tablas. Un archivo que no existe cuenta como tabla vacía (primer arranque)."""
        return {tabla: self._leer_tabla(tabla) for tabla in puente.TABLAS}

    def _leer_tabla(self, tabla):
        ruta = self._ruta(tabla)
        if not os.path.exists(ruta):
            return []
        columnas = puente.COLUMNAS[tabla]
        archivo_nombre = os.path.basename(ruta)
        filas = []
        try:
            with open(ruta, "r", encoding="utf-8", newline="") as archivo:
                lector = csv.reader(archivo, delimiter=settings.SEPARADOR_ARCHIVO)
                encabezado = next(lector, None)
                if encabezado != list(columnas):
                    raise DatosCorruptosError(archivo_nombre, "falta el encabezado o es distinto al esperado.")
                for numero, campos in enumerate(lector, start=2):
                    if not campos:                   # línea en blanco
                        continue
                    if len(campos) != len(columnas):
                        raise DatosCorruptosError(
                            f"{archivo_nombre}, línea {numero}",
                            f"se esperaban {len(columnas)} campos y hay {len(campos)}.")
                    filas.append(self._convertir(archivo_nombre, numero, columnas, campos))
        except (OSError, UnicodeDecodeError, csv.Error) as error:
            raise ErrorPersistencia(f"no se pudo leer '{ruta}': {error}.")
        return filas

    @staticmethod
    def _convertir(archivo_nombre, numero, columnas, campos):
        """Convierte los textos numéricos; el resto queda como texto."""
        valores = []
        for columna, campo in zip(columnas, campos):
            conversion = _CONVERSIONES.get(columna)
            if conversion is None:
                valores.append(campo)
                continue
            try:
                valores.append(conversion(campo))
            except ValueError:
                raise DatosCorruptosError(f"{archivo_nombre}, línea {numero}",
                                          f"'{columna}' no es un número válido: '{campo}'.")
        return tuple(valores)
