"""Almacén en PostgreSQL.

Los arreglos paralelos siguen siendo la memoria de trabajo; PostgreSQL es donde los datos
sobreviven. Cada vez que el sistema confirma un cambio, guardar() sincroniza las cuatro
tablas en UNA sola transacción (una venta y su descuento de stock se guardan juntos o
no se guarda nada). Al arrancar, leer() trae las tablas y crea el esquema si no existe.

Requiere:  pip install psycopg2-binary   y un servidor PostgreSQL con la base creada.
La contraseña se toma de la variable de entorno PGPASSWORD (nunca del código).
"""
import os
from decimal import Decimal

from almacenamiento import tablas as puente
from config import settings
from exceptions.errores import ErrorPersistencia

_RUTA_ESQUEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "esquema_bd.sql")

_SELECT = {
    "empleados": "SELECT usuario, password_hash, sal, nombres, rol FROM empleados ORDER BY usuario",
    "clientes": "SELECT documento, nombre, telefono FROM clientes ORDER BY documento",
    "productos": "SELECT codigo, nombre, precio, stock FROM productos ORDER BY codigo",
    "ventas": ("SELECT codigo, documento_cliente, codigo_producto, cantidad, precio_unitario, "
               "total, usuario_vendedor FROM ventas ORDER BY fecha_venta, codigo"),
}

_UPSERT = {
    "empleados": (
        "INSERT INTO empleados (usuario, password_hash, sal, nombres, rol) "
        "VALUES (%s, %s, %s, %s, %s) ON CONFLICT (usuario) DO UPDATE SET "
        "password_hash = EXCLUDED.password_hash, sal = EXCLUDED.sal, "
        "nombres = EXCLUDED.nombres, rol = EXCLUDED.rol"),
    "clientes": (
        "INSERT INTO clientes (documento, nombre, telefono) VALUES (%s, %s, %s) "
        "ON CONFLICT (documento) DO UPDATE SET "
        "nombre = EXCLUDED.nombre, telefono = EXCLUDED.telefono"),
    "productos": (
        "INSERT INTO productos (codigo, nombre, precio, stock) VALUES (%s, %s, %s, %s) "
        "ON CONFLICT (codigo) DO UPDATE SET "
        "nombre = EXCLUDED.nombre, precio = EXCLUDED.precio, stock = EXCLUDED.stock"),
    "ventas": (
        "INSERT INTO ventas (codigo, documento_cliente, codigo_producto, cantidad, "
        "precio_unitario, total, usuario_vendedor) VALUES (%s, %s, %s, %s, %s, %s, %s) "
        "ON CONFLICT (codigo) DO UPDATE SET "
        "documento_cliente = EXCLUDED.documento_cliente, "
        "codigo_producto = EXCLUDED.codigo_producto, cantidad = EXCLUDED.cantidad, "
        "precio_unitario = EXCLUDED.precio_unitario, total = EXCLUDED.total, "
        "usuario_vendedor = EXCLUDED.usuario_vendedor"),
}

_BORRAR_VENTAS_AUSENTES = "DELETE FROM ventas WHERE NOT (codigo = ANY(%s::varchar[]))"


class AlmacenPostgres:
    nombre = "postgresql"

    def __init__(self, parametros=None, conectar=None):
        """parametros: dict de psycopg2.connect. conectar: función que devuelve una conexión
        (se reemplaza en las pruebas por una conexión falsa)."""
        self.parametros = parametros or {
            "host": settings.PG_HOST, "port": settings.PG_PUERTO, "dbname": settings.PG_BASE,
            "user": settings.PG_USUARIO, "password": settings.PG_CLAVE,
        }
        self._conectar = conectar or self._conectar_real

    def descripcion(self):
        p = self.parametros
        return f"PostgreSQL {p['dbname']} en {p['host']}:{p['port']}"

    def _conectar_real(self):
        try:
            import psycopg2
        except ImportError:
            raise ErrorPersistencia("falta instalar psycopg2 (pip install psycopg2-binary).")
        try:
            return psycopg2.connect(connect_timeout=5, **self.parametros)
        except (psycopg2.Error, UnicodeDecodeError) as error:
            # UnicodeDecodeError: en Windows en español el servidor puede responder en un
            # idioma que psycopg2 no decodifica; el motivo real suele ser clave o base incorrecta.
            raise ErrorPersistencia(
                f"no se pudo conectar a PostgreSQL ({self.descripcion()}): {error}. "
                "Revise que el servicio esté activo, que la base exista y la variable PGPASSWORD.")

    def _en_transaccion(self, trabajo):
        """Abre conexión, ejecuta trabajo(cursor) en una transacción y siempre cierra."""
        conexion = self._conectar()
        try:
            with conexion:                       # COMMIT si todo salió bien, ROLLBACK si falla
                with conexion.cursor() as cursor:
                    return trabajo(cursor)
        except ErrorPersistencia:
            raise
        except Exception as error:               # errores de psycopg2 (SQL, restricciones...)
            raise ErrorPersistencia(f"error de base de datos: {str(error).strip()}.")
        finally:
            conexion.close()

    @staticmethod
    def _crear_esquema(cursor):
        with open(_RUTA_ESQUEMA, "r", encoding="utf-8") as archivo:
            cursor.execute(archivo.read())

    @staticmethod
    def _a_python(fila):
        """NUMERIC llega como Decimal; el resto del sistema trabaja con float."""
        return tuple(float(v) if isinstance(v, Decimal) else v for v in fila)

    def leer(self):
        def trabajo(cursor):
            self._crear_esquema(cursor)
            datos = {}
            for tabla in puente.TABLAS:
                cursor.execute(_SELECT[tabla])
                datos[tabla] = [self._a_python(fila) for fila in cursor.fetchall()]
            return datos
        return self._en_transaccion(trabajo)

    def guardar(self, datos):
        def trabajo(cursor):
            self._crear_esquema(cursor)
            # 1) borrar ventas eliminadas  2) maestros  3) ventas (que referencian a los maestros)
            cursor.execute(_BORRAR_VENTAS_AUSENTES, ([fila[0] for fila in datos["ventas"]],))
            for tabla in puente.TABLAS:
                if datos[tabla]:
                    cursor.executemany(_UPSERT[tabla], datos[tabla])
        self._en_transaccion(trabajo)
