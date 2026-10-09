# Sistema de Control de Ventas - Maquinarias Narváez S.A.C.

Prototipo en Python (versión inicial, Evaluación Parcial) para registrar, validar, buscar y ordenar ventas
con arreglos paralelos. Curso: Fundamentos de Programación.

## Estructura

```
src/sistemaventas/
├── config/        settings.py              constantes (capacidad, IGV, longitudes de DNI/RUC)
├── models/        venta.py                 arreglos paralelos (datos)
├── exceptions/    errores.py               errores propios del sistema
├── repositories/  venta_repository.py      guardar, obtener, buscar y ordenar
├── services/      validacion_service.py    reglas de validación
│                  venta_service.py         reglas de negocio
├── views/         consola_view.py          entradas y salidas por consola
├── controllers/   venta_controller.py      flujo del menú
└── main.py                                 punto de entrada
```

Flujo de dependencias: `main` -> `controllers` -> `services` -> `repositories` -> `models`.

## Ejecución

Requiere Python 3.8 o superior. Desde la carpeta `src`:

```
python -m sistemaventas.main
```

## Pendiente (Evaluación Final)

- Guardar los registros en archivos (persistencia).
- Procesamiento de cadenas de caracteres.
- Pruebas con datos reales recogidos en campo.
