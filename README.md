# Sistema de Control de Ventas - Maquinarias Narváez S.A.C.

Sistema de consola en Python para controlar ventas de maquinaria: acceso con usuario y contraseña,
registro de clientes, inventario con stock y ventas conectadas a ambos.
Los datos viven en **arreglos paralelos**. Curso: Fundamentos de Programación.

- **Entrega 1:** registro, validación, búsqueda por código, ordenamiento burbuja y listado.
- **Entrega 2:** CRUD completo, ordenamiento por selección, procesamiento de cadenas, búsqueda textual,
  arreglo bidimensional, y además: empleados con login, clientes, inventario y pruebas automáticas.

## Estructura

```
src/
├── config/        settings.py                 constantes (capacidades, IGV, roles, intentos de login)
├── models/        empleado.py cliente.py      arreglos paralelos (solo datos)
│                  producto.py venta.py
├── exceptions/    errores.py                  errores propios del sistema
├── utils/         cadenas.py                  procesamiento de cadenas (funciones puras)
│                  seguridad.py                hash de contraseñas (PBKDF2 con sal)
├── repositories/  empleado_/cliente_/         único acceso a los arreglos
│                  producto_/venta_repository.py
├── services/      validacion_service.py       reglas de validación
│                  auth_service.py             sesión, login y permisos por rol
│                  cliente_service.py          reglas de clientes
│                  producto_service.py         inventario y stock
│                  venta_service.py            ventas (descuenta stock, guarda vendedor)
├── views/         consola_view.py             entradas y salidas por consola
├── controllers/   entradas.py                 lectura de datos reutilizable
│                  auth_/cliente_/producto_/venta_controller.py
│                  menu_controller.py          login, menú principal y submenús
├── tests/         test_sistema.py             pruebas automáticas
├── datos_demo.py                              datos de ejemplo (sin persistencia aún)
└── main.py                                    punto de entrada
docs/esquema_bd.sql                            esquema de BD para el futuro
```

Flujo de dependencias: `main` -> `controllers` -> `services` -> `repositories` -> `models`.

## Ejecución

Requiere Python 3.8 o superior. Desde la carpeta `src`:

```
python main.py
```

Usuarios de ejemplo (solo para demostración, definidos en `datos_demo.py`):

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `vendedor1` | `venta123` | Vendedor |

Si `CARGAR_DATOS_DEMO = False` en `config/settings.py`, el primer arranque pide crear al administrador.

## Pruebas

```
python -m unittest discover -s tests -v
```

## Roles y permisos

| Acción | Vendedor | Administrador |
|---|:---:|:---:|
| Registrar / modificar / listar / buscar ventas | Sí | Sí |
| Registrar y modificar clientes | Sí | Sí |
| Consultar inventario | Sí | Sí |
| Eliminar ventas | No | Sí |
| Registrar productos y reponer stock | No | Sí |
| Registrar empleados | No | Sí |

Los permisos se validan en los **servicios**, no solo en el menú.

## Datos (futuras tablas)

| Entidad | Clave | Campos |
|---|---|---|
| empleados | usuario | hash, sal, nombres, rol |
| clientes | documento (DNI/RUC) | nombre, teléfono |
| productos | código | nombre, precio, stock |
| ventas | código | documento del cliente, código de producto, cantidad, precio, total, vendedor |

La venta guarda solo las **claves** del cliente, del producto y del vendedor. Al registrar una venta
se descuenta el stock; al modificarla o eliminarla, el stock se ajusta o se devuelve.
Detalle en `docs/esquema_bd.sql`.

## Cadenas de caracteres (`utils/cadenas.py`)

| Método | Uso |
|---|---|
| `strip`, `replace`, `upper` | `normalizar_codigo`: `" v 001 "` -> `V001` |
| `split` + `join` | `normalizar_nombre` y `separar_registro` |
| `replace` | `quitar_tildes` para comparar sin acentos |
| `find` (IndexOf) | `contiene`: búsqueda textual |
| Substring (`[:n]`, `[-2:]`) | `abreviar`, `enmascarar_documento` (`47581234` -> `******34`) |
| `len` | `tipo_documento`: 8 = DNI, 11 = RUC |
| Concatenación | `"*" * k + doc[-2:]`, `texto[:n] + "..."` |

## Pendiente (Evaluación Final)

- Guardar los registros en archivos (persistencia). Solo cambia la capa `repositories`.
- Pruebas con datos reales recogidos en campo.
- Opcional: interfaz gráfica (Tkinter) y base de datos (`docs/esquema_bd.sql`).
