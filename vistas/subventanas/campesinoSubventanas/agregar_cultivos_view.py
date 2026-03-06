import tkinter as tk
from tkinter import simpledialog, messagebox
from estilo.estilizador import Estilo
from vistas.subventanas.interfaceSubViews import InterfaceSubViews
import logging
logger = logging.getLogger(__name__)

class AgregarCultivosView(InterfaceSubViews):
    def __init__(self, root,user,nombreCultivo,estilo,notificationService):
        self.notificationService=notificationService
        self.user=user
        self.root = root
        self.estilo = estilo
        self.win = tk.Toplevel(root)
        self.titulo = 'Agregar Cultivos'
        self.win.title(self.titulo)
        self.win.geometry('300x200')
        self.win.config(bg=self.estilo.colorFondo())
        tk.Label(self.win, text='➕Agregar Cultivos',bg= self.estilo.colorFondo(),fg= self.estilo.colorLetra(), font=('Arial',18,'bold')).pack(pady=8)     
        tk.Label(self.win, text='Nombre Cultivo:',bg= self.estilo.colorFondo(),fg= self.estilo.colorLetra()).pack(anchor='w')   
        self.entryCultivo = tk.Entry(self.win,fg=self.estilo.colorFondo(),bg=self.estilo.colorLetra(), width=40)
        self.entryCultivo.pack(fill='x',anchor='w')               
        self.entryCultivo.bind('<Return>', lambda e: self.botonAgregar())
        self.entryCultivo.insert(0, nombreCultivo)
        tk.Button(self.win, text='Agregar',fg=self.estilo.colorFondo(),bg=self.estilo.colorLetra(), command=self.botonAgregar).pack(pady=6)            
        tk.Button(self.win, text='Cerrar',fg=self.estilo.colorFondo(),bg=self.estilo.colorLetra(), command=self.botonCerrar).pack(pady=6)
        self.bloquearRoot()   

    def botonAgregar(self):               
        nombre=self.entryCultivo.get().strip().lower()          
        cantidad = simpledialog.askinteger('Ingresar Numero','ingrese cantidad de '+nombre.capitalize())
        precio = simpledialog.askfloat('Ingresar Numero','ingrese valor unitario de '+nombre.capitalize())

        if not nombre or not cantidad or not precio:
            logger.warning('capa 8: no se ingresó información completa')
            messagebox.showerror("Error", "Ingrese Todos los datos")
            return            
        self.campos = {
            "nombre": nombre,
            "cantidad": cantidad,
            "precio": precio
        }

        from controlador.controladorRegis import ControladorRegis
        self.controlador = ControladorRegis(self.campos,None, self.root,self.user,None, self.estilo)
        logger.debug('intentando agregar cultivo...')
        self.controlador.submitCultivo(user=self.user)
        self.win.destroy()
                