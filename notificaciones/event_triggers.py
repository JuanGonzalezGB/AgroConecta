# notificaciones/event_triggers.py
# Generador de eventos que envían notificaciones usando NotificationService

def notificar_nuevo_pedido(notification_service, campesino_nombre, pedido_id, restaurante_nombre):
    titulo = "Nuevo Pedido Recibido"
    mensaje = f"Tienes un nuevo pedido #{pedido_id} del restaurante {restaurante_nombre}."
    notification_service.notificar(campesino_nombre, titulo, mensaje)


def notificar_pedido_aceptado(notification_service, restaurante_nombre, pedido_id, estado):
    titulo = "Estado de Pedido"
    mensaje = f"El pedido #{pedido_id} ha sido {estado}."
    notification_service.notificar(restaurante_nombre, titulo, mensaje)


def notificar_asignado_delivery(notification_service, delivery_nombre, pedido_id):
    titulo = "Pedido Asignado"
    mensaje = f"Se te ha asignado el pedido #{pedido_id}."
    notification_service.notificar(delivery_nombre, titulo, mensaje)


def notificar_cambio_estado(notification_service, usuario_nombre, pedido_id, nuevo_estado):
    titulo = "Actualización de Pedido"
    mensaje = f"El pedido #{pedido_id} cambió a estado: {nuevo_estado}."
    notification_service.notificar(usuario_nombre, titulo, mensaje)


def notificar_pago_confirmado(notification_service, campesino_nombre, pedido_id):
    titulo = "Pago Confirmado"
    mensaje = f"El pago del pedido #{pedido_id} ha sido confirmado."
    notification_service.notificar(campesino_nombre, titulo, mensaje)
