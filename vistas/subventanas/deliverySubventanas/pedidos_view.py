import tkinter as tk
from estilo.estilizador import Estilo
from vistas.subventanas.interfaceSubViews import InterfaceSubViews

class PedidosView(InterfaceSubViews):
    def __init__(self, root,estilo = Estilo):
        self.root = root
        self.estilo = estilo
        tipo='pendientes'
        self.win = tk.Toplevel(root)
        self.titulo = 'Pedidos -' + tipo.capitalize()
        self.win.title(self.titulo)
        self.win.geometry('380x300')
        self.win.config(bg=self.estilo.colorFondo())
        tk.Label(self.win, text=f'📦 Pedidos - {tipo.capitalize()}',bg= self.estilo.colorFondo(),fg= self.estilo.colorLetra(), font=('Arial',14,'bold')).pack(pady=8)
        tk.Listbox(self.win, fg=estilo.colorFondo(),bg=estilo.colorLetra(),width=50).pack(pady=6)
        tk.Button(self.win, text='Cerrar',fg=self.estilo.colorFondo(),bg=self.estilo.colorLetra(), command=self.botonCerrar).pack(pady=8)
        self.bloquearRoot()         