from tkinter import messagebox
from auth.permisos import require_permission
from diccionarios import TIPOSUSUARIOS
from servicios import autenticacion, cultivos
from servicios.errores import ServicioError
from auth.validaciones import *
import logging
logger = logging.getLogger(__name__)

class ControladorRegis:
    def __init__(self,fields,frame, root, user,tipo, estilo):
        self.user = user
        self.fields = fields
        self.root = root
        self.tipo = tipo
        self.estilo = estilo
        self.frame = frame
                
    def submitUsr(self):
        if not self.validar_formulario():
            return
        data = {k: e.get() for k, e in self.fields.items()}
        try:
            autenticacion.registrar(TIPOSUSUARIOS[self.tipo], data)
            logger.info('nuevo usuario registrado.')
            messagebox.showinfo("Éxito", "Registro guardado correctamente")
        except ServicioError as e:
            logger.warning('error al registrar usuario.')
            messagebox.showerror("Error", e.mensaje)
        self.back()

    @require_permission("agregar_cultivo")
    def submitCultivo(self, *, user):
        c = self.fields
        try:
            cultivos.agregar_cultivo(self.user, c["nombre"], c["cantidad"], c["precio"])
            logger.info('cultivo agregado correctamente.')
            messagebox.showinfo("Éxito", "Cultivo guardado correctamente.")
        except ServicioError as e:
            logger.warning('error al agregar cultivo.')
            messagebox.showerror("Error", e.mensaje)

    @require_permission("eliminar_cultivo")
    def eliminarCultivo(self, nombre_cultivo, *, user):
        """Elimina un cultivo por nombre. Retorna (exito: bool, mensaje: str)."""
        try:
            cultivos.eliminar_cultivo(user, nombre_cultivo)
            return True, f"Cultivo '{nombre_cultivo}' eliminado correctamente."
        except ServicioError as e:
            return False, e.mensaje

    def back(self):        
        from controlador.controladorVistas import ControladorVistas
        self.controlador = ControladorVistas(self.frame,self.root,None,None,self.estilo, None)        
        self.controlador.open_main()    
        
    def validar_formulario(self):
        errores = []
        erroresLog = []
        nombre = self.fields.get('nombre').get()
        if not validar_nombre(nombre):
            errores.append("El nombre no es válido (solo letras y espacios, mínimo 2).")
            erroresLog.append('NMB')
        email = self.fields.get('email').get()
        if not validar_email(email):
            errores.append("El correo electrónico no tiene un formato válido.")
            erroresLog.append('EML')
        password = self.fields.get('password').get()
        if not validar_contrasena(password):
            errores.append("La contraseña debe tener al menos 8 caracteres, incluyendo mayúscula, minúscula, número y símbolo.")
            erroresLog.append('CTS')
        if 'nit' in self.fields:
            nit = self.fields['nit'].get()
            if not validar_nit(nit):
                errores.append("El NIT debe tener entre 6 y 12 dígitos (puede incluir un guion).")
                erroresLog.append('NIT')
        telefono = self.fields.get('telefono').get()
        if not validar_telefono(telefono):
            errores.append("El teléfono debe tener entre 7 y 10 dígitos.")
            erroresLog.append('TEL')            
        if errores:
            logger.warning('Capa 8: no se cumplió especificación de formato \n\t'+ '\n\t'.join(erroresLog))
            messagebox.showerror("Error de validación", "\n".join(errores))
            return False
        return True