"""Configuración del sistema, constantes que se pueden cambiar sin tocar la lógica."""
import os

# Capacidad de los arreglos paralelos
MAX_VENTAS = 50
MAX_CLIENTES = 50
MAX_PRODUCTOS = 30
MAX_EMPLEADOS = 10

# Reglas de negocio
IGV = 0.18                 # impuesto general a las ventas (18 %)
STOCK_MINIMO = 2           # a partir de este stock se marca "BAJO" en el inventario

# Documentos y teléfono
LONGITUD_DNI = 8
LONGITUD_RUC = 11
PREFIJOS_RUC = ("10", "20")
LONGITUD_TELEFONO = 9      # celular peruano: 9 dígitos y empieza en 9

# Seguridad
MAX_INTENTOS_LOGIN = 3
LONGITUD_MIN_CLAVE = 6
ITERACIONES_HASH = 100_000  # vueltas de PBKDF2 (más vueltas = más difícil de atacar)
ROL_ADMIN = "Administrador"
ROL_VENDEDOR = "Vendedor"
ROLES = (ROL_ADMIN, ROL_VENDEDOR)

# Registro rápido de ventas: código;documento;código de producto;cantidad
SEPARADOR_REGISTRO = ";"
CAMPOS_REGISTRO = 4


# Límites que coinciden con las columnas de la base de datos (docs: esquema_bd.sql)
LONGITUD_MAX_CODIGO = 20
LONGITUD_MAX_NOMBRE = 100

# Persistencia: dónde viven los datos entre una ejecución y otra
#   "archivos"   -> archivos de texto en CARPETA_DATOS (no necesita instalar nada)
#   "postgresql" -> base de datos PostgreSQL (necesita psycopg2 y un servidor activo)
#   "memoria"    -> no guarda nada (solo para pruebas)
# Se puede cambiar sin editar el código con la variable de entorno VENTAS_PERSISTENCIA.
PERSISTENCIA = os.environ.get("VENTAS_PERSISTENCIA", "archivos")
CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
SEPARADOR_ARCHIVO = ";"

# Conexión a PostgreSQL. La contraseña NO se escribe aquí: se lee de la variable PGPASSWORD.
PG_HOST = os.environ.get("PGHOST", "localhost")
PG_PUERTO = int(os.environ.get("PGPORT", "5432"))
PG_BASE = os.environ.get("PGDATABASE", "ventas_narvaez")
PG_USUARIO = os.environ.get("PGUSER", "postgres")
PG_CLAVE = os.environ.get("PGPASSWORD", "")

# Pruebas de rendimiento de la recursividad (tamaños de lista; el límite de Python es ~1000)
TAMANOS_PRUEBA_RECURSION = (100, 500, 2000, 10000)
