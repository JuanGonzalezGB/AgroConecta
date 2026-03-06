import tkinter as tk
from diccionarios import TIPOSUSUARIOS, LLAVESFORMUSUARIOS
import logging
logger = logging.getLogger(__name__)
class Registro:
    def __init__(self, root, estilo):
        self.estilo = estilo
        self.root = root
        self.frame = tk.Frame(root,bg=estilo.colorFondo(), padx=10, pady=10)
        self.frame.pack(fill='both', expand=True)
        self.user=None
        tk.Label(self.frame, text='Registro',bg=estilo.colorFondo(),fg=estilo.colorTitulo(), font=('Arial',16,'bold')).pack(pady=6)
        tk.Label(self.frame, text='Rol primario:',bg=self.estilo.colorFondo(),fg=self.estilo.colorTitulo()).pack(anchor='w')
        self.tipo = tk.StringVar(value='Campesino')
        opciones = list(TIPOSUSUARIOS.keys())
        menusito = tk.OptionMenu(self.frame, self.tipo, *opciones, command=self.build_form)
        menusito.config(bg=estilo.colorFondo(),fg=estilo.colorLetra(),highlightbackground=estilo.colorLetraH(),highlightcolor=estilo.colorFondoH(),activebackground=estilo.colorLetra(),activeforeground=estilo.colorFondo())
        menusito.pack(fill='x')

        self.form_frame = tk.Frame(self.frame,background=estilo.colorFondo()); self.form_frame.pack(fill='both', expand=True, pady=6)

        self.fields = {}
        self.build_form('Campesino')

        tk.Button(self.frame, text='Registrar',bg=self.estilo.colorFondo(),fg=self.estilo.colorLetra(), command=self.submit).pack(fill='x', anchor="s",pady=6)
        tk.Button(self.frame, text='Volver',bg=self.estilo.colorFondo(),fg=self.estilo.colorLetra(), command=self.back).pack(fill='x',anchor="s",pady=6)

    def build_form(self, tipo):
        logger.info('tipo '+ self.tipo.get()+' seleccionado.')
        logger.debug('destruyendo formulario anterior...')
        try:
            for w in self.form_frame.winfo_children():
                w.destroy()
            logger.info('Formulario destruido.')
        except:
            logger.error('NO SE PUDO DESTRUIR FORMULARIO')
        self.fields = {}
        opciones = list(LLAVESFORMUSUARIOS.get(tipo)) 
        self.root.geometry("")
        keys=[*opciones]
        logger.debug('generando nuevo formulario...')
        try:
            for k in keys:
                tk.Label(self.form_frame, text=k.replace('_',' ').capitalize()+':',bg=self.estilo.colorFondo(),fg=self.estilo.colorTitulo()).pack(anchor='w')
                e = tk.Entry(self.form_frame,fg=self.estilo.colorFondo(),bg=self.estilo.colorLetra(), width=40); e.pack(fill='x',anchor='w')
                self.fields[k] = e
            logger.info('Formulario Generado Correctamente.')
        except:
            logger.error('NO SE PUDO GENERAR FORMULARIO!')
    def submit(self):
        from controlador.controladorRegis import ControladorRegis
        logger.debug('intentando registrar usuario nuevo...')
        self.controlador = ControladorRegis(self.fields,self.frame,self.root,None,self.tipo.get(),self.estilo)        
        self.controlador.submitUsr()      

    def back(self):        
        from controlador.controladorVistas import ControladorVistas
        self.controlador = ControladorVistas(self.frame,self.root,self.user,None,self.estilo,None)        
        self.controlador.open_main()
