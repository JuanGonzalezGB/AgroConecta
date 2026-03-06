import tkinter as tk
from diccionarios import TEMAS
import modelo.saveConfig
from controlador.controladorTemas import ControladorTemas
import logging
logger = logging.getLogger(__name__)

class SelecTema:
    def __init__(self, root, estilo):
        self.estilo = estilo    
        self.root = root
        #self.root.geometry("320x220")
        self.root.geometry("")
        self.frame = tk.Frame(root,bg=estilo.colorFondo(), padx=20, pady=20)
        self.frame.config(bg=self.estilo.colorFondo())
        self.frame.pack(fill='both', expand=True)         
        self.controladorTema= ControladorTemas(self.frame,self.root,self.estilo)   
        tk.Label(self.frame, text="Elegir modo de colores",bg= self.estilo.colorFondo(),fg= self.estilo.colorTitulo(),font=('Arial',18,'bold')).pack(pady=10)
        self.tipo = tk.StringVar(value=self.traduz())
        opciones = list(TEMAS.keys())
        menusito = tk.OptionMenu(self.frame, self.tipo, *opciones, command=self.prever)
        menusito.config(
            bg=estilo.colorFondo(),
            fg=estilo.colorLetra(),
            highlightbackground=estilo.colorLetraH(),
            highlightcolor=estilo.colorFondoH(),
            activebackground=estilo.colorLetra(),
            activeforeground=estilo.colorFondo()            
            )
        menusito.pack(fill='x')
        tk.Button(self.frame, text='Aceptar',bg=estilo.colorLetra(),fg=estilo.colorFondo(), command=self.submit).pack(fill='x', pady=7)
        tk.Button(self.frame, text='Cancelar',bg=estilo.colorLetra(),fg=estilo.colorFondo(), command=self.back).pack(fill='x',pady=7) 

    def traduz(self):
        codigoANombre = {v: k for k, v in TEMAS.items()} 
        return codigoANombre.get(modelo.saveConfig.cargar(), 'Oscuro')  
    def prever(self,args):
        tipito = TEMAS.get(self.tipo.get(), "dark")
        self.controladorTema.aplicarTema(tipito)    
    def submit(self):
        tipito = TEMAS.get(self.tipo.get(), "dark")
        self.controladorTema.aceptarTema(tipito)
    def back(self):   
        logger.info('\t\tOPERACION CANCELADA')
        from controlador.controladorVistas import ControladorVistas
        self.controlador = ControladorVistas(self.frame,self.root,None,None,self.estilo,None)        
        self.controlador.open_main()