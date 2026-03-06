import tkinter as tk
from tkinter import messagebox
from vistas.subventanas.interfaceSubViews import InterfaceSubViews
from modelo.CRU import obtenerCultivosUsuario

class CultivosView(InterfaceSubViews):
    def __init__(self, root, user, estilo, notificationService):
        self.notificationService = notificationService
        self.user = user
        self.root = root
        self.win = tk.Toplevel(root)
        self.estilo = estilo
        self.titulo = 'Cultivos'
        self.win.title(self.titulo)
        self.win.geometry('400x330')
        self.win.config(bg=self.estilo.colorFondo())

        tk.Label(
            self.win,
            text='🌱 Mis Cultivos',
            bg=self.estilo.colorFondo(),
            fg=self.estilo.colorLetra(),
            font=('Arial',14,'bold')
        ).pack(pady=8)

        self.listbox = tk.Listbox(self.win, fg=estilo.colorFondo(), bg=estilo.colorLetra(), width=60)
        self.listbox.pack(pady=6, expand=True)
        self.actualizarLista()

        tk.Button(
            self.win,
            text='Agregar',
            fg=self.estilo.colorFondo(),
            bg=self.estilo.colorLetra(),
            command=self.agregarCultivo
        ).pack(anchor='s', pady=4)

        tk.Button(
            self.win,
            text='Eliminar',
            fg=self.estilo.colorFondo(),
            bg=self.estilo.colorLetra(),
            command=self.eliminarCultivo
        ).pack(anchor='s', pady=4)

        tk.Button(
            self.win,
            text='Cerrar',
            fg=self.estilo.colorFondo(),
            bg=self.estilo.colorLetra(),
            command=self.botonCerrar
        ).pack(anchor='s', pady=4)

        self.bloquearRoot()    

    def agregarCultivo(self):
        # Obtener selección del Listbox
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            cultivo_texto = self.listbox.get(index)
            nombre_cultivo = cultivo_texto.split("|")[0].strip()
        else:
            nombre_cultivo=""

        # Usamos ControladorSubVistas para abrir la ventana de agregar/editar cultivo
        from controlador.controladorSubVistas import ControladorSubVistas
        controlador = ControladorSubVistas(
            None, self.root, self.user, None, None, None, self.estilo, self.notificationService
        )
        controlador.open_agregar_cultivos_view(nombre_cultivo)
        self.win.destroy()


    def eliminarCultivo(self):
        if not self.listbox.curselection():
            messagebox.showwarning("Error", "Selecciona un cultivo para eliminar.")
            return

        index = self.listbox.curselection()[0]
        cultivo_texto = self.listbox.get(index)
        nombre_cultivo = cultivo_texto.split("|")[0].strip()

        if not messagebox.askyesno("Confirmar", f"¿Deseas eliminar el cultivo '{nombre_cultivo}'?"):
            return

        # Llamamos a ControladorRegis para eliminar directo
        from controlador.controladorRegis import ControladorRegis
        controlador = ControladorRegis(None, None, self.root, self.user, None, self.estilo)
        exito, msg = controlador.eliminarCultivo(nombre_cultivo,user=self.user)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.actualizarLista()
        else:
            messagebox.showerror("Error", msg)


    def actualizarLista(self):
        cultivos = obtenerCultivosUsuario(self.user)
        self.listbox.delete(0, tk.END)  
        if not cultivos:
            self.listbox.insert(tk.END, "No tienes cultivos registrados.")
            return
        for c in cultivos:
            texto = f"{c['nombre'].capitalize()} | Cantidad: {c['cantidad']} | Precio Unitario: {c['precio']}"
            self.listbox.insert(tk.END, texto)