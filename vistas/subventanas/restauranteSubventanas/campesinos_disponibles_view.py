import tkinter as tk
from tkinter import messagebox
from vistas.subventanas.interfaceSubViews import InterfaceSubViews
from modelo.CRU import obtenerCampesinosConCultivos, obtener_usuario_por_email

class CampesinosDisponiblesView(InterfaceSubViews):
    def __init__(self, root,user, estilo,notificationService):
        self.notificationService=notificationService
        self.root = root
        self.user=user
        self.win = tk.Toplevel(root)
        self.estilo = estilo
        self.titulo = 'Campesinos Disponibles'
        self.win.title(self.titulo)
        self.win.geometry('420x320')
        self.win.config(bg=self.estilo.colorFondo())
        tk.Label(
            self.win,
            text='👨‍🌾 Campesinos disponibles',
            bg=self.estilo.colorFondo(),
            fg=self.estilo.colorLetra(),
            font=('Arial', 18, 'bold')
        ).pack(pady=8)
        self.listbox = tk.Listbox(
            self.win,
            width=60,
            fg=estilo.colorFondo(),
            bg=estilo.colorLetra()
        )
        self.listbox.pack(pady=6, expand=True)
        self.cargarCampesinos()
        self.listbox.bind("<Double-1>", self.verInventarioCampesino)

        tk.Button(
            self.win,
            text='Actualizar',
            fg=self.estilo.colorFondo(),
            bg=self.estilo.colorLetra(),
            command=self.cargarCampesinos
        ).pack(pady=6)

        tk.Button(
            self.win,
            text='Cerrar',
            fg=self.estilo.colorFondo(),
            bg=self.estilo.colorLetra(),
            command=self.botonCerrar
        ).pack(pady=6)
        self.bloquearRoot()   



    def cargarCampesinos(self):
        self.listbox.delete(0, tk.END)
        self.campesinos = obtenerCampesinosConCultivos()
        if not self.campesinos:
            self.listbox.insert(tk.END, "No hay campesinos con cultivos disponibles.")
            return

        for c in self.campesinos:
            email = c.get("email", "")
            cantidad_cultivos = len(c.get("cultivos", []))

            # Obtener nombre desde usuarios.json
            usuario_info = obtener_usuario_por_email(email)
            nombre = usuario_info.get("nombre", email) if usuario_info else email

            texto = f"{nombre} ({email}) | {cantidad_cultivos} cultivo(s)"
            self.listbox.insert(tk.END, texto)



    def verInventarioCampesino(self, event):
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un campesino para ver su inventario.")
            return
        index = seleccion[0]
        campesino = self.campesinos[index]
        from controlador.controladorSubVistas import ControladorSubVistas
        controlador = ControladorSubVistas(None,self.root,self.user,None,campesino,None,self.estilo,self.notificationService)
        controlador.open_inventario_campesino_view()          
        self.win.destroy()
                  