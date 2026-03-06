from tkinter import messagebox, simpledialog
from vistas import perfilView
from vistas.admin_view import AdminView
from vistas.selecTema import SelecTema
from vistas.campesino_view import CampesinoView
from vistas.delivery_view import DeliveryView
from vistas.registro import Registro
from vistas.restaurante_view import RestauranteView
from vistas.generica_view import GenericaView
from modelo.rolesModel import cargar_roles
import logging

logger = logging.getLogger(__name__)

class ControladorVistas:
    def __init__(self, frame, root, user, usuario_objetivo, estilo, notificationService):
        self.frame = frame
        self.root = root
        self.user = user
        self.usuario_objetivo = usuario_objetivo
        self.estilo = estilo
        self.notificationService = notificationService

    def abrir_vista_por_roles(self):
        """
        Abre la vista principal según los roles del usuario.
        Si hay varios roles, pregunta cuál desea abrir.
        Los roles creados por admin usan GenericaView.
        """
        from tkinter import simpledialog, messagebox

        roles_def = cargar_roles()

        # Extraemos los roles completos que tiene el usuario
        roles_usuario = [r for r in roles_def if r["id"] in self.user.get("roles", [])]

        if not roles_usuario:
            messagebox.showerror("Error", "No hay interfaz asociada a los roles del usuario.")
            return

        # Si solo hay un rol, abrir la vista directamente
        if len(roles_usuario) == 1:
            rol = roles_usuario[0]
            if rol["vista"] == "open_generica":
                self.open_generica(rol["id"])
            else:
                getattr(self, rol["vista"])()
            return

        # Si hay varios roles, preguntar al usuario cuál abrir
        titulos_disponibles = [r["nombre"] for r in roles_usuario]
        opciones = "\n".join([f"{i+1}. {titulo}" for i, titulo in enumerate(titulos_disponibles)])
        eleccion = simpledialog.askinteger(
            "Elegir rol",
            f"Tienes varios roles:\n{opciones}\n\nIngresa el número de la opción:"
        )

        if eleccion and 1 <= eleccion <= len(roles_usuario):
            rol_seleccionado = roles_usuario[eleccion - 1]
            if rol_seleccionado["vista"] == "open_generica":
                self.open_generica(rol_seleccionado["id"])
            else:
                getattr(self, rol_seleccionado["vista"])()
        else:
            messagebox.showwarning("Opción inválida", "No seleccionaste una opción válida.")


    def cambiar_vista(self, nueva_vista):
        if self.frame:
            logger.debug('\tdestruyendo vista anterior...')
            self.frame.destroy()  
        logger.debug('\tcreando nueva vista...')
        self.vista_actual = nueva_vista

    def open_generica(self, rol_id):
        roles_def = cargar_roles()
        rol = next((r for r in roles_def if r["id"] == rol_id), None)
        if not rol:
            return
        permisos_dict = {cat: [p["id"] for p in lista] for cat, lista in rol["permisos"].items()}
        from controlador.controladorAdmin import ControladorAdmin
        self.controlAdmin=ControladorAdmin(self.user,self.root,self.notificationService)
        permisos_protegidos = self.controlAdmin.obtener_ids_permisos_de_rol_desde_inicial(rol_id)

        vista = GenericaView(self.root, self.user, self.estilo, self.notificationService,
                            rol_id, permisos_dict, permisos_protegidos)        
        logger.debug(f'Abriendo GenericaView para rol: {rol_id}')
        self.cambiar_vista(vista)
        self.mostrarNotificaciones(vista)
        logger.info(f'GenericaView cargada correctamente')


    def open_main(self):
        from vistas.main_view import MainView
        vista = MainView(self.root, self.estilo, self.notificationService)
        logger.debug('Abriendo MainView')
        self.cambiar_vista(vista)
        logger.info('MainView cargado correctamente')

    def open_campesino(self):
        vista = CampesinoView(self.root, self.user, self.estilo, self.notificationService)
        logger.debug('Abriendo CampesinoView')
        self.cambiar_vista(vista)
        self.mostrarNotificaciones(vista)
        logger.info('CampesinoView cargado correctamente')

    def open_restaurante(self):
        vista = RestauranteView(self.root, self.user, self.estilo, self.notificationService)
        logger.debug('Abriendo RestauranteView')
        self.cambiar_vista(vista)
        self.mostrarNotificaciones(vista)
        logger.info('RestauranteView cargado correctamente')

    def open_delivery(self):
        vista = DeliveryView(self.root, self.user, self.estilo, self.notificationService)
        logger.debug('Abriendo DeliveryView')
        self.cambiar_vista(vista)
        self.mostrarNotificaciones(vista)
        logger.info('DeliveryView cargado correctamente')
    def open_admin(self):
        """
        Abre la vista de administración. No solicita usuario objetivo aquí.
        """
        vista = AdminView(self.root, self.user, self.usuario_objetivo, self.estilo, self.notificationService)
        logger.debug('abriendo AdminView')
        self.cambiar_vista(vista)
        self.mostrarNotificaciones(vista)
        logger.info('AdminView Cargado Correctamente')
        return vista

    def open_register(self):
        vista = Registro(self.root, self.estilo)
        logger.debug('Abriendo Registro')
        self.cambiar_vista(vista)
        logger.info('Registro cargado correctamente')

    def open_temas(self):
        vista = SelecTema(self.root, self.estilo)
        logger.debug('Abriendo SelecTema')
        self.cambiar_vista(vista)
        logger.info('SelecTema cargado correctamente')

    def openPerfil(self):
        vista = perfilView.PerfilView(self.root, self.user, self.estilo, self.notificationService)
        logger.debug('Abriendo PerfilView')
        self.cambiar_vista(vista)
        logger.info('PerfilView cargado correctamente')

    def mostrarNotificaciones(self, vista):
        from controlador.controladorInternas import ControladorInternas
        controlador = ControladorInternas(self.frame, self.root, self.user, self.estilo, vista, self.notificationService)
        controlador.open_internas()

    def open_pedidos_view(self):
        from vistas.subventanas.restauranteSubventanas.mis_pedidos_restaurante_view import MisPedidosRestauranteView
        vista = MisPedidosRestauranteView(self.root, self.user, self.estilo)        
        logger.debug('Abriendo MisPedidosRestauranteView')
        self.cambiar_vista(vista)
        logger.info('MisPedidosRestauranteView cargado correctamente')