from vistas.subventanas.campesinoSubventanas.agregar_cultivos_view import AgregarCultivosView
from vistas.subventanas.restauranteSubventanas.campesinos_disponibles_view import CampesinosDisponiblesView
from vistas.subventanas.campesinoSubventanas.cultivos_view import CultivosView
from vistas.subventanas.ganancias_view import GananciasView
from vistas.subventanas.restauranteSubventanas.inventario_campesino_view import InventarioCampesinoView
from vistas.subventanas.deliverySubventanas.pedidos_delivery_view import PedidosDeliveryView
from vistas.subventanas.deliverySubventanas.pedidos_entrega_view import PedidosEntregaView
from vistas.subventanas.deliverySubventanas.pedidos_proceso_view import PedidosProcesoView
from vistas.subventanas.deliverySubventanas.pedidos_realizados_view import PedidosRealizadosView
from vistas.subventanas.deliverySubventanas.pedidos_view import PedidosView 
from vistas.subventanas.adminSubventanas.seleccion_roles_view import VentanaSeleccionRoles
from vistas.subventanas.adminSubventanas.ventana_editar_rol import VentanaEditarRol
from vistas.subventanas.ventana_notificaciones_view import VentanaNotificaciones
from vistas.subventanas.adminSubventanas.asignar_roles_view import AsignarRolesView
from vistas.subventanas.adminSubventanas.permisos_view import PermisosView
from vistas.subventanas.adminSubventanas.roles_view import RolesView
from vistas.subventanas.adminSubventanas.ventana_editar_permiso_view import VentanaEditarPermiso
from vistas.subventanas.restauranteSubventanas.mis_pedidos_restaurante_view import MisPedidosRestauranteView


import logging
logger = logging.getLogger(__name__)

class ControladorSubVistas:

    def __init__(self, frame, root, user,usuario_objetivo, campesino,rol, estilo, notificationService):
        self.campesino = campesino
        self.root = root
        self.estilo = estilo
        self.frame = frame
        self.usuario_objetivo=usuario_objetivo
        self.rol=rol
        self.user = user
        self.notificationService = notificationService

    def cambiar_subvista(self, nueva_vista):
        logger.debug('\tgenerando nueva ventana...')
        logger.debug('\tcreando nueva vista...')
        self.vista_actual = nueva_vista

    def open_campesinos_disponibles_view(self):
        vista = CampesinosDisponiblesView(self.root, self.user, self.estilo,self.notificationService)
        self.cambiar_subvista(vista)

    def open_cultivos_view(self):
        vista = CultivosView(self.root, self.user, self.estilo,self.notificationService)
        self.cambiar_subvista(vista)

    def open_ganancias_view(self):
        vista = GananciasView(self.root, self.estilo,self.notificationService)
        self.cambiar_subvista(vista)

    def open_pedidos_delivery_view(self):
        vista = PedidosDeliveryView(self.root, self.estilo)
        self.cambiar_subvista(vista)

    def open_pedidos_entrega_view(self):
        vista = PedidosEntregaView(self.root, self.estilo)
        self.cambiar_subvista(vista)

    def open_pedidos_proceso_view(self):
        vista = PedidosProcesoView(self.root, self.estilo)
        self.cambiar_subvista(vista)

    def open_pedidos_realizados_view(self):
        vista = PedidosRealizadosView(self.root, self.estilo)
        self.cambiar_subvista(vista)

    def open_pedidos_view(self):
        vista = PedidosView(self.root, self.estilo)
        self.cambiar_subvista(vista)

    def open_agregar_cultivos_view(self,nombreCultivo):
        vista = AgregarCultivosView(self.root, self.user,nombreCultivo, self.estilo,self.notificationService)
        self.cambiar_subvista(vista)
       

    def open_inventario_campesino_view(self):                
        vista = InventarioCampesinoView(self.root, self.user, self.campesino, self.estilo, self.notificationService)    
        self.cambiar_subvista(vista)

    def open_ventana_notificaciones_view(self):                
        vista = VentanaNotificaciones(self.root,self.user,self.estilo,self.notificationService)
        self.cambiar_subvista(vista)

    def open_roles_view(self):
        vista = RolesView(self.root,self.estilo,self.user,self.notificationService)
        self.cambiar_subvista(vista)
    
    def open_ventana_seleccion_roles_view(self):
        vista = VentanaSeleccionRoles(self.root, self.usuario_objetivo, self.estilo, self.user)
        self.cambiar_subvista(vista)

        
    def open_asignar_roles_view(self):
        vista = AsignarRolesView(self.root,self.user,self.usuario_objetivo,self.notificationService, self.estilo)
        self.cambiar_subvista(vista)  

    def open_permisos_view(self):
        vista = PermisosView(self.user,self.root, self.estilo,self.notificationService)
        self.cambiar_subvista(vista)

    
    def open_editar_permiso_view(self,permiso,callback_recargar):
        vista = VentanaEditarPermiso(self.root,self.user,permiso,self.estilo,self.notificationService,callback_recargar)
        self.cambiar_subvista(vista)

    def open_editar_rol_view(self,callback_recargar):
        vista = VentanaEditarRol(self.root, self.user, self.rol, self.estilo, self.notificationService,callback_recargar)        
        self.cambiar_subvista(vista)
    
    def open_mis_pedidos_restaurante_view(self):
        vista = MisPedidosRestauranteView(self.root,self.user, self.estilo)
        self.cambiar_subvista(vista)
    