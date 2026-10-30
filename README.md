# Sistema de Control de Ventas - Maquinarias Narváez S.A.C.

Sistema de consola en Python para controlar ventas de maquinaria: acceso con usuario y contraseña,
registro de clientes, inventario con stock y ventas conectadas a ambos.
Los datos viven en **arreglos paralelos**. Curso: Fundamentos de Programación.

- **Entrega 1:** registro, validación, búsqueda por código, ordenamiento burbuja y listado.
- **Entrega 2:** CRUD completo, ordenamiento por selección, procesamiento de cadenas, búsqueda textual,
  arreglo bidimensional, y además: empleados con login, clientes, inventario y pruebas automáticas.
- **Entrega 3:** persistencia en archivos de texto con validación de integridad al cargar.
- **Entrega 4 / Evaluación Final:** recursividad con comparación iterativo vs recursivo, base de datos
  **PostgreSQL** (opcional) e interfaz gráfica **Tkinter** (opcional).

## Estructura

```
src/
├── config/        settings.py                 constantes (capacidades, IGV, roles, persistencia, PostgreSQL)
├── models/        empleado.py cliente.py      arreglos paralelos (solo datos)
│                  producto.py venta.py
├── exceptions/    errores.py                  errores propios del sistema
├── utils/         cadenas.py                  procesamiento de cadenas (funciones puras)
│                  seguridad.py                hash de contraseñas (PBKDF2 con sal)
│                  recursividad.py             sumas y búsquedas: versión iterativa y recursiva
├── repositories/  empleado_/cliente_/         único acceso a los arreglos (con vaciar() para recargar)
│                  producto_/venta_repository.py
├── almacenamiento/ gestor.py                  elige el almacén, carga al iniciar y confirma cada cambio
│                  archivos.py                 almacén en archivos de texto (un archivo por tabla)
│                  postgres.py                 almacén en PostgreSQL (una transacción por cambio)
│                  integridad.py               validación de los datos leídos antes de cargarlos
│                  tablas.py                   puente arreglos <-> tablas
│                  esquema_bd.sql              esquema de la base de datos
├── services/      validacion_service.py       reglas de validación
│                  auth_service.py             sesión, login y permisos por rol
│                  cliente_service.py          reglas de clientes
│                  producto_service.py         inventario y stock
│                  venta_service.py            ventas (descuenta stock, guarda vendedor)
│                  reporte_service.py          reportes de negocio (recursivos) y comparación iterativo vs recursivo
├── views/         consola_view.py             entradas y salidas por consola
│                  texto_reportes.py           textos de los reportes de recursividad (consola)
├── controllers/   entradas.py                 lectura de datos reutilizable
│                  auth_/cliente_/producto_/venta_controller.py
│                  recursividad_controller.py
│                  menu_controller.py          login, menú principal y submenús
├── gui/           app.py                      ventana principal: login -> pestañas
│                  pestana_ventas/clientes/inventario/reportes/empleados.py
│                  dialogos.py util.py         ventanas emergentes y ayudas de Tkinter
├── tests/         test_sistema.py             pruebas del núcleo (login, stock, permisos, estructuras)
│                  test_persistencia.py        archivos, integridad, gestor y PostgreSQL (conexión simulada)
│                  test_recursividad.py        casos base, equivalencias y desbordamiento
│                  test_gui_logica.py          lógica de la GUI con un Tkinter simulado (fake_tk.py)
├── arranque.py                                prepara (carga y valida) y cierra el sistema
└── main.py                                    punto de entrada (GUI por defecto; --consola para la consola)
```

Flujo de dependencias: `main` -> `controllers` / `gui` -> `services` -> `repositories` -> `models`.
Los servicios avisan a `almacenamiento.gestor` cada vez que confirman un cambio.

## Ejecución

Requiere Python 3.8 o superior. Desde la carpeta `src`:

```
python main.py             # interfaz gráfica (Tkinter)
python main.py --consola   # menú por consola
```

Los datos se guardan solos en `src/datos/` (archivos de texto) después de **cada** cambio y al cerrar.
Esa carpeta no se sube a git (contiene hashes de contraseñas).

**Primer uso:** si todavía no hay datos, el programa pide crear la cuenta del administrador; luego se
registran empleados, clientes y productos desde la propia aplicación. Para empezar de cero basta
borrar la carpeta `src/datos/` (o vaciar las tablas en PostgreSQL).

## Pruebas

```
python -m unittest discover -s tests -v
```

Las pruebas usan el modo `memoria` (no escriben en `src/datos/`) y no necesitan PostgreSQL ni pantalla.

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

## Datos (tablas)

| Entidad | Clave | Campos |
|---|---|---|
| empleados | usuario | hash, sal, nombres, rol |
| clientes | documento (DNI/RUC) | nombre, teléfono |
| productos | código | nombre, precio, stock |
| ventas | código | documento del cliente, código de producto, cantidad, precio, total, vendedor |

La venta guarda solo las **claves** del cliente, del producto y del vendedor. Al registrar una venta
se descuenta el stock; al modificarla o eliminarla, el stock se ajusta o se devuelve.
Detalle en `src/almacenamiento/esquema_bd.sql`.

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

## Persistencia en archivos (Entrega 3)

Cada tabla es un archivo de texto UTF-8 en `src/datos/`: `empleados.txt`, `clientes.txt`,
`productos.txt` y `ventas.txt`. Una línea por registro, campos separados por `;`, primera línea con
los nombres de columna:

```
codigo;nombre;precio;stock
EXC-01;EXCAVADORA;120000.00;3
```

- **Lectura/escritura segura:** `with open(...)`; se escriben primero archivos `.tmp` y luego se
  reemplazan los originales (`os.replace`), así un corte a mitad de camino no deja un archivo roto.
- **Validación de integridad al cargar** (`almacenamiento/integridad.py`): encabezados, cantidad de
  campos, números válidos, claves únicas, referencias de ventas a clientes/productos/vendedores que
  existan, stock sin negativos y capacidad de los arreglos. Si algo falla el programa **no arranca ni
  sobrescribe** los archivos y dice en qué archivo y línea está el problema.
- **Si guardar falla** (disco lleno, base caída) el cambio se deshace en memoria y se avisa al usuario.

## Base de datos PostgreSQL (opcional)

Los arreglos siguen siendo la memoria de trabajo; PostgreSQL es donde los datos sobreviven. Cada
cambio sincroniza las 4 tablas en **una sola transacción** (una venta y su descuento de stock se
guardan juntos o no se guardan).

1. Instalar el conector: `pip install -r requirements.txt` (psycopg2-binary).
2. Crear la base vacía (las tablas las crea el programa con `almacenamiento/esquema_bd.sql`):
   `createdb -U postgres ventas_narvaez`
3. Indicar la contraseña por variable de entorno (nunca en el código) y activar el modo:

```
# PowerShell
$env:PGPASSWORD = "su_clave"; $env:VENTAS_PERSISTENCIA = "postgresql"
# Linux / macOS
export PGPASSWORD=su_clave VENTAS_PERSISTENCIA=postgresql
python main.py
```

Host, puerto, base y usuario se pueden cambiar con `PGHOST`, `PGPORT`, `PGDATABASE` y `PGUSER`
(por defecto `localhost`, `5432`, `ventas_narvaez`, `postgres`). Limitación: se asume **una sola
instancia** del programa usando la base a la vez.

### Usar y ver la base desde pgAdmin

1. **Crear la base:** en pgAdmin, clic derecho en *Databases* > *Create* > *Database…*, nombre
   `ventas_narvaez` (dueño `postgres`) > *Save*. No hay que crear tablas: el programa las crea solo.
2. **Arrancar el programa** con `PGPASSWORD` y `VENTAS_PERSISTENCIA=postgresql` (ver arriba). Si la
   conexión falla, el mensaje del programa indica el motivo (servicio apagado, base inexistente, clave).
3. **Ver los datos:** *ventas_narvaez* > *Schemas* > *public* > *Tables* (aparecen `empleados`,
   `clientes`, `productos`, `ventas`). Clic derecho en una tabla > *View/Edit Data* > *All Rows*.
   Si no ves las tablas, clic derecho en *Tables* > *Refresh*.
4. **Consultas libres:** clic derecho en la base > *Query Tool*, por ejemplo:

```sql
SELECT v.codigo, c.nombre AS cliente, p.nombre AS maquinaria, v.cantidad, v.total, v.usuario_vendedor
FROM ventas v
JOIN clientes c ON c.documento = v.documento_cliente
JOIN productos p ON p.codigo = v.codigo_producto
ORDER BY v.fecha_venta;
```

5. **Empezar de cero:** en el Query Tool,
   `TRUNCATE ventas, clientes, productos, empleados;` y reiniciar el programa (pedirá crear el admin).

Conviene **no editar filas a mano mientras el programa está abierto**: el programa guarda su memoria
completa en cada cambio y pisaría lo editado. Cierre el programa, edite y vuelva a abrirlo.

## Recursividad (Entrega 4)

`utils/recursividad.py` tiene dos procesos, cada uno en versión iterativa y recursiva:

| Proceso | Iterativa | Recursiva | Caso base | Caso recursivo | Parada |
|---|---|---|---|---|---|
| Acumulado de ventas | `sumar_iterativo` | `sumar_recursivo` | `n <= 0` -> 0 | `valores[n-1] + suma(n-1)` | `n` baja de a 1 hasta 0 |
| Acumulado (dividir) | — | `sumar_recursivo_dividir` | 0 o 1 elemento | suma(izquierda) + suma(derecha) | cada mitad es más corta |
| Búsqueda por código | `buscar_iterativo` | `buscar_recursivo` | fin de lista (-1) o encontrado | buscar desde `pos + 1` | `pos` avanza hasta el final |

Además, `sumar_por_clave`, `contar_por_clave` y `posicion_mayor` (todas dividiendo a la mitad) son las que
calculan los reportes de la pestaña **Reportes** de la interfaz gráfica.

En el menú **Recursividad** (consola): explicación, acumulado de
ventas, búsqueda por código con tiempos de ambas versiones, y una **prueba de rendimiento** con
listas de 100 a 10 000 números donde la recursión lineal se desborda (`RecursionError`, límite de
Python ~1000) y la que divide a la mitad no (solo apila ~log2 n llamadas).

## Interfaz gráfica (Tkinter)

`python main.py`: inicio de sesión (3 intentos), y pestañas Ventas, Clientes, Inventario,
Reportes y (solo administrador) Empleados. Usa los mismos servicios y validaciones que la
consola, así que los permisos por rol y el stock se comportan igual.

**Reportes:** cifras clave (ventas registradas, monto total con IGV, venta de mayor monto, valor del
inventario, productos con stock bajo) y una tabla de ventas agrupadas por vendedor, cliente o
maquinaria con número de ventas, unidades, total y porcentaje. Se actualiza al entrar a la pestaña.

