"""Pruebas automáticas. Ejecutar desde la carpeta src:  python -m unittest discover -s tests -v"""
import importlib
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from exceptions.errores import (ClienteDuplicadoError, ClienteNoEncontradoError,
                                CredencialesInvalidasError, PermisoDenegadoError,
                                SesionRequeridaError, StockInsuficienteError,
                                ValorInvalidoError, VentaNoEncontradaError)
from models import cliente, empleado, producto, venta
from services import auth_service as auth
from services import cliente_service as clientes
from services import producto_service as productos
from services import validacion_service as val
from services import venta_service as ventas
from utils import cadenas


class Base(unittest.TestCase):
    """Cada prueba parte de arreglos vacíos y, si se pide, con sesión de administrador."""

    def setUp(self):
        for modelo in (empleado, cliente, producto, venta):
            importlib.reload(modelo)          # vuelve a declarar los arreglos vacíos
        auth.cerrar_sesion()
        auth.crear_primer_administrador("admin", "admin123", "ADMIN")
        auth.iniciar_sesion("admin", "admin123")
        auth.registrar_empleado("vend", "venta123", "VENDEDOR UNO", "Vendedor")
        clientes.registrar_cliente("47581234", "JUAN PEREZ", "987654321")
        clientes.registrar_cliente("20123456789", "CONSTRUCTORA NARVAEZ SAC", "944111222")
        productos.registrar_producto("EXC-01", "EXCAVADORA", 100000.0, 5)
        productos.registrar_producto("CARG-01", "CARGADOR FRONTAL", 50000.0, 4)

    def stock(self, codigo):
        return productos.buscar_producto(codigo)[3]


class TestAutenticacion(Base):
    def test_login_correcto_guarda_sesion(self):
        auth.cerrar_sesion()
        auth.iniciar_sesion("vend", "venta123")
        self.assertEqual(auth.empleado_actual()[0], "vend")
        self.assertFalse(auth.es_admin())

    def test_login_incorrecto_mismo_mensaje(self):
        auth.cerrar_sesion()
        with self.assertRaises(CredencialesInvalidasError) as c1:
            auth.iniciar_sesion("vend", "mala")
        with self.assertRaises(CredencialesInvalidasError) as c2:
            auth.iniciar_sesion("noexiste", "venta123")
        self.assertEqual(str(c1.exception), str(c2.exception))

    def test_la_clave_no_se_guarda_en_texto_plano(self):
        self.assertNotIn("admin123", empleado.hashes)
        self.assertEqual(len(empleado.hashes[0]), 64)
        self.assertNotEqual(empleado.sales[0], empleado.sales[1])   # sal distinta por usuario

    def test_primer_administrador_solo_si_no_hay_empleados(self):
        with self.assertRaises(PermisoDenegadoError):
            auth.crear_primer_administrador("otro", "clave123", "OTRO")

    def test_vendedor_no_registra_empleados(self):
        auth.cerrar_sesion()
        auth.iniciar_sesion("vend", "venta123")
        with self.assertRaises(PermisoDenegadoError):
            auth.registrar_empleado("nuevo", "clave123", "NUEVO", "Vendedor")

    def test_sin_sesion_no_se_puede_vender(self):
        auth.cerrar_sesion()
        with self.assertRaises(SesionRequeridaError):
            ventas.registrar_venta("V001", "47581234", "EXC-01", 1)


class TestClientes(Base):
    def test_cliente_duplicado(self):
        with self.assertRaises(ClienteDuplicadoError):
            clientes.registrar_cliente("47581234", "OTRO", "987654321")

    def test_cliente_inexistente(self):
        with self.assertRaises(ClienteNoEncontradoError):
            clientes.obtener_cliente("99999999")

    def test_modificar_cliente(self):
        clientes.modificar_cliente("47581234", "JUAN PEREZ DIAZ", "911222333")
        self.assertEqual(clientes.buscar_cliente("47581234")[1:], ("JUAN PEREZ DIAZ", "911222333"))

    def test_venta_a_cliente_no_registrado_se_rechaza(self):
        with self.assertRaises(ClienteNoEncontradoError):
            ventas.registrar_venta("V001", "99999999", "EXC-01", 1)
        self.assertEqual(self.stock("EXC-01"), 5)       # no se tocó el stock


class TestInventario(Base):
    def test_venta_descuenta_stock_y_guarda_vendedor(self):
        total = ventas.registrar_venta("V001", "47581234", "EXC-01", 2)
        self.assertAlmostEqual(total, 2 * 100000.0 * 1.18)
        self.assertEqual(self.stock("EXC-01"), 3)
        self.assertEqual(ventas.buscar_venta("V001")[7], "admin")

    def test_stock_insuficiente_no_registra_nada(self):
        with self.assertRaises(StockInsuficienteError):
            ventas.registrar_venta("V001", "47581234", "EXC-01", 6)
        self.assertEqual(self.stock("EXC-01"), 5)
        self.assertIsNone(ventas.buscar_venta("V001"))

    def test_eliminar_devuelve_stock(self):
        ventas.registrar_venta("V001", "47581234", "EXC-01", 2)
        ventas.eliminar_venta("V001")
        self.assertEqual(self.stock("EXC-01"), 5)

    def test_vendedor_no_puede_eliminar(self):
        ventas.registrar_venta("V001", "47581234", "EXC-01", 2)
        auth.cerrar_sesion()
        auth.iniciar_sesion("vend", "venta123")
        with self.assertRaises(PermisoDenegadoError):
            ventas.eliminar_venta("V001")
        self.assertEqual(self.stock("EXC-01"), 3)

    def test_modificar_cantidad_ajusta_stock(self):
        ventas.registrar_venta("V001", "47581234", "EXC-01", 2)
        ventas.modificar_venta("V001", "47581234", None, 4)
        self.assertEqual(self.stock("EXC-01"), 1)

    def test_modificar_producto_devuelve_uno_y_descuenta_otro(self):
        ventas.registrar_venta("V001", "47581234", "EXC-01", 2)
        total = ventas.modificar_venta("V001", "47581234", "CARG-01", 3)
        self.assertEqual(self.stock("EXC-01"), 5)
        self.assertEqual(self.stock("CARG-01"), 1)
        self.assertAlmostEqual(total, 3 * 50000.0 * 1.18)   # toma el precio del nuevo producto

    def test_modificar_con_stock_insuficiente_deja_todo_igual(self):
        ventas.registrar_venta("V001", "47581234", "EXC-01", 2)
        with self.assertRaises(StockInsuficienteError):
            ventas.modificar_venta("V001", "47581234", None, 9)
        self.assertEqual(self.stock("EXC-01"), 3)
        self.assertEqual(ventas.buscar_venta("V001")[4], 2)

    def test_reponer_solo_administrador(self):
        self.assertEqual(productos.reponer_stock("EXC-01", 5), 10)
        auth.cerrar_sesion()
        auth.iniciar_sesion("vend", "venta123")
        with self.assertRaises(PermisoDenegadoError):
            productos.reponer_stock("EXC-01", 1)

    def test_marca_de_stock_bajo(self):
        ventas.registrar_venta("V001", "47581234", "EXC-01", 4)    # quedan 1
        bajo = {p[0]: p[4] for p in productos.listar_productos()}
        self.assertTrue(bajo["EXC-01"])
        self.assertFalse(bajo["CARG-01"])


class TestVentasEstructuras(Base):
    def cargar_tres(self):
        ventas.registrar_venta("V003", "47581234", "CARG-01", 1)        # 59 000
        ventas.registrar_venta("V001", "20123456789", "EXC-01", 2)      # 236 000
        ventas.registrar_venta("V002", "47581234", "EXC-01", 1)         # 118 000

    def codigos(self):
        return [v[0] for v in ventas.listar_ventas()[0]]

    def test_ordenar_burbuja_por_codigo(self):
        self.cargar_tres()
        ventas.ordenar_ventas(1)
        self.assertEqual(self.codigos(), ["V001", "V002", "V003"])

    def test_ordenar_seleccion_por_total_descendente(self):
        self.cargar_tres()
        ventas.ordenar_ventas(2)
        self.assertEqual(self.codigos(), ["V001", "V002", "V003"])
        totales = [v[6] for v in ventas.listar_ventas()[0]]
        self.assertEqual(totales, sorted(totales, reverse=True))

    def test_ordenar_mantiene_alineados_los_arreglos(self):
        self.cargar_tres()
        ventas.ordenar_ventas(1)
        v1 = ventas.buscar_venta("V001")
        self.assertEqual((v1[1], v1[3], v1[4]), ("20123456789", "EXCAVADORA", 2))

    def test_eliminar_desplaza_y_limpia_la_ultima_posicion(self):
        self.cargar_tres()
        ventas.eliminar_venta("V003")
        self.assertEqual(self.codigos(), ["V001", "V002"])
        self.assertEqual(venta.codigos[2], "")
        self.assertEqual(venta.totales[2], 0.0)

    def test_eliminar_inexistente(self):
        with self.assertRaises(VentaNoEncontradaError):
            ventas.eliminar_venta("NOEXISTE")

    def test_busqueda_textual_ignora_tildes_y_mayusculas(self):
        self.cargar_tres()
        self.assertEqual(len(ventas.buscar_por_texto("narváez")), 1)
        self.assertEqual(len(ventas.buscar_por_texto("EXCA")), 2)
        self.assertEqual(ventas.buscar_por_texto("zzz"), [])

    def test_matriz_resumen(self):
        self.cargar_tres()
        maquinas, matriz = ventas.resumen_unidades()
        self.assertEqual(maquinas, ["CARGADOR FRONTAL", "EXCAVADORA"])
        self.assertEqual(matriz[0], [1, 1])    # DNI
        self.assertEqual(matriz[1], [0, 2])    # RUC


class TestCadenasYValidacion(unittest.TestCase):
    def test_normalizar(self):
        self.assertEqual(cadenas.normalizar_codigo(" v 001 "), "V001")
        self.assertEqual(cadenas.normalizar_nombre("  juan   pérez "), "JUAN PÉREZ")

    def test_enmascarar_y_abreviar(self):
        self.assertEqual(cadenas.enmascarar_documento("47581234"), "******34")
        self.assertEqual(cadenas.abreviar("CONSTRUCTORA NARVAEZ SAC", 10), "CONSTRU...")

    def test_separar_registro(self):
        self.assertEqual(cadenas.separar_registro("V1; 4758 ;EXC;2", ";", 4), ["V1", "4758", "EXC", "2"])
        with self.assertRaises(ValorInvalidoError):
            cadenas.separar_registro("V1;4758", ";", 4)

    def test_validaciones(self):
        self.assertEqual(val.validar_documento("20123456789"), "20123456789")
        for malo in ("123", "30123456789", "abcdefgh"):
            with self.assertRaises(Exception):
                val.validar_documento(malo)
        self.assertEqual(val.validar_telefono("987654321"), "987654321")
        with self.assertRaises(ValorInvalidoError):
            val.validar_telefono("887654321")
        with self.assertRaises(ValorInvalidoError):
            val.validar_clave("123")
        self.assertEqual(val.validar_usuario(" Admin_1 "), "admin_1")
        with self.assertRaises(ValorInvalidoError):
            val.validar_usuario("a b")


if __name__ == "__main__":
    unittest.main()
