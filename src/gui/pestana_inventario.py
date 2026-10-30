"""Pestaña de inventario: consulta para todos; registrar productos y reponer stock solo admin."""
import tkinter as tk
from tkinter import ttk

from exceptions.errores import ErrorNegocio
from gui import util
from services import auth_service as auth
from services import producto_service as productos
from services import validacion_service as val


class PestanaInventario(ttk.Frame):
    COLUMNAS = (("codigo", "Código", 100, "w"), ("nombre", "Maquinaria", 230, "w"),
                ("precio", "Precio (sin IGV)", 130, "e"), ("stock", "Stock", 70, "e"),
                ("estado", "Estado", 110, "w"))

    def __init__(self, padre):
        super().__init__(padre, padding=10)
        self.var_codigo = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_precio = tk.StringVar()
        self.var_stock = tk.StringVar()
        self.var_unidades = tk.StringVar()

        izquierda = ttk.Frame(self)
        izquierda.pack(side="left", fill="y", padx=(0, 10))
        alta = ttk.LabelFrame(izquierda, text="Registrar producto", padding=10)
        alta.pack(fill="x")
        util.campo(alta, 0, "Código", self.var_codigo)
        util.campo(alta, 1, "Tipo de maquinaria", self.var_nombre)
        util.campo(alta, 2, "Precio (S/, sin IGV)", self.var_precio)
        util.campo(alta, 3, "Stock inicial", self.var_stock)
        ttk.Button(alta, text="Registrar", command=self.registrar).grid(row=4, column=0,
                                                                         sticky="w", pady=(8, 0))
        reposicion = ttk.LabelFrame(izquierda, text="Reponer stock del producto elegido", padding=10)
        reposicion.pack(fill="x", pady=(10, 0))
        util.campo(reposicion, 0, "Unidades a agregar", self.var_unidades)
        ttk.Button(reposicion, text="Reponer", command=self.reponer).grid(row=1, column=0,
                                                                           sticky="w", pady=(8, 0))
        if not auth.es_admin():
            util.deshabilitar(izquierda)
            ttk.Label(izquierda, text="Solo el administrador puede modificar el inventario.",
                      foreground="gray", wraplength=240).pack(anchor="w", pady=(10, 0))

        derecha = ttk.Frame(self)
        derecha.pack(side="left", fill="both", expand=True)
        marco, self.tabla = util.crear_tabla(derecha, self.COLUMNAS, alto=16)
        marco.pack(fill="both", expand=True)
        self.tabla.tag_configure("bajo", foreground="#b00020")
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)
        self.actualizar()

    def actualizar(self):
        util.llenar_tabla(self.tabla, [
            (codigo, (codigo, nombre, f"S/ {precio:,.2f}", stock, "STOCK BAJO" if bajo else "Normal"),
             ("bajo",) if bajo else ())
            for codigo, nombre, precio, stock, bajo in productos.listar_productos()])

    def _al_seleccionar(self, _evento=None):
        codigo = util.seleccionado(self.tabla)
        if codigo:
            self.var_codigo.set(codigo)

    def registrar(self):
        try:
            auth.exigir_admin()
            codigo = val.validar_codigo(self.var_codigo.get())
            nombre = val.validar_nombre(self.var_nombre.get())
            precio = val.validar_decimal_positivo(self.var_precio.get())
            stock = val.validar_entero_no_negativo(self.var_stock.get())
            productos.registrar_producto(codigo, nombre, precio, stock)
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        util.mostrar_info("Inventario", "Producto registrado.")
        for variable in (self.var_codigo, self.var_nombre, self.var_precio, self.var_stock):
            variable.set("")
        self.actualizar()

    def reponer(self):
        try:
            auth.exigir_admin()
            codigo = val.validar_codigo(self.var_codigo.get())
            unidades = val.validar_entero_positivo(self.var_unidades.get())
            nuevo = productos.reponer_stock(codigo, unidades)
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        util.mostrar_info("Inventario", f"Stock actualizado. Disponible: {nuevo} unidad(es).")
        self.var_unidades.set("")
        self.actualizar()
