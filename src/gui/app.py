"""Ventana principal: primer uso -> inicio de sesión -> pestañas por módulo."""
import tkinter as tk
from tkinter import messagebox, ttk

import arranque
from config import settings
from exceptions.errores import ErrorNegocio, ValorInvalidoError
from gui import util
from gui.pestana_clientes import PestanaClientes
from gui.pestana_empleados import PestanaEmpleados
from gui.pestana_inventario import PestanaInventario
from gui.pestana_reportes import PestanaReportes
from gui.pestana_ventas import PestanaVentas
from services import auth_service as auth
from services import validacion_service as val
from utils import cadenas


class PantallaLogin(ttk.Frame):
    def __init__(self, app):
        super().__init__(app, padding=30)
        self.app = app
        self.var_usuario = tk.StringVar()
        self.var_clave = tk.StringVar()
        ttk.Label(self, text="MAQUINARIAS NARVÁEZ S.A.C.", font=("Segoe UI", 18, "bold")).pack(pady=(40, 4))
        ttk.Label(self, text="Control de ventas - Iniciar sesión").pack(pady=(0, 20))
        formulario = ttk.Frame(self)
        formulario.pack()
        entrada = util.campo(formulario, 0, "Usuario", self.var_usuario)
        util.campo(formulario, 1, "Contraseña", self.var_clave, oculto=True)
        ttk.Button(self, text="Ingresar", command=self.ingresar).pack(pady=18)
        self.bind_all("<Return>", lambda _e: self.ingresar())
        entrada.focus_set()

    def ingresar(self):
        usuario = cadenas.normalizar_usuario(self.var_usuario.get())
        try:
            auth.iniciar_sesion(usuario, self.var_clave.get())
        except ErrorNegocio as error:
            self.app.intentos += 1
            util.mostrar_error(f"{error} (intento {self.app.intentos}/{settings.MAX_INTENTOS_LOGIN})")
            self.var_clave.set("")
            if self.app.intentos >= settings.MAX_INTENTOS_LOGIN:
                util.mostrar_info("Acceso", "Se agotaron los intentos.")
                self.app.cerrar()
            return
        self.unbind_all("<Return>")
        self.app.mostrar_principal()


class PantallaPrimerAdmin(ttk.Frame):
    """No hay empleados: se crea la cuenta del administrador."""

    def __init__(self, app):
        super().__init__(app, padding=30)
        self.app = app
        self.var_usuario = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_clave = tk.StringVar()
        self.var_clave2 = tk.StringVar()
        ttk.Label(self, text="Primer uso: cree la cuenta del administrador",
                  font=("Segoe UI", 14, "bold")).pack(pady=(30, 16))
        formulario = ttk.Frame(self)
        formulario.pack()
        util.campo(formulario, 0, "Usuario", self.var_usuario)
        util.campo(formulario, 1, "Nombres completos", self.var_nombre)
        util.campo(formulario, 2, "Contraseña", self.var_clave, oculto=True)
        util.campo(formulario, 3, "Repita la contraseña", self.var_clave2, oculto=True)
        ttk.Button(self, text="Crear administrador", command=self.crear).pack(pady=18)

    def crear(self):
        try:
            usuario = val.validar_usuario(self.var_usuario.get())
            nombre = val.validar_nombre(self.var_nombre.get())
            clave = val.validar_clave(self.var_clave.get())
            if clave != self.var_clave2.get():
                raise ValorInvalidoError("las contraseñas no coinciden.")
            auth.crear_primer_administrador(usuario, clave, nombre)
        except ErrorNegocio as error:
            util.mostrar_error(error)
            return
        util.mostrar_info("Administrador", "Administrador creado. Ahora inicie sesión.")
        self.app.mostrar_inicio()


class PantallaPrincipal(ttk.Frame):
    def __init__(self, app):
        super().__init__(app, padding=8)
        self.app = app
        _usuario, nombre, rol = auth.empleado_actual()
        cabecera = ttk.Frame(self)
        cabecera.pack(fill="x", pady=(0, 6))
        ttk.Label(cabecera, text=f"Sesión: {nombre} ({rol})", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(cabecera, text="Cerrar sesión", command=app.cerrar_sesion).pack(side="right")

        self.cuaderno = ttk.Notebook(self)
        self.cuaderno.pack(fill="both", expand=True)
        self.pestanas = [("Ventas", PestanaVentas(self.cuaderno)),
                         ("Clientes", PestanaClientes(self.cuaderno)),
                         ("Inventario", PestanaInventario(self.cuaderno)),
                         ("Reportes", PestanaReportes(self.cuaderno))]
        if auth.es_admin():
            self.pestanas.append(("Empleados", PestanaEmpleados(self.cuaderno)))
        for titulo, pestana in self.pestanas:
            self.cuaderno.add(pestana, text=titulo)
        self.cuaderno.bind("<<NotebookTabChanged>>", self._al_cambiar_pestana)

    def _al_cambiar_pestana(self, _evento=None):
        """Al entrar a una pestaña se refresca (otra pudo cambiar stock, ventas o clientes)."""
        indice = self.cuaderno.index(self.cuaderno.select())
        self.pestanas[indice][1].actualizar()


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maquinarias Narváez S.A.C. - Control de ventas")
        self.geometry("1150x640")
        self.minsize(960, 560)
        try:
            ttk.Style(self).theme_use("clam")
        except tk.TclError:
            pass
        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.intentos = 0
        self._pantalla = None
        self.mostrar_inicio()

    def _mostrar(self, pantalla):
        if self._pantalla is not None:
            self._pantalla.destroy()
        self._pantalla = pantalla
        pantalla.pack(fill="both", expand=True)

    def mostrar_inicio(self):
        self.intentos = 0
        self._mostrar(PantallaLogin(self) if auth.hay_empleados() else PantallaPrimerAdmin(self))

    def mostrar_principal(self):
        self._mostrar(PantallaPrincipal(self))

    def cerrar_sesion(self):
        auth.cerrar_sesion()
        self.mostrar_inicio()

    def cerrar(self):
        """Guardado final y salida."""
        aviso = arranque.cerrar()
        if aviso:
            messagebox.showwarning("Aviso al guardar", aviso)
        self.destroy()


def iniciar():
    Aplicacion().mainloop()
