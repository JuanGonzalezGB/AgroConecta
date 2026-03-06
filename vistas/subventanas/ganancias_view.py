import tkinter as tk
from vistas.subventanas.interfaceSubViews import InterfaceSubViews

class GananciasView(InterfaceSubViews):
    def __init__(self, root, estilo,notificationService):
        self.root = root
        self.notificationService=notificationService
        self.estilo = estilo
        self.win = tk.Toplevel(root)
        self.titulo = 'Ganancias'
        self.win.title(self.titulo)
        #self.win.geometry('360x240')
        self.win.geometry('')
        self.win.config(bg=self.estilo.colorFondo())
        tk.Label(self.win, text='💰 Ganancias (simulado)',bg= self.estilo.colorFondo(),fg= self.estilo.colorLetra(), font=('Arial',14,'bold')).pack(pady=8)
        tk.Label(self.win, text='Total acumulado: $2.500.000',bg= self.estilo.colorFondo(),fg= self.estilo.colorLetra()).pack(pady=6)
        tk.Button(self.win, text='Cerrar',fg=self.estilo.colorFondo(),bg=self.estilo.colorLetra(), command=self.botonCerrar).pack(pady=8)
        self.bloquearRoot()   