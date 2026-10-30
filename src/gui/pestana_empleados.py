"""Pestaña de empleados (solo la ve el administrador)."""
import tkinter as tk
from tkinter import ttk

from config import settings
from exceptions.errores import ErrorNegocio, ValorInvalidoError
from gui import util
from services import auth_service as auth
from services import validacion_service as val


class PestanaEmpleados(ttk.Frame):
    COLUMNAS = (("usuario", "Usuario", 140, "w"), ("nombre", "Nombres", 300, "w"),
                ("rol", "Rol", 120, "w"))

    def __init__(self, padre):
        super().__init__(padre, padding=10)
        self.var_usuario = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_rol = tk.StringVar(value=settings.ROL_VENDEDOR)
        self.var_clave = tk.StringVar()
        self.var_clave2 = tk.StringVar()

        formulario = ttk.LabelFrame(self, text="Registrar empleado", padding=10)
        formulario.pack(side="left", fill="y", padx=(0, 10))
        util.campo(formulario, 0, "Usuario", self.var_usuario)
        util.campo(formulario, 1, "Nombres completos", self.var_nombre)
        ttk.Label(formulario, text="Rol").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Combobox(formulario, textvariable=self.var_rol, values=list(settings.ROLES),
                     state="readonly", width=23).grid(row=2, column=1, sticky="ew", pady=3)
        util.campo(formulario, 3, "Contraseña", self.var_clave, oculto=True)
        util.campo(formulario, 4, "Repita la contraseña", self.var_clave2, oculto=True)
        ttk.Button(formulario, text="Registrar", command=self.registrar).grid(
            row=5, column=0, sticky="w", pady=(10, 0))

        derecha = ttk.Frame(self)
        derecha.pack(side="left", fill="both", expand=True)
        marco, self.tabla = util.crear_tabla(derecha, self.COLUMNAS, alto=16)
        marco.pack(fill="both", expand=True)
        self.actualizar()

    def actualizar(self):
        try:
            lista = auth.listar_empleados()
        except ErrorNegocio:
            lista = []
        util.llenar_tabla(self.tabla, [(usuario, (usuario, nombre, rol), ())
                                       for usuario, nombre, rol in lista])

    def registrar(self):
        try:
            usuario = val.validar_usuario(self.var_usuario.get())
            nombre = val.validar_nombre(self.var_nombre.get())
            clave = val.validar_clave(self.var_clave.get())
            if clave != self.var_clave2.get():
                raise ValorInvalidoError("las contraseñas no coinciden.")
            auth.registrar_empleado(usuario, clave, nombre, self.var_rol.get())
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        util.mostrar_info("Empleados", "Empleado registrado.")
        for variable in (self.var_usuario, self.var_nombre, self.var_clave, self.var_clave2):
            variable.set("")
        self.actualizar()
