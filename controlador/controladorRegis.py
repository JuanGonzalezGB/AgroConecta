from tkinter import messagebox
from modelo.CRU import cargarCultivos, guardarCultivos
from auth.permisos import require_permission
from auth.seguridad import hash_contrasena
from modelo.CRUD import crearCultivo, crearUsuario
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
        tipo = self.tipo
        if not self.validar_formulario():
            return        
        data = {k: e.get() for k, e in self.fields.items()}
        
        # Encriptar la contraseña antes de crear el usuario
        data["password"] = hash_contrasena(data["password"])
        
        exito, agregar = crearUsuario(tipo, data)
        if exito:
            logger.info('nuevo usuario registrado.')
            messagebox.showinfo("Éxito", agregar)
        else:
            logger.warning('error al registrar usuario.')
            messagebox.showerror("Error", agregar)
        self.back() 

    @require_permission("agregar_cultivo")
    def submitCultivo(self,*,user):
        cultivo = dict(self.fields)  
        exito, agregar = crearCultivo(self.user, cultivo)
        if exito:
            logger.info('cultivo agregado correctamente.')
            messagebox.showinfo("Éxito", agregar)
        else:
            logger.warning('error al agregar cultivo.')
            messagebox.showerror("Error", agregar)

    @require_permission("eliminar_cultivo")        
    def eliminarCultivo(self,nombre_cultivo,*,user):
        """
        Elimina un cultivo por nombre para el usuario dado.
        Retorna (exito: bool, mensaje: str)
        """
        #self.nombreCultivo = nombre_cultivo.strip().lower()
        email_usuario = user.get("email")
        if not email_usuario:
            logger.error("Usuario sin email al intentar eliminar cultivo")
            return False, "Usuario inválido"

        cultivos_data = cargarCultivos()
        cultivos_usuario = cultivos_data.get(email_usuario, [])

        # Buscar y eliminar cultivo
        cultivo_encontrado = False
        for i, c in enumerate(cultivos_usuario):
            if c.get("nombre") == nombre_cultivo.strip().lower():
                cultivo_encontrado = True
                cultivos_usuario.pop(i)
                logger.info(f"Cultivo '{nombre_cultivo}' eliminado para {email_usuario}")
                break

        if not cultivo_encontrado:
            logger.warning(f"Intento de eliminar cultivo inexistente '{nombre_cultivo}' para {email_usuario}")
            return False, f"No se encontró el cultivo '{nombre_cultivo}'"

        # Guardar cambios
        cultivos_data[email_usuario] = cultivos_usuario
        try:
            guardarCultivos(cultivos_data)
            return True, f"Cultivo '{nombre_cultivo}' eliminado correctamente."
        except Exception as e:
            logger.error(f"No se pudo guardar cultivos después de eliminar '{nombre_cultivo}' para {email_usuario}: {e}")
            return False, f"No se pudo eliminar el cultivo: {e}"


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