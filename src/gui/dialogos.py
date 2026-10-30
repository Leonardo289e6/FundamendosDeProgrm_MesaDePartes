"""Ventanas emergentes pequeñas."""
import tkinter as tk
from tkinter import ttk

from exceptions.errores import ErrorNegocio
from gui import util
from services import cliente_service as clientes
from services import validacion_service as val


class DialogoCliente(tk.Toplevel):
    """Pide nombre y celular para registrar un cliente nuevo (se usa al vender)."""

    def __init__(self, padre, documento):
        super().__init__(padre)
        self.title("Registrar cliente")
        self.resizable(False, False)
        self.documento = documento
        self.registrado = False
        self.var_nombre = tk.StringVar()
        self.var_telefono = tk.StringVar()
        marco = ttk.Frame(self, padding=14)
        marco.pack()
        ttk.Label(marco, text=f"Documento: {documento}").grid(row=0, column=0, columnspan=2,
                                                              sticky="w", pady=(0, 6))
        util.campo(marco, 1, "Nombres / Razón social", self.var_nombre, ancho=32)
        util.campo(marco, 2, "Celular (9 dígitos)", self.var_telefono, ancho=32)
        botones = ttk.Frame(marco)
        botones.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="e")
        ttk.Button(botones, text="Registrar", command=self.guardar).pack(side="left", padx=4)
        ttk.Button(botones, text="Cancelar", command=self.destroy).pack(side="left")
        self.transient(padre)
        self.grab_set()

    def guardar(self):
        try:
            nombre = val.validar_nombre(self.var_nombre.get())
            telefono = val.validar_telefono(self.var_telefono.get())
            clientes.registrar_cliente(self.documento, nombre, telefono)
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        self.registrado = True
        self.destroy()

    def esperar(self):
        """Bloquea hasta que se cierre la ventana. True si el cliente quedó registrado."""
        self.wait_window(self)
        return self.registrado
