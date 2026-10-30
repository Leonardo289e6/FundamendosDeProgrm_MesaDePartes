"""Pestaña de reportes: cifras clave del negocio y ventas agrupadas por vendedor, cliente o maquinaria.

Los acumulados los calcula services/reporte_service.py con funciones recursivas
(utils/recursividad.py). La pestaña solo muestra los resultados; no modifica datos.
"""
import tkinter as tk
from tkinter import ttk

from gui import util
from services import reporte_service as reportes


class PestanaReportes(ttk.Frame):
    COLUMNAS = (("grupo", "Grupo", 260, "w"), ("ventas", "N.º de ventas", 100, "e"),
                ("unidades", "Unidades", 90, "e"), ("total", "Total (S/)", 140, "e"),
                ("porcentaje", "% del total", 90, "e"))

    def __init__(self, padre):
        super().__init__(padre, padding=10)
        self.var_agrupar = tk.StringVar(value="Vendedor")
        self.var_ventas = tk.StringVar()
        self.var_monto = tk.StringVar()
        self.var_mayor = tk.StringVar()
        self.var_inventario = tk.StringVar()
        self.var_bajo = tk.StringVar()
        self._armar_resumen()
        self._armar_detalle()
        self.actualizar()

    # ---------- construcción ----------
    def _armar_resumen(self):
        marco = ttk.Frame(self)
        marco.pack(fill="x")
        tarjetas = (("Ventas registradas", self.var_ventas), ("Monto total vendido (con IGV)", self.var_monto),
                    ("Venta de mayor monto", self.var_mayor), ("Valor del inventario", self.var_inventario),
                    ("Productos con stock bajo", self.var_bajo))
        for columna, (titulo, variable) in enumerate(tarjetas):
            tarjeta = ttk.LabelFrame(marco, text=titulo, padding=8)
            tarjeta.grid(row=0, column=columna, sticky="nsew", padx=(0, 8))
            marco.columnconfigure(columna, weight=1)
            ttk.Label(tarjeta, textvariable=variable, font=("Segoe UI", 12, "bold")).pack(anchor="w")

    def _armar_detalle(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(14, 6))
        ttk.Label(barra, text="Ver ventas por:").pack(side="left")
        combo = ttk.Combobox(barra, textvariable=self.var_agrupar, state="readonly", width=14,
                             values=list(reportes.AGRUPACIONES))
        combo.pack(side="left", padx=6)
        combo.bind("<<ComboboxSelected>>", lambda _e: self.mostrar_grupo())
        ttk.Button(barra, text="Actualizar", command=self.actualizar).pack(side="left", padx=6)

        marco, self.tabla = util.crear_tabla(self, self.COLUMNAS, alto=12)
        marco.pack(fill="both", expand=True)
        ttk.Label(self, foreground="gray",
                  text="Los totales se calculan con funciones recursivas (utils/recursividad.py).").pack(
            anchor="w", pady=(6, 0))

    # ---------- datos ----------
    def actualizar(self):
        """Se llama al entrar a la pestaña: otra pudo registrar ventas o mover el stock."""
        r = reportes.resumen_general()
        self.var_ventas.set(str(r["n_ventas"]))
        self.var_monto.set(f"S/ {r['monto_total']:,.2f}")
        mayor = r["venta_mayor"]
        self.var_mayor.set("-" if mayor is None else f"{mayor[0]}: S/ {mayor[6]:,.2f}")
        self.var_inventario.set(f"S/ {r['valor_inventario']:,.2f}")
        self.var_bajo.set(str(r["productos_stock_bajo"]))
        self.mostrar_grupo()

    def mostrar_grupo(self):
        filas = reportes.reporte_por(self.var_agrupar.get())
        util.llenar_tabla(self.tabla, [
            (f"G{i}", (grupo, n, unidades, f"{total:,.2f}", f"{porcentaje:.1f} %"), ())
            for i, (grupo, n, unidades, total, porcentaje) in enumerate(filas)])
