import logging
from datetime import datetime
from conect.mongoConnection import MongoConnection  # <-- tu import correcto

logger = logging.getLogger(__name__)

class NotificationRepository:

    def __init__(self):
        try:
            self.mongo = MongoConnection()
            self.db = self.mongo.get_database()
            self.notificaciones_col = self.db["notificaciones"]
        except Exception as e:
            logger.critical(f"No se pudo conectar a MongoDB para notificaciones: {e}")
            raise e

    def guardar(self, data):
        """Agrega fecha y hora y guarda la notificación en MongoDB"""
        try:
            data["fecha_hora"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["leido"] = False  # por defecto
            self.notificaciones_col.insert_one(data)
            logger.info(f"Notificación guardada en MongoDB: {data}")
        except Exception as e:
            logger.error(f"Error guardando notificación en MongoDB: {e}")

    def cargar(self, usuario):
        """Devuelve solo notificaciones de un usuario"""
        try:
            notis = list(self.notificaciones_col.find({"destinatario": usuario}, {"_id": 0}))
            return notis
        except Exception as e:
            logger.error(f"Error cargando notificaciones de {usuario} desde MongoDB: {e}")
            return []

    def cargar_todas(self):
        """Devuelve todas las notificaciones sin filtrar"""
        try:
            notis = list(self.notificaciones_col.find({}, {"_id": 0}))
            return notis
        except Exception as e:
            logger.error(f"Error cargando todas las notificaciones desde MongoDB: {e}")
            return []

    def marcar_como_leidas(self, usuario):
        """Marca todas las notificaciones de un usuario como leídas"""
        try:
            result = self.notificaciones_col.update_many(
                {"destinatario": usuario},
                {"$set": {"leido": True}}
            )
            logger.info(f"Notificaciones de {usuario} marcadas como leídas en MongoDB ({result.modified_count} actualizadas)")
        except Exception as e:
            logger.error(f"Error marcando notificaciones como leídas en MongoDB: {e}")