"""Ayudas comunes de la interfaz gráfica: mensajes, campos de formulario y tablas."""
from tkinter import messagebox, ttk


def mostrar_error(error):
    texto = str(error)
    messagebox.showerror("Error", texto[:1].upper() + texto[1:])


def mostrar_info(titulo, texto):
    messagebox.showinfo(titulo, texto)


def confirmar(titulo, texto):
    return messagebox.askyesno(titulo, texto)


def campo(padre, fila, etiqueta, variable, ancho=26, oculto=False):
    """Etiqueta + caja de texto en la fila indicada de un formulario (grid)."""
    ttk.Label(padre, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=(0, 8), pady=3)
    entrada = ttk.Entry(padre, textvariable=variable, width=ancho, show="*" if oculto else "")
    entrada.grid(row=fila, column=1, sticky="ew", pady=3)
    return entrada


def crear_tabla(padre, columnas, alto=14):
    """columnas: lista de (id, título, ancho, alineación). Devuelve (marco, tabla)."""
    marco = ttk.Frame(padre)
    tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings",
                         height=alto, selectmode="browse")
    for ident, titulo, ancho, ancla in columnas:
        tabla.heading(ident, text=titulo)
        tabla.column(ident, width=ancho, anchor=ancla)
    barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    return marco, tabla


def llenar_tabla(tabla, filas):
    """filas: lista de (id_interno, valores, etiquetas). Reemplaza el contenido."""
    tabla.delete(*tabla.get_children())
    for iid, valores, etiquetas in filas:
        tabla.insert("", "end", iid=iid, values=valores, tags=etiquetas)


def seleccionado(tabla):
    """Id interno de la fila elegida, o None."""
    seleccion = tabla.selection()
    return seleccion[0] if seleccion else None


def deshabilitar(contenedor):
    """Desactiva cajas, botones y listas desplegables de un contenedor (y de sus hijos)."""
    for hijo in contenedor.winfo_children():
        if isinstance(hijo, (ttk.Entry, ttk.Button, ttk.Combobox)):
            hijo.state(["disabled"])
        else:
            deshabilitar(hijo)
