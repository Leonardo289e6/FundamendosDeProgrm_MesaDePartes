-- ============================================================
-- Control de Ventas - Maquinarias Narváez S.A.C.
-- Esquema de la base de datos (PostgreSQL).
-- Lo ejecuta almacenamiento/postgres.py al conectarse (es idempotente: IF NOT EXISTS).
-- Los datos de trabajo viven en arreglos paralelos (src/models/);
-- cada arreglo paralelo corresponde a una tabla de este esquema.
-- ============================================================

-- models/empleado.py  ->  empleados
CREATE TABLE IF NOT EXISTS empleados (
    usuario        VARCHAR(20)  PRIMARY KEY,
    password_hash  VARCHAR(64)  NOT NULL,          -- PBKDF2-HMAC-SHA256 en hexadecimal
    sal            VARCHAR(32)  NOT NULL,          -- sal aleatoria de 16 bytes en hexadecimal
    nombres        VARCHAR(100) NOT NULL,
    rol            VARCHAR(20)  NOT NULL CHECK (rol IN ('Administrador', 'Vendedor'))
);

-- models/cliente.py  ->  clientes
CREATE TABLE IF NOT EXISTS clientes (
    documento  VARCHAR(11)  PRIMARY KEY,           -- DNI (8) o RUC (11)
    nombre     VARCHAR(100) NOT NULL,              -- nombres o razón social
    telefono   VARCHAR(9)   NOT NULL
);

-- models/producto.py  ->  productos (inventario)
CREATE TABLE IF NOT EXISTS productos (
    codigo  VARCHAR(20)   PRIMARY KEY,
    nombre  VARCHAR(100)  NOT NULL,                -- tipo de maquinaria
    precio  NUMERIC(12,2) NOT NULL CHECK (precio > 0),   -- unitario, sin IGV
    stock   INTEGER       NOT NULL CHECK (stock >= 0)
);

-- models/venta.py  ->  ventas
CREATE TABLE IF NOT EXISTS ventas (
    codigo            VARCHAR(20)   PRIMARY KEY,
    documento_cliente VARCHAR(11)   NOT NULL REFERENCES clientes(documento),
    codigo_producto   VARCHAR(20)   NOT NULL REFERENCES productos(codigo),
    cantidad          INTEGER       NOT NULL CHECK (cantidad > 0),
    precio_unitario   NUMERIC(12,2) NOT NULL,      -- precio al momento de la venta (sin IGV)
    total             NUMERIC(14,2) NOT NULL,      -- con IGV (18 %)
    usuario_vendedor  VARCHAR(20)   NOT NULL REFERENCES empleados(usuario),
    fecha_venta       TIMESTAMP     NOT NULL DEFAULT now()   -- la asigna la BD al insertar
);

-- Regla de negocio: la venta y el cambio de stock se guardan en la MISMA transacción
-- (postgres.py sincroniza las 4 tablas dentro de un solo COMMIT; si falla algo, ROLLBACK).
-- El CHECK stock >= 0 es la última barrera si algún día falla la validación del servicio.
