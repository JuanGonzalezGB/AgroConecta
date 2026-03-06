import tkinter as tk
from estilo import estiloFactory
import modelo.saveConfig
import logging
logger = logging.getLogger(__name__)

class ControladorTemas:
    def __init__(self,frame, root,estilo):
        self.frame = frame
        self.root = root
        self.estilo = estilo
    def aplicarTema(self, tipo):
        self.tipo = tipo
        estiloSel = estiloFactory.EstiloFactory.definirEstilo(self.tipo)
        estiloAux = estiloSel  
        logger.debug('aplicando tema: '+ self.tipo+'...')
        self.frame.config(bg=estiloAux.colorFondo())
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=estiloAux.colorFondo(), fg=estiloAux.colorTitulo())
            elif isinstance(widget, tk.Button):
                widget.config(bg=estiloAux.colorLetra(), fg=estiloAux.colorFondo())              
            elif isinstance(widget, tk.OptionMenu):
                widget.config(
                    bg=estiloAux.colorFondo(),
                    fg=estiloAux.colorLetra(),
                    highlightbackground=estiloAux.colorLetraH(),
                    highlightcolor=estiloAux.colorFondoH(),
                    activebackground=estiloAux.colorLetra(),
                    activeforeground=estiloAux.colorFondo()
                )
    def aceptarTema(self, tipo):
        logger.debug('intentando guardar tema: '+tipo+'...')
        from controlador.controladorVistas import ControladorVistas
        estiloSel = estiloFactory.EstiloFactory.definirEstilo(tipo)
        self.controlaVistas = ControladorVistas(self.frame,self.root,None,None,estiloSel,None)
        modelo.saveConfig.guardar(tipo)
        self.controlaVistas.open_main()