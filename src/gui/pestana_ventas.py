"""Pestaña de ventas: registrar, modificar, eliminar, buscar, ordenar y resumir."""
import tkinter as tk
from tkinter import ttk

from exceptions.errores import ErrorNegocio, ValorInvalidoError, VentaNoEncontradaError
from gui import util
from gui.dialogos import DialogoCliente
from services import auth_service as auth
from services import cliente_service as clientes
from services import producto_service as productos
from services import validacion_service as val
from services import venta_service as ventas
from utils import cadenas


class PestanaVentas(ttk.Frame):
    COLUMNAS = (("codigo", "Código", 80, "w"), ("documento", "Documento", 100, "w"),
                ("cliente", "Cliente", 190, "w"), ("maquinaria", "Maquinaria", 150, "w"),
                ("cantidad", "Cant.", 50, "e"), ("total", "Total (S/)", 110, "e"),
                ("vendedor", "Vendedor", 90, "w"))

    def __init__(self, padre):
        super().__init__(padre, padding=10)
        self.var_codigo = tk.StringVar()
        self.var_documento = tk.StringVar()
        self.var_producto = tk.StringVar()
        self.var_cantidad = tk.StringVar()
        self.var_busqueda = tk.StringVar()
        self.var_estado = tk.StringVar()
        self._armar_formulario()
        self._armar_listado()
        self.actualizar()

    # ---------- construcción ----------
    def _armar_formulario(self):
        formulario = ttk.LabelFrame(self, text="Datos de la venta", padding=10)
        formulario.pack(side="left", fill="y", padx=(0, 10))
        util.campo(formulario, 0, "Código de venta", self.var_codigo)
        util.campo(formulario, 1, "DNI o RUC del cliente", self.var_documento)
        ttk.Label(formulario, text="Producto").grid(row=2, column=0, sticky="w", pady=3)
        self.combo_producto = ttk.Combobox(formulario, textvariable=self.var_producto,
                                           state="readonly", width=34)
        self.combo_producto.grid(row=2, column=1, sticky="ew", pady=3)
        util.campo(formulario, 3, "Cantidad", self.var_cantidad)
        ttk.Label(formulario, text="Al modificar, deje el producto vacío para conservarlo.",
                  foreground="gray").grid(row=4, column=0, columnspan=2, sticky="w", pady=(2, 8))
        botones = ttk.Frame(formulario)
        botones.grid(row=5, column=0, columnspan=2, sticky="w")
        ttk.Button(botones, text="Registrar", command=self.registrar).pack(side="left", padx=(0, 6))
        ttk.Button(botones, text="Modificar", command=self.modificar).pack(side="left", padx=(0, 6))
        self.boton_eliminar = ttk.Button(botones, text="Eliminar", command=self.eliminar)
        self.boton_eliminar.pack(side="left", padx=(0, 6))
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left")
        if not auth.es_admin():
            self.boton_eliminar.state(["disabled"])
            ttk.Label(formulario, text="Solo el administrador puede eliminar ventas.",
                      foreground="gray").grid(row=6, column=0, columnspan=2, sticky="w", pady=(6, 0))

    def _armar_listado(self):
        derecha = ttk.Frame(self)
        derecha.pack(side="left", fill="both", expand=True)

        busqueda = ttk.Frame(derecha)
        busqueda.pack(fill="x", pady=(0, 6))
        ttk.Label(busqueda, text="Buscar:").pack(side="left")
        ttk.Entry(busqueda, textvariable=self.var_busqueda, width=24).pack(side="left", padx=6)
        ttk.Button(busqueda, text="Por código", command=self.buscar_codigo).pack(side="left", padx=2)
        ttk.Button(busqueda, text="Por cliente o maquinaria",
                   command=self.buscar_texto).pack(side="left", padx=2)
        ttk.Button(busqueda, text="Ver todas", command=self.actualizar).pack(side="left", padx=2)

        marco, self.tabla = util.crear_tabla(derecha, self.COLUMNAS)
        marco.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

        pie = ttk.Frame(derecha)
        pie.pack(fill="x", pady=(6, 0))
        ttk.Button(pie, text="Ordenar por código (burbuja)",
                   command=lambda: self.ordenar(1)).pack(side="left", padx=(0, 6))
        ttk.Button(pie, text="Ordenar por total (selección)",
                   command=lambda: self.ordenar(2)).pack(side="left", padx=(0, 6))
        ttk.Button(pie, text="Resumen de unidades", command=self.resumen).pack(side="left")
        ttk.Label(pie, textvariable=self.var_estado).pack(side="right")

    # ---------- datos ----------
    def actualizar(self):
        self._cargar_productos()
        lista, suma = ventas.listar_ventas()
        self._mostrar(lista)
        self.var_estado.set(f"Ventas registradas: {len(lista)} | Monto acumulado: S/ {suma:,.2f}")

    def _mostrar(self, lista):
        util.llenar_tabla(self.tabla, [
            (v[0], (v[0], cadenas.enmascarar_documento(v[1]), v[2], v[3], v[4], f"{v[6]:,.2f}", v[7]), ())
            for v in lista])

    def _cargar_productos(self):
        """Llena la lista desplegable con el stock actual, conservando el producto elegido."""
        elegido = self._codigo_producto()
        opciones = [f"{codigo} - {nombre} (stock {stock})"
                    for codigo, nombre, _precio, stock, _bajo in productos.listar_productos()]
        self.combo_producto["values"] = opciones
        self.var_producto.set(next((o for o in opciones if o.split(" - ")[0] == elegido), ""))

    def _codigo_producto(self):
        """Código del producto elegido en la lista, o None si no hay ninguno."""
        texto = self.var_producto.get().strip()
        return texto.split(" - ")[0] if texto else None

    def _al_seleccionar(self, _evento=None):
        codigo = util.seleccionado(self.tabla)
        venta = ventas.buscar_venta(codigo) if codigo else None
        if venta is not None:
            self.var_codigo.set(venta[0])
            self.var_documento.set(venta[1])
            self.var_cantidad.set(str(venta[4]))
            self.var_producto.set("")       # vacío = conservar el producto al modificar

    def limpiar(self):
        for variable in (self.var_codigo, self.var_documento, self.var_producto, self.var_cantidad):
            variable.set("")

    # ---------- acciones ----------
    def _asegurar_cliente(self, documento):
        """Si el cliente no existe ofrece registrarlo. True si ya existe o se registró."""
        if clientes.existe_cliente(documento):
            return True
        if not util.confirmar("Cliente no registrado", "El cliente no está registrado. ¿Registrarlo ahora?"):
            return False
        return DialogoCliente(self, documento).esperar()

    def registrar(self):
        try:
            codigo = val.validar_codigo(self.var_codigo.get())
            ventas.validar_codigo_nuevo(codigo)
            documento = val.validar_documento(self.var_documento.get())
            if not self._asegurar_cliente(documento):
                return
            cod_producto = self._codigo_producto()
            if cod_producto is None:
                raise ValorInvalidoError("elija un producto.")
            cantidad = val.validar_entero_positivo(self.var_cantidad.get())
            total = ventas.registrar_venta(codigo, documento, cod_producto, cantidad)
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        util.mostrar_info("Venta registrada", f"Total con IGV: S/ {total:,.2f}")
        self.limpiar()
        self.actualizar()

    def modificar(self):
        try:
            codigo = val.validar_codigo(self.var_codigo.get())
            documento = val.validar_documento(self.var_documento.get())
            cantidad = val.validar_entero_positivo(self.var_cantidad.get())
            total = ventas.modificar_venta(codigo, documento, self._codigo_producto(), cantidad)
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        util.mostrar_info("Venta modificada", f"Nuevo total con IGV: S/ {total:,.2f}")
        self.actualizar()

    def eliminar(self):
        try:
            auth.exigir_admin()
            codigo = val.validar_codigo(self.var_codigo.get())
            if ventas.buscar_venta(codigo) is None:
                raise VentaNoEncontradaError()
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        if not util.confirmar("Eliminar venta",
                              f"¿Eliminar la venta {codigo}? Las unidades volverán al inventario."):
            return
        try:
            ventas.eliminar_venta(codigo)
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        util.mostrar_info("Venta eliminada", "Las unidades volvieron al inventario.")
        self.limpiar()
        self.actualizar()

    def buscar_codigo(self):
        try:
            codigo = val.validar_codigo(self.var_busqueda.get())
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        venta = ventas.buscar_venta(codigo)
        if venta is None:
            util.mostrar_info("Búsqueda", "Código no encontrado.")
            return
        self._mostrar([venta])
        self.var_estado.set("Coincidencias: 1")

    def buscar_texto(self):
        try:
            texto = val.validar_texto(self.var_busqueda.get())
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        encontradas = ventas.buscar_por_texto(texto)
        if not encontradas:
            util.mostrar_info("Búsqueda", "Sin coincidencias.")
            return
        self._mostrar(encontradas)
        self.var_estado.set(f"Coincidencias: {len(encontradas)}")

    def ordenar(self, criterio):
        ventas.ordenar_ventas(criterio)
        self.actualizar()

    def resumen(self):
        lista, _ = ventas.listar_ventas()
        if not lista:
            util.mostrar_info("Resumen", "No hay ventas registradas.")
            return
        maquinas, matriz = ventas.resumen_unidades()
        ventana = tk.Toplevel(self)
        ventana.title("Unidades vendidas por tipo de cliente y maquinaria")
        columnas = [("tipo", "Tipo de cliente", 130, "w")] + [(f"m{i}", mq, 130, "e")
                                                            for i, mq in enumerate(maquinas)]
        marco, tabla = util.crear_tabla(ventana, columnas, alto=2)
        marco.pack(fill="both", expand=True, padx=10, pady=10)
        for etiqueta, fila in zip(("Persona (DNI)", "Empresa (RUC)"), matriz):
            tabla.insert("", "end", values=[etiqueta] + fila)
