"""Pruebas de persistencia: archivos, validación de integridad, PostgreSQL (conexión simulada)
y gestor. Ejecutar desde src:  python -m unittest discover -s tests -v"""
import importlib
import os
import shutil
import sys
import tempfile
import unittest
from decimal import Decimal
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from almacenamiento import gestor, integridad
from almacenamiento import tablas as puente
from almacenamiento.archivos import AlmacenArchivos
from almacenamiento.postgres import AlmacenPostgres
from exceptions.errores import DatosCorruptosError, ErrorPersistencia
from models import cliente, empleado, producto, venta
from services import auth_service as auth
from services import cliente_service as clientes
from services import producto_service as productos
from services import venta_service as ventas


def reiniciar_arreglos():
    for modelo in (empleado, cliente, producto, venta):
        importlib.reload(modelo)
    auth.cerrar_sesion()


def sembrar():
    """Un administrador, dos clientes, dos productos y una venta."""
    auth.crear_primer_administrador("admin", "admin123", "ADMIN")
    auth.iniciar_sesion("admin", "admin123")
    clientes.registrar_cliente("47581234", "JUAN; PEREZ", "987654321")   # ';' dentro del nombre
    clientes.registrar_cliente("20123456789", "CONSTRUCTORA NARVAEZ SAC", "944111222")
    productos.registrar_producto("EXC-01", "EXCAVADORA", 120000.0, 5)
    productos.registrar_producto("CARG-01", "CARGADOR FRONTAL", 85000.5, 4)
    ventas.registrar_venta("V001", "47581234", "EXC-01", 2)


class BaseArchivos(unittest.TestCase):
    def setUp(self):
        reiniciar_arreglos()
        self.carpeta = tempfile.mkdtemp()
        gestor.configurar(almacen=AlmacenArchivos(self.carpeta))
        self.addCleanup(shutil.rmtree, self.carpeta, True)
        self.addCleanup(gestor.configurar, "memoria")


class TestArchivos(BaseArchivos):
    def test_cada_cambio_se_guarda_y_se_recupera_al_reiniciar(self):
        sembrar()
        antes = puente.extraer()
        reiniciar_arreglos()                      # simula cerrar y volver a abrir el programa
        self.assertEqual(clientes.listar_clientes(), [])
        gestor.cargar()
        self.assertEqual(puente.extraer(), antes)
        self.assertEqual(productos.buscar_producto("EXC-01")[3], 3)     # el stock descontado persiste
        self.assertEqual(clientes.buscar_cliente("47581234")[1], "JUAN; PEREZ")

    def test_formato_de_texto_plano_legible(self):
        sembrar()
        with open(os.path.join(self.carpeta, "productos.txt"), encoding="utf-8") as f:
            lineas = f.read().splitlines()
        self.assertEqual(lineas[0], "codigo;nombre;precio;stock")
        self.assertEqual(lineas[1], "EXC-01;EXCAVADORA;120000.00;3")

    def test_la_clave_se_conserva_y_el_login_funciona_tras_reiniciar(self):
        sembrar()
        reiniciar_arreglos()
        gestor.cargar()
        auth.iniciar_sesion("admin", "admin123")
        self.assertTrue(auth.es_admin())

    def test_sin_archivos_es_primer_arranque(self):
        gestor.cargar()
        self.assertFalse(auth.hay_empleados())

    def test_no_quedan_temporales(self):
        sembrar()
        self.assertEqual([n for n in os.listdir(self.carpeta) if n.endswith(".tmp")], [])

    def test_eliminar_venta_y_modificar_persisten(self):
        sembrar()
        ventas.modificar_venta("V001", "47581234", None, 4)
        reiniciar_arreglos()
        gestor.cargar()
        self.assertEqual(ventas.buscar_venta("V001")[4], 4)
        auth.iniciar_sesion("admin", "admin123")
        ventas.eliminar_venta("V001")
        reiniciar_arreglos()
        gestor.cargar()
        self.assertIsNone(ventas.buscar_venta("V001"))
        self.assertEqual(productos.buscar_producto("EXC-01")[3], 5)

    def _corromper(self, nombre, reemplazos):
        ruta = os.path.join(self.carpeta, nombre)
        with open(ruta, encoding="utf-8") as f:
            texto = f.read()
        for viejo, nuevo in reemplazos:
            self.assertIn(viejo, texto)
            texto = texto.replace(viejo, nuevo)
        with open(ruta, "w", encoding="utf-8", newline="") as f:
            f.write(texto)

    def test_detecta_numero_invalido(self):
        sembrar()
        self._corromper("productos.txt", [("120000.00", "mucho")])
        reiniciar_arreglos()
        with self.assertRaises(DatosCorruptosError) as c:
            gestor.cargar()
        self.assertIn("productos.txt", str(c.exception))
        self.assertIn("línea 2", str(c.exception))
        self.assertFalse(auth.hay_empleados())     # no se cargó nada a medias

    def test_detecta_campos_faltantes(self):
        sembrar()
        self._corromper("clientes.txt", [("987654321", "")])    # teléfono vacío
        reiniciar_arreglos()
        with self.assertRaises(DatosCorruptosError):
            gestor.cargar()

    def test_detecta_encabezado_alterado(self):
        sembrar()
        self._corromper("clientes.txt", [("documento;", "dni;")])
        reiniciar_arreglos()
        with self.assertRaises(DatosCorruptosError):
            gestor.cargar()

    def test_detecta_venta_con_cliente_inexistente(self):
        sembrar()
        self._corromper("ventas.txt", [("V001;47581234", "V001;99999999")])
        reiniciar_arreglos()
        with self.assertRaises(DatosCorruptosError) as c:
            gestor.cargar()
        self.assertIn("no existe", str(c.exception))

    def test_detecta_clave_repetida(self):
        sembrar()
        self._corromper("productos.txt", [("CARG-01", "EXC-01")])
        reiniciar_arreglos()
        with self.assertRaises(DatosCorruptosError) as c:
            gestor.cargar()
        self.assertIn("repetida", str(c.exception))

    def test_detecta_stock_negativo_y_precio_infinito(self):
        sembrar()
        self._corromper("productos.txt", [(";3\n", ";-1\n")])
        reiniciar_arreglos()
        with self.assertRaises(DatosCorruptosError):
            gestor.cargar()
        self._corromper("productos.txt", [(";-1\n", ";3\n"), ("120000.00", "inf")])
        reiniciar_arreglos()
        with self.assertRaises(DatosCorruptosError):
            gestor.cargar()

    def test_detecta_mas_registros_que_la_capacidad(self):
        filas = [(f"C{i}", "X", 10.0, 1) for i in range(40)]
        datos = {"empleados": [], "clientes": [], "productos": filas, "ventas": []}
        with self.assertRaises(DatosCorruptosError):
            integridad.validar_tablas(datos)

    def test_error_al_guardar_revierte_la_memoria_y_no_deja_temporales(self):
        sembrar()
        with mock.patch("almacenamiento.archivos.os.replace", side_effect=OSError("disco lleno")):
            with self.assertRaises(ErrorPersistencia) as c:
                clientes.registrar_cliente("11111111", "NUEVO", "911111111")
        self.assertIn("disco lleno", str(c.exception))
        self.assertIn("NO se guardó", str(c.exception))
        self.assertIsNone(clientes.buscar_cliente("11111111"))        # la memoria se deshizo
        self.assertEqual(len(clientes.listar_clientes()), 2)
        self.assertEqual([n for n in os.listdir(self.carpeta) if n.endswith(".tmp")], [])
        reiniciar_arreglos()
        gestor.cargar()                                                # lo guardado sigue intacto
        self.assertIsNone(clientes.buscar_cliente("11111111"))
        self.assertEqual(len(clientes.listar_clientes()), 2)


class TestGestor(unittest.TestCase):
    def tearDown(self):
        gestor.configurar("memoria")

    def test_modo_memoria_por_defecto_no_escribe(self):
        gestor.configurar("memoria")
        self.assertEqual(gestor.modo_activo(), "memoria")
        gestor.confirmar()      # no hace nada ni falla

    def test_modo_desconocido(self):
        with self.assertRaises(Exception):
            gestor.configurar("nube")

    def test_si_guardar_falla_se_restaura_lo_ultimo_guardado(self):
        class AlmacenFalla:
            nombre = "falla"
            def __init__(self): self.guardado = {t: [] for t in puente.TABLAS}; self.falla = False
            def descripcion(self): return "falso"
            def leer(self): return {t: list(f) for t, f in self.guardado.items()}
            def guardar(self, datos):
                if self.falla:
                    raise ErrorPersistencia("disco lleno.")
                self.guardado = {t: list(f) for t, f in datos.items()}
        almacen = AlmacenFalla()
        reiniciar_arreglos()
        gestor.configurar(almacen=almacen)
        auth.crear_primer_administrador("admin", "admin123", "ADMIN")
        auth.iniciar_sesion("admin", "admin123")
        clientes.registrar_cliente("47581234", "JUAN", "987654321")
        almacen.falla = True
        with self.assertRaises(ErrorPersistencia) as c:
            clientes.registrar_cliente("20123456789", "EMPRESA", "944111222")
        self.assertIn("NO se guardó", str(c.exception))
        self.assertEqual(len(clientes.listar_clientes()), 1)      # el cliente nuevo se deshizo


# ---------------- PostgreSQL con una conexión simulada ----------------
class BaseDatosFalsa:
    def __init__(self):
        self.sentencias = []
        self.tablas = {"empleados": [], "clientes": [], "productos": [], "ventas": []}
        self.commits = self.rollbacks = self.cerradas = 0
        self.fallar_en = None


class _Cursor:
    def __init__(self, bd):
        self.bd = bd
        self.ultima = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=None):
        self.bd.sentencias.append((sql, params))
        if sql.lstrip().startswith("SELECT"):
            self.ultima = sql.split(" FROM ")[1].split()[0]

    def executemany(self, sql, filas):
        if self.bd.fallar_en and self.bd.fallar_en in sql:
            raise RuntimeError("violación de restricción")
        self.bd.sentencias.append((sql, list(filas)))

    def fetchall(self):
        return self.bd.tablas[self.ultima]


class _Conexion:
    def __init__(self, bd):
        self.bd = bd

    def __enter__(self):
        return self

    def __exit__(self, tipo, *args):
        if tipo is None:
            self.bd.commits += 1
        else:
            self.bd.rollbacks += 1
        return False

    def cursor(self):
        return _Cursor(self.bd)

    def close(self):
        self.bd.cerradas += 1


class TestPostgres(unittest.TestCase):
    def setUp(self):
        reiniciar_arreglos()
        self.bd = BaseDatosFalsa()
        self.almacen = AlmacenPostgres(
            parametros={"host": "h", "port": 5432, "dbname": "d", "user": "u", "password": ""},
            conectar=lambda: _Conexion(self.bd))
        gestor.configurar(almacen=self.almacen)
        self.addCleanup(gestor.configurar, "memoria")

    def test_guardar_usa_una_sola_transaccion_y_el_orden_correcto(self):
        sembrar()
        # sembrar() confirma 6 veces (admin, 2 clientes, 2 productos, venta): 6 transacciones
        self.assertEqual(self.bd.commits, 6)
        self.assertEqual(self.bd.rollbacks, 0)
        self.assertEqual(self.bd.cerradas, 6)           # la conexión siempre se cierra
        # La última transacción: primero borra ventas, luego maestros y al final las ventas
        # (que referencian a clientes, productos y empleados).
        escritura = [s[0] for s in self.bd.sentencias if s[0].startswith(("DELETE", "INSERT"))][-5:]
        self.assertTrue(escritura[0].startswith("DELETE FROM ventas"))
        self.assertEqual([e.split()[2] for e in escritura[1:]],
                         ["empleados", "clientes", "productos", "ventas"])

    def test_borra_las_ventas_que_ya_no_existen(self):
        sembrar()
        borrado = [s for s in self.bd.sentencias if s[0].startswith("DELETE")][-1]
        self.assertEqual(borrado[1], (["V001"],))

    def test_el_esquema_se_crea_al_leer_y_guardar(self):
        self.almacen.leer()
        self.assertIn("CREATE TABLE IF NOT EXISTS ventas", self.bd.sentencias[0][0])

    def test_leer_convierte_decimal_a_float_y_carga(self):
        self.bd.tablas["empleados"] = []
        sembrar()
        datos = puente.extraer()
        self.bd.tablas = {t: [tuple(Decimal(str(v)) if isinstance(v, float) else v for v in fila)
                              for fila in filas] for t, filas in datos.items()}
        reiniciar_arreglos()
        gestor.cargar()
        self.assertEqual(puente.extraer(), datos)
        self.assertIsInstance(productos.buscar_producto("EXC-01")[2], float)

    def test_error_sql_hace_rollback_revierte_memoria_y_avisa(self):
        sembrar()
        self.bd.tablas = {t: list(f) for t, f in puente.extraer().items()}   # lo "guardado"
        self.bd.fallar_en = "INSERT INTO clientes"
        antes = self.bd.rollbacks
        with self.assertRaises(ErrorPersistencia) as c:
            clientes.registrar_cliente("11111111", "NUEVO", "911111111")
        self.assertIn("error de base de datos", str(c.exception))
        self.assertGreater(self.bd.rollbacks, antes)
        self.assertEqual(self.bd.cerradas, self.bd.commits + self.bd.rollbacks)
        self.assertIsNone(clientes.buscar_cliente("11111111"))              # memoria revertida

    def test_sin_psycopg2_el_mensaje_es_claro(self):
        almacen = AlmacenPostgres(parametros={"host": "h", "port": 1, "dbname": "d",
                                              "user": "u", "password": ""})
        try:
            import psycopg2  # noqa: F401
        except ImportError:
            with self.assertRaises(ErrorPersistencia) as c:
                almacen.leer()
            self.assertIn("psycopg2", str(c.exception))
        else:
            self.skipTest("psycopg2 está instalado")


if __name__ == "__main__":
    unittest.main()
