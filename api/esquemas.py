"""Esquemas Pydantic de entrada y salida."""
from typing import Literal

from pydantic import BaseModel, Field

TipoUsuario = Literal["campesino", "restaurante", "delivery"]


# ---------- auth ----------
class RegistroIn(BaseModel):
    tipo: TipoUsuario
    nombre: str
    email: str
    password: str
    telefono: str
    direccion: str | None = None
    fecha_nacimiento: str | None = None   # campesino
    nit: str | None = None                # restaurante
    tipo_vehiculo: str | None = None      # domiciliario

    model_config = {"json_schema_extra": {"example": {
        "tipo": "campesino", "nombre": "Carlos Campo", "email": "carlos@mail.com",
        "password": "Clave123!", "telefono": "3001112233", "direccion": "Vereda La Esperanza"}}}


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioOut(BaseModel):
    nombre: str
    email: str
    tipo: str
    roles: list[str]
    permisos: list[str]
    telefono: str | None = None
    direccion: str | None = None
    fecha_nacimiento: str | None = None
    nit: str | None = None
    tipo_vehiculo: str | None = None


# ---------- cultivos ----------
class CultivoIn(BaseModel):
    nombre: str
    cantidad: int = Field(gt=0)
    precio: float = Field(gt=0)


class CultivoOut(BaseModel):
    nombre: str
    cantidad: int
    precio: float


class CampesinoOut(BaseModel):
    email: str
    nombre: str
    direccion: str | None = None
    telefono: str | None = None
    cultivos: list[CultivoOut]


class DomiciliarioOut(BaseModel):
    email: str
    nombre: str
    tipo_vehiculo: str | None = None


# ---------- pedidos ----------
class PedidoIn(BaseModel):
    email_campesino: str
    cultivo: str
    cantidad: int = Field(gt=0)


class EventoOut(BaseModel):
    timestamp: str
    evento: str
    detalle: str


class PedidoOut(BaseModel):
    id_pedido: str
    estado: str
    restaurante: str
    restaurante_email: str
    campesino: str
    campesino_email: str
    delivery: str | None = None
    delivery_email: str | None = None
    producto: str
    cantidad: int
    precio_total: float
    fecha: str
    historial: list[EventoOut]


class AsignarIn(BaseModel):
    email_delivery: str


class EstadoIn(BaseModel):
    estado: str = Field(description="ACEPTADO, RECHAZADO, CANCELADO, EN_CAMINO o ENTREGADO")
    motivo: str = ""


class MotivoIn(BaseModel):
    motivo: str = ""


# ---------- notificaciones ----------
class NotificacionOut(BaseModel):
    destinatario: str
    titulo: str
    mensaje: str
    leido: bool
    fecha_hora: str


# ---------- administración ----------
class PermisoOut(BaseModel):
    id: str
    nombre: str


class RolOut(BaseModel):
    id: str
    nombre: str
    vista: str
    permisos: dict[str, list[PermisoOut]]


class RolIn(BaseModel):
    id: str
    nombre: str
    vista: str = "open_generica"


class RolUpdate(BaseModel):
    nombre: str | None = None
    vista: str | None = None


class PermisoIn(BaseModel):
    categoria: str
    id: str
    nombre: str | None = None


class PermisoRename(BaseModel):
    nombre: str


class AsignarRolIn(BaseModel):
    rol_id: str
