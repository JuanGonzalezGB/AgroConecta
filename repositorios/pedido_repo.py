from sqlalchemy import select
from sqlalchemy.orm import selectinload

from repositorios._base import SQLAlchemyRepo
from repositorios.errores import ConflictoError, DuplicadoError, NoEncontradoError
from repositorios.interfaces import PedidoRepository
from repositorios.modelos import Pedido, PedidoEvento, Usuario, ahora_str


def _a_dict(p: Pedido) -> dict:
    return {
        "id_pedido": p.id_pedido,
        "restaurante": p.restaurante.nombre,
        "restaurante_email": p.restaurante.email,
        "campesino": p.campesino.nombre,
        "campesino_email": p.campesino.email,
        "delivery": p.delivery.nombre if p.delivery else None,
        "delivery_email": p.delivery.email if p.delivery else None,
        "producto": p.producto,
        "cantidad": p.cantidad,
        "precio_total": p.precio_total,
        "estado": p.estado,
        "fecha": p.fecha,
        "info_producto": p.info_producto or {},
        "historial": [
            # 'fecha' se conserva porque la vista de historial lo lee con ese nombre.
            {"timestamp": e.timestamp, "fecha": e.timestamp, "evento": e.evento, "detalle": e.detalle}
            for e in p.eventos
        ],
        "qr_base64": p.qr_base64,
    }


def _usuario_id(s, email: str, rol: str) -> int:
    uid = s.scalar(select(Usuario.id).where(Usuario.email == email))
    if uid is None:
        raise NoEncontradoError(f"{rol} '{email}' no encontrado")
    return uid


_CARGAR = (selectinload(Pedido.eventos),)


class SQLAlchemyPedidoRepository(SQLAlchemyRepo, PedidoRepository):
    def crear(self, pedido: dict) -> dict:
        with self._session() as s:
            if s.get(Pedido, pedido["id_pedido"]):
                raise DuplicadoError(f"Ya existe el pedido {pedido['id_pedido']}")
            p = Pedido(
                id_pedido=pedido["id_pedido"],
                restaurante_id=_usuario_id(s, pedido["restaurante_email"], "Restaurante"),
                campesino_id=_usuario_id(s, pedido["campesino_email"], "Campesino"),
                delivery_id=(_usuario_id(s, pedido["delivery_email"], "Domiciliario")
                             if pedido.get("delivery_email") else None),
                producto=pedido.get("producto", ""),
                cantidad=pedido.get("cantidad", 0),
                precio_total=pedido.get("precio_total", 0),
                estado=pedido.get("estado", "CREADO"),
                info_producto=pedido.get("info_producto") or {},
                qr_base64=pedido.get("qr_base64"),
            )
            if pedido.get("fecha"):
                p.fecha = pedido["fecha"]
            for ev in pedido.get("historial", []):
                p.eventos.append(PedidoEvento(
                    timestamp=ev.get("timestamp") or ev.get("fecha") or ahora_str(),
                    evento=ev.get("evento", ""), detalle=ev.get("detalle", "")))
            s.add(p)
            s.flush()
            s.refresh(p)
            return _a_dict(p)

    def obtener(self, id_pedido: str) -> dict | None:
        with self._session() as s:
            p = s.scalar(select(Pedido).options(*_CARGAR).where(Pedido.id_pedido == id_pedido))
            return _a_dict(p) if p else None

    def listar(self, restaurante_email=None, campesino_email=None, delivery_email=None, estado=None) -> list[dict]:
        with self._session() as s:
            q = select(Pedido).options(*_CARGAR).order_by(Pedido.fecha, Pedido.id_pedido)
            for col, email in ((Pedido.restaurante_id, restaurante_email),
                               (Pedido.campesino_id, campesino_email),
                               (Pedido.delivery_id, delivery_email)):
                if email is not None:
                    q = q.where(col == s.scalar(select(Usuario.id).where(Usuario.email == email)))
            if estado is not None:
                q = q.where(Pedido.estado == estado)
            return [_a_dict(p) for p in s.scalars(q).all()]

    def actualizar(self, pedido: dict, estado_esperado: str | None = None) -> dict:
        with self._session() as s:
            p = s.scalar(select(Pedido).options(*_CARGAR).where(Pedido.id_pedido == pedido["id_pedido"]))
            if p is None:
                raise NoEncontradoError(f"Pedido {pedido['id_pedido']} no encontrado")
            if estado_esperado is not None and p.estado != estado_esperado:
                raise ConflictoError(f"El pedido {p.id_pedido} ya está en estado {p.estado}")
            p.estado = pedido.get("estado", p.estado)
            email_delivery = pedido.get("delivery_email")
            p.delivery_id = _usuario_id(s, email_delivery, "Domiciliario") if email_delivery else None
            if "info_producto" in pedido:
                p.info_producto = pedido["info_producto"] or {}
            if pedido.get("qr_base64"):
                p.qr_base64 = pedido["qr_base64"]
            # El historial solo crece: se agregan los eventos que aún no están guardados.
            ya = len(p.eventos)
            for ev in pedido.get("historial", [])[ya:]:
                p.eventos.append(PedidoEvento(
                    timestamp=ev.get("timestamp") or ev.get("fecha") or ahora_str(),
                    evento=ev.get("evento", ""), detalle=ev.get("detalle", "")))
            s.flush()
            s.refresh(p)
            return _a_dict(p)
