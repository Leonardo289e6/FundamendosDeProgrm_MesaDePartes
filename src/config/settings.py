"""Configuración del sistema, constantes que se pueden cambiar sin tocar la lógica."""

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

# Datos de ejemplo mientras no exista persistencia (se desactiva en la versión final)
CARGAR_DATOS_DEMO = True
