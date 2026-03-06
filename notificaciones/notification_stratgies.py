from abc import ABC, abstractmethod

class NotificationStrategy(ABC):
    @abstractmethod
    def format_message(self, event_data: dict) -> str:
        pass


class NewOrderNotificationStrategy(NotificationStrategy):
    def format_message(self, event_data: dict) -> str:
        return f"Nuevo pedido #{event_data['order_id']} recibido de {event_data['restaurant_name']}"


class OrderStatusChangedStrategy(NotificationStrategy):
    def format_message(self, event_data: dict) -> str:
        return f"El pedido #{event_data['order_id']} cambió a estado: {event_data['new_status']}"


