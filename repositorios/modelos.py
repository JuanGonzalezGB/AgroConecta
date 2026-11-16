"""Modelos ORM (SQLAlchemy 2.x). Solo describen tablas; la lógica vive en los repositorios."""
from datetime import datetime

from sqlalchemy import (
    JSON, Boolean, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def ahora_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Base(DeclarativeBase):
    pass


class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    vista: Mapped[str] = mapped_column(String(100), default="")

    permisos: Mapped[list["RolPermiso"]] = relationship(
        back_populates="rol", cascade="all, delete-orphan", order_by="RolPermiso.orden"
    )


class RolPermiso(Base):
    """Un permiso concedido a un rol, dentro de una categoría (lectura, escritura, ...)."""
    __tablename__ = "rol_permisos"

    rol_id: Mapped[str] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    categoria: Mapped[str] = mapped_column(String(30), primary_key=True)
    permiso_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    orden: Mapped[int] = mapped_column(Integer, default=0)

    rol: Mapped[Rol] = relationship(back_populates="permisos")

    __table_args__ = (Index("ix_rol_permisos_permiso", "permiso_id"),)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    # campesinos | restaurantes | deliverys | admin  (mismas llaves que LLAVESUSUARIOS)
    tipo: Mapped[str] = mapped_column(String(30), index=True)
    telefono: Mapped[str | None] = mapped_column(String(30))
    direccion: Mapped[str | None] = mapped_column(String(255))
    fecha_nacimiento: Mapped[str | None] = mapped_column(String(30))  # campesino
    nit: Mapped[str | None] = mapped_column(String(30))               # restaurante
    tipo_vehiculo: Mapped[str | None] = mapped_column(String(60))     # domiciliario

    roles: Mapped[list["UsuarioRol"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan", order_by="UsuarioRol.rol_id"
    )
    cultivos: Mapped[list["Cultivo"]] = relationship(
        back_populates="campesino", cascade="all, delete-orphan", order_by="Cultivo.id"
    )


class UsuarioRol(Base):
    __tablename__ = "usuario_roles"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    rol_id: Mapped[str] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)

    usuario: Mapped[Usuario] = relationship(back_populates="roles")


class Cultivo(Base):
    __tablename__ = "cultivos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    campesino_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    cantidad: Mapped[int] = mapped_column(Integer, default=0)
    precio: Mapped[float] = mapped_column(Float, default=0)

    campesino: Mapped[Usuario] = relationship(back_populates="cultivos")

    __table_args__ = (UniqueConstraint("campesino_id", "nombre", name="uq_cultivo_campesino_nombre"),)


class Pedido(Base):
    __tablename__ = "pedidos"

    id_pedido: Mapped[str] = mapped_column(String(64), primary_key=True)
    restaurante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    campesino_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    delivery_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), index=True)
    producto: Mapped[str] = mapped_column(String(120), default="")
    cantidad: Mapped[int] = mapped_column(Integer, default=0)
    precio_total: Mapped[float] = mapped_column(Float, default=0)
    estado: Mapped[str] = mapped_column(String(30), index=True, default="CREADO")
    fecha: Mapped[str] = mapped_column(String(30), default=ahora_str)
    # Datos realmente flexibles del producto (siembra, cosecha, tipo de cultivo, ...)
    info_producto: Mapped[dict] = mapped_column(JSON, default=dict)
    qr_base64: Mapped[str | None] = mapped_column(Text)

    restaurante: Mapped[Usuario] = relationship(foreign_keys=[restaurante_id])
    campesino: Mapped[Usuario] = relationship(foreign_keys=[campesino_id])
    delivery: Mapped[Usuario | None] = relationship(foreign_keys=[delivery_id])
    eventos: Mapped[list["PedidoEvento"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan", order_by="PedidoEvento.id"
    )


class PedidoEvento(Base):
    """Historial inmutable del pedido (una fila por evento)."""
    __tablename__ = "pedido_eventos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pedido_id: Mapped[str] = mapped_column(ForeignKey("pedidos.id_pedido", ondelete="CASCADE"), index=True)
    timestamp: Mapped[str] = mapped_column(String(30), default=ahora_str)
    evento: Mapped[str] = mapped_column(String(60))
    detalle: Mapped[str] = mapped_column(Text, default="")

    pedido: Mapped[Pedido] = relationship(back_populates="eventos")


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # El código existente identifica al destinatario por nombre (no por email).
    destinatario: Mapped[str] = mapped_column(String(120), index=True)
    titulo: Mapped[str] = mapped_column(String(200))
    mensaje: Mapped[str] = mapped_column(Text)
    leido: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_hora: Mapped[str] = mapped_column(String(30), default=ahora_str)
    mostrar_inmediatamente: Mapped[bool] = mapped_column(Boolean, default=True)
