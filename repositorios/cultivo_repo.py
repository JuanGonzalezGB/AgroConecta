from sqlalchemy import select, update

from repositorios._base import SQLAlchemyRepo
from repositorios.errores import NoEncontradoError
from repositorios.interfaces import CultivoRepository
from repositorios.modelos import Cultivo, Usuario


def _a_dict(c: Cultivo) -> dict:
    return {"nombre": c.nombre, "cantidad": c.cantidad, "precio": c.precio}


def _campesino(s, email: str) -> Usuario:
    u = s.scalar(select(Usuario).where(Usuario.email == email))
    if u is None:
        raise NoEncontradoError(f"Usuario '{email}' no encontrado")
    return u


class SQLAlchemyCultivoRepository(SQLAlchemyRepo, CultivoRepository):
    def listar(self, email_campesino: str) -> list[dict]:
        with self._session() as s:
            q = (select(Cultivo).join(Usuario, Cultivo.campesino_id == Usuario.id)
                 .where(Usuario.email == email_campesino).order_by(Cultivo.id))
            return [_a_dict(c) for c in s.scalars(q).all()]

    def listar_todos(self) -> dict[str, list[dict]]:
        with self._session() as s:
            data: dict[str, list[dict]] = {}
            q = select(Usuario.email, Cultivo).join(Cultivo, Cultivo.campesino_id == Usuario.id).order_by(Cultivo.id)
            for email, c in s.execute(q):
                data.setdefault(email, []).append(_a_dict(c))
            return data

    def agregar_o_sumar(self, email_campesino: str, nombre: str, cantidad: int, precio: float) -> dict:
        with self._session() as s:
            u = _campesino(s, email_campesino)
            c = s.scalar(select(Cultivo).where(Cultivo.campesino_id == u.id, Cultivo.nombre == nombre))
            if c is None:
                c = Cultivo(campesino_id=u.id, nombre=nombre, cantidad=cantidad, precio=precio)
                s.add(c)
            else:
                c.cantidad += cantidad
                c.precio = precio
            s.flush()
            return _a_dict(c)

    def reemplazar(self, email_campesino: str, cultivos: list[dict]) -> None:
        with self._session() as s:
            u = _campesino(s, email_campesino)
            actuales = {c.nombre: c for c in s.scalars(select(Cultivo).where(Cultivo.campesino_id == u.id)).all()}
            nuevos = {c["nombre"] for c in cultivos}
            for nombre, c in actuales.items():
                if nombre not in nuevos:
                    s.delete(c)
            for datos in cultivos:
                c = actuales.get(datos["nombre"])
                if c is None:
                    s.add(Cultivo(campesino_id=u.id, nombre=datos["nombre"],
                                  cantidad=datos.get("cantidad", 0), precio=datos.get("precio", 0)))
                else:
                    c.cantidad = datos.get("cantidad", c.cantidad)
                    c.precio = datos.get("precio", c.precio)

    def eliminar(self, email_campesino: str, nombre: str) -> bool:
        with self._session() as s:
            c = s.scalar(select(Cultivo).join(Usuario, Cultivo.campesino_id == Usuario.id)
                         .where(Usuario.email == email_campesino, Cultivo.nombre == nombre))
            if c is None:
                return False
            s.delete(c)
            return True

    def actualizar_cantidad(self, email_campesino: str, nombre: str, cantidad: int) -> bool:
        with self._session() as s:
            c = s.scalar(select(Cultivo).join(Usuario, Cultivo.campesino_id == Usuario.id)
                         .where(Usuario.email == email_campesino, Cultivo.nombre == nombre))
            if c is None:
                return False
            c.cantidad = cantidad
            return True

    def descontar_stock(self, email_campesino: str, nombre: str, cantidad: int) -> bool:
        with self._session() as s:
            u = s.scalar(select(Usuario.id).where(Usuario.email == email_campesino))
            if u is None:
                return False
            # UPDATE condicional: atómico incluso con varios clientes (Tkinter + API).
            res = s.execute(
                update(Cultivo)
                .where(Cultivo.campesino_id == u, Cultivo.nombre == nombre, Cultivo.cantidad >= cantidad)
                .values(cantidad=Cultivo.cantidad - cantidad)
            )
            return res.rowcount == 1
