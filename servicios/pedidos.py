"""Ciclo de vida del pedido: crear, aceptar, asignar domiciliario, cambiar estado, historial y QR.

Reglas de autorización (además de los permisos dinámicos):
  - crear:               restaurante con permiso ``realizar_compra``
  - aceptar / rechazar:  el campesino dueño del pedido
  - asignar domiciliario el campesino dueño del pedido
  - en camino / entregado: el domiciliario asignado
  - cancelar:            el restaurante que lo creó o el campesino dueño
  - ver:                 participantes del pedido y administradores
"""
import base64

from modelo import pedidoModel as pm
from modelo import pedidos_utils
from repositorios import get_cultivo_repo, get_pedido_repo, get_usuario_repo
from repositorios.errores import ConflictoError as RepoConflicto
from servicios import notificaciones
from servicios.autorizacion import es_admin, exigir_permiso
from servicios.errores import (
    ConflictoError, NoEncontradoError, PermisoDenegadoError, ValidacionError,
)


# ---------- helpers ----------

def _cargar(id_pedido: str) -> dict:
    pedido = get_pedido_repo().obtener(id_pedido)
    if pedido is None:
        raise NoEncontradoError(f"Pedido {id_pedido} no encontrado.")
    return pedido


def _participa(actor: dict, pedido: dict) -> bool:
    return actor["email"] in (pedido["restaurante_email"], pedido["campesino_email"], pedido.get("delivery_email"))


def _exigir_ver(actor: dict, pedido: dict) -> None:
    if not (es_admin(actor) or _participa(actor, pedido)):
        raise PermisoDenegadoError("No participas en este pedido.")


def _exigir_rol_en_pedido(actor: dict, pedido: dict, campo_email: str, descripcion: str) -> None:
    if pedido.get(campo_email) != actor["email"]:
        raise PermisoDenegadoError(f"Solo {descripcion} puede realizar esta acción.")


def _devolver_stock(pedido: dict) -> None:
    """Al rechazar o cancelar, las unidades vuelven al inventario del campesino."""
    info = pedido.get("info_producto") or {}
    get_cultivo_repo().agregar_o_sumar(
        pedido["campesino_email"], pedido["producto"], pedido["cantidad"], info.get("precio", 0))


def _aplicar(id_pedido: str, autorizar, accion, *args) -> dict:
    """Lee, autoriza, aplica la transición del modelo y guarda con control de concurrencia."""
    pedido = _cargar(id_pedido)
    autorizar(pedido)
    estado_original = pedido["estado"]
    try:
        accion(pedido, *args)
    except pm.EstadoInvalidoError as e:
        raise ConflictoError(str(e)) from e
    try:
        return get_pedido_repo().actualizar(pedido, estado_esperado=estado_original)
    except RepoConflicto as e:
        raise ConflictoError(str(e)) from e


# ---------- operaciones ----------

def crear_pedido(restaurante: dict, email_campesino: str, nombre_cultivo: str, cantidad: int) -> dict:
    exigir_permiso(restaurante, "realizar_compra")
    if cantidad is None or cantidad <= 0:
        raise ValidacionError("La cantidad debe ser mayor que cero.")
    campesino = get_usuario_repo().obtener_por_email(email_campesino)
    if campesino is None or campesino["tipo"] != "campesinos":
        raise NoEncontradoError("Campesino no encontrado.")
    cultivo = next((c for c in get_cultivo_repo().listar(email_campesino)
                    if c["nombre"] == nombre_cultivo.strip().lower()), None)
    if cultivo is None:
        raise NoEncontradoError(f"El campesino no tiene el cultivo '{nombre_cultivo}'.")
    if not get_cultivo_repo().descontar_stock(email_campesino, cultivo["nombre"], cantidad):
        raise ConflictoError("Stock insuficiente.")
    try:
        pedido = pedidos_utils.registrar_pedido(restaurante, campesino, cultivo, cantidad)
    except Exception:
        get_cultivo_repo().agregar_o_sumar(email_campesino, cultivo["nombre"], cantidad, cultivo["precio"])
        raise
    notificaciones.nuevo_pedido(campesino["nombre"], pedido)
    notificaciones.notificar(restaurante["nombre"], "Compra realizada",
                             f"Pedido {pedido['id_pedido']} enviado a {campesino['nombre']}.")
    return pedido


def aceptar(actor: dict, id_pedido: str) -> dict:
    pedido = _aplicar(id_pedido, lambda p: _exigir_rol_en_pedido(actor, p, "campesino_email", "el campesino del pedido"),
                      pm.aceptar)
    notificaciones.cambio_estado(pedido["restaurante"], pedido)
    return pedido


def rechazar(actor: dict, id_pedido: str, motivo: str = "") -> dict:
    pedido = _aplicar(id_pedido, lambda p: _exigir_rol_en_pedido(actor, p, "campesino_email", "el campesino del pedido"),
                      pm.rechazar, motivo)
    _devolver_stock(pedido)
    notificaciones.cambio_estado(pedido["restaurante"], pedido)
    return pedido


def cancelar(actor: dict, id_pedido: str, motivo: str = "") -> dict:
    def autorizar(p):
        if actor["email"] not in (p["restaurante_email"], p["campesino_email"]):
            raise PermisoDenegadoError("Solo el restaurante o el campesino del pedido pueden cancelarlo.")
    pedido = _aplicar(id_pedido, autorizar, pm.cancelar, motivo)
    _devolver_stock(pedido)
    for nombre in {pedido["restaurante"], pedido["campesino"], pedido["delivery"]} - {None, actor["nombre"]}:
        notificaciones.cambio_estado(nombre, pedido)
    return pedido


def asignar_delivery(actor: dict, id_pedido: str, email_delivery: str) -> dict:
    domi = get_usuario_repo().obtener_por_email(email_delivery)
    if domi is None or "delivery" not in domi["roles"]:
        raise NoEncontradoError("Domiciliario no encontrado.")
    pedido = _aplicar(id_pedido, lambda p: _exigir_rol_en_pedido(actor, p, "campesino_email", "el campesino del pedido"),
                      pm.asignar_delivery, domi)
    notificaciones.notificar(domi["nombre"], "Pedido asignado", f"Se te asignó el pedido {pedido['id_pedido']}.")
    notificaciones.cambio_estado(pedido["restaurante"], pedido)
    return pedido


def _avanzar_delivery(actor: dict, id_pedido: str, accion) -> dict:
    pedido = _aplicar(id_pedido, lambda p: _exigir_rol_en_pedido(actor, p, "delivery_email", "el domiciliario asignado"),
                      accion)
    notificaciones.cambio_estado(pedido["restaurante"], pedido)
    notificaciones.cambio_estado(pedido["campesino"], pedido)
    return pedido


def marcar_en_camino(actor: dict, id_pedido: str) -> dict:
    return _avanzar_delivery(actor, id_pedido, pm.marcar_en_camino)


def marcar_entregado(actor: dict, id_pedido: str) -> dict:
    return _avanzar_delivery(actor, id_pedido, pm.marcar_entregado)


def cambiar_estado(actor: dict, id_pedido: str, nuevo_estado: str, motivo: str = "") -> dict:
    """Punto único para ``POST /pedidos/{id}/estado``; delega según el estado pedido."""
    nuevo_estado = (nuevo_estado or "").upper()
    if nuevo_estado == pm.ACEPTADO:
        return aceptar(actor, id_pedido)
    if nuevo_estado == pm.RECHAZADO:
        return rechazar(actor, id_pedido, motivo)
    if nuevo_estado == pm.CANCELADO:
        return cancelar(actor, id_pedido, motivo)
    if nuevo_estado == pm.EN_CAMINO:
        return marcar_en_camino(actor, id_pedido)
    if nuevo_estado == pm.ENTREGADO:
        return marcar_entregado(actor, id_pedido)
    if nuevo_estado == pm.ASIGNADO:
        raise ValidacionError("Para asignar un domiciliario usa la operación de asignación.")
    raise ValidacionError(f"Estado no válido: {nuevo_estado}")


# ---------- consultas ----------

def listar(actor: dict, estado: str | None = None) -> list[dict]:
    repo = get_pedido_repo()
    if es_admin(actor):
        return repo.listar(estado=estado)
    campo = {"restaurantes": "restaurante_email", "campesinos": "campesino_email",
             "deliverys": "delivery_email"}.get(actor["tipo"])
    if campo is None:
        return []
    return repo.listar(**{campo: actor["email"]}, estado=estado)


def obtener(actor: dict, id_pedido: str) -> dict:
    pedido = _cargar(id_pedido)
    _exigir_ver(actor, pedido)
    return pedido


def historial(actor: dict, id_pedido: str) -> list[dict]:
    return obtener(actor, id_pedido)["historial"]


def qr_png(actor: dict, id_pedido: str) -> bytes:
    pedido = obtener(actor, id_pedido)
    if not pedido.get("qr_base64"):
        raise NoEncontradoError("Este pedido no tiene QR.")
    return base64.b64decode(pedido["qr_base64"])


def listar_domiciliarios(actor: dict) -> list[dict]:
    if not (es_admin(actor) or actor["tipo"] == "campesinos"):
        raise PermisoDenegadoError("Solo campesinos y administradores pueden listar domiciliarios.")
    return [{"email": u["email"], "nombre": u["nombre"], "tipo_vehiculo": u.get("tipo_vehiculo")}
            for u in get_usuario_repo().listar() if "delivery" in u["roles"]]
