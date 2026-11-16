from sqlalchemy import select, update

from repositorios._base import SQLAlchemyRepo
from repositorios.interfaces import NotificacionRepository
from repositorios.modelos import Notificacion, ahora_str


def _a_dict(n: Notificacion) -> dict:
    return {
        "destinatario": n.destinatario,
        "titulo": n.titulo,
        "mensaje": n.mensaje,
        "leido": n.leido,
        "fecha_hora": n.fecha_hora,
        "mostrar_inmediatamente": n.mostrar_inmediatamente,
    }


class SQLAlchemyNotificacionRepository(SQLAlchemyRepo, NotificacionRepository):
    def guardar(self, data: dict) -> dict:
        with self._session() as s:
            n = Notificacion(
                destinatario=data["destinatario"],
                titulo=data.get("titulo", ""),
                mensaje=data.get("mensaje", ""),
                leido=False,
                fecha_hora=ahora_str(),
                mostrar_inmediatamente=data.get("mostrar_inmediatamente", True),
            )
            s.add(n)
            s.flush()
            return _a_dict(n)

    def listar(self, destinatario: str, solo_no_leidas: bool = False) -> list[dict]:
        with self._session() as s:
            q = select(Notificacion).where(Notificacion.destinatario == destinatario).order_by(Notificacion.id)
            if solo_no_leidas:
                q = q.where(Notificacion.leido.is_(False))
            return [_a_dict(n) for n in s.scalars(q).all()]

    def listar_todas(self) -> list[dict]:
        with self._session() as s:
            return [_a_dict(n) for n in s.scalars(select(Notificacion).order_by(Notificacion.id)).all()]

    def marcar_como_leidas(self, destinatario: str) -> int:
        with self._session() as s:
            res = s.execute(
                update(Notificacion)
                .where(Notificacion.destinatario == destinatario, Notificacion.leido.is_(False))
                .values(leido=True)
            )
            return res.rowcount
