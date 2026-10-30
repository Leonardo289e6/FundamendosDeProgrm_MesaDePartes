"""Pestaña de clientes: registrar, buscar, modificar y listar."""
import tkinter as tk
from tkinter import ttk

from exceptions.errores import ErrorNegocio
from gui import util
from services import cliente_service as clientes
from services import validacion_service as val
from utils import cadenas


class PestanaClientes(ttk.Frame):
    COLUMNAS = (("tipo", "Tipo", 60, "w"), ("documento", "Documento", 110, "w"),
                ("nombre", "Nombres / Razón social", 330, "w"), ("telefono", "Teléfono", 110, "w"))

    def __init__(self, padre):
        super().__init__(padre, padding=10)
        self.var_documento = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_telefono = tk.StringVar()

        formulario = ttk.LabelFrame(self, text="Datos del cliente", padding=10)
        formulario.pack(side="left", fill="y", padx=(0, 10))
        util.campo(formulario, 0, "DNI o RUC", self.var_documento)
        util.campo(formulario, 1, "Nombres / Razón social", self.var_nombre)
        util.campo(formulario, 2, "Celular (9 dígitos)", self.var_telefono)
        botones = ttk.Frame(formulario)
        botones.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="w")
        for texto, comando in (("Registrar", self.registrar), ("Modificar", self.modificar),
                               ("Buscar", self.buscar), ("Ver todos", self.actualizar),
                               ("Limpiar", self.limpiar)):
            ttk.Button(botones, text=texto, command=comando).pack(side="left", padx=(0, 6))

        derecha = ttk.Frame(self)
        derecha.pack(side="left", fill="both", expand=True)
        marco, self.tabla = util.crear_tabla(derecha, self.COLUMNAS, alto=16)
        marco.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)
        self.var_estado = tk.StringVar()
        ttk.Label(derecha, textvariable=self.var_estado).pack(anchor="w", pady=(6, 0))
        self.actualizar()

    def actualizar(self):
        self._mostrar(clientes.listar_clientes())

    def _mostrar(self, lista):
        util.llenar_tabla(self.tabla, [
            (documento, (cadenas.tipo_documento(documento), cadenas.enmascarar_documento(documento),
                         nombre, telefono), ())
            for documento, nombre, telefono in lista])
        self.var_estado.set(f"Clientes registrados: {len(lista)}")

    def _al_seleccionar(self, _evento=None):
        documento = util.seleccionado(self.tabla)
        cliente = clientes.buscar_cliente(documento) if documento else None
        if cliente is not None:
            self.var_documento.set(cliente[0])
            self.var_nombre.set(cliente[1])
            self.var_telefono.set(cliente[2])

    def limpiar(self):
        for variable in (self.var_documento, self.var_nombre, self.var_telefono):
            variable.set("")

    def registrar(self):
        try:
            documento = val.validar_documento(self.var_documento.get())
            nombre = val.validar_nombre(self.var_nombre.get())
            telefono = val.validar_telefono(self.var_telefono.get())
            clientes.registrar_cliente(documento, nombre, telefono)
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        util.mostrar_info("Clientes", "Cliente registrado.")
        self.limpiar()
        self.actualizar()

    def modificar(self):
        try:
            documento = val.validar_documento(self.var_documento.get())
            nombre = val.validar_nombre(self.var_nombre.get())
            telefono = val.validar_telefono(self.var_telefono.get())
            clientes.modificar_cliente(documento, nombre, telefono)
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        util.mostrar_info("Clientes", "Cliente modificado.")
        self.actualizar()

    def buscar(self):
        try:
            documento = val.validar_documento(self.var_documento.get())
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        cliente = clientes.buscar_cliente(documento)
        if cliente is None:
            util.mostrar_info("Clientes", "Cliente no encontrado.")
            return
        self._mostrar([cliente])
        self.var_nombre.set(cliente[1])
        self.var_telefono.set(cliente[2])
        self.var_estado.set("Coincidencias: 1")
