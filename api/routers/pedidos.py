from fastapi import APIRouter, Depends, Query, Response, status

from api.dependencias import requiere_permiso, usuario_actual
from api.esquemas import (
    AsignarIn, DomiciliarioOut, EstadoIn, EventoOut, MotivoIn, PedidoIn, PedidoOut,
)
from servicios import pedidos

router = APIRouter(tags=["Pedidos"])


@router.post("/pedidos", response_model=PedidoOut, status_code=status.HTTP_201_CREATED,
             summary="Crear pedido (restaurante)")
def crear(datos: PedidoIn, usuario: dict = Depends(requiere_permiso("realizar_compra"))):
    return pedidos.crear_pedido(usuario, datos.email_campesino, datos.cultivo, datos.cantidad)


@router.get("/pedidos", response_model=list[PedidoOut], summary="Mis pedidos (según mi rol)")
def listar(estado: str | None = Query(None, description="Filtra por estado, p. ej. CREADO"),
           usuario: dict = Depends(usuario_actual)):
    return pedidos.listar(usuario, estado.upper() if estado else None)


@router.get("/pedidos/{id_pedido}", response_model=PedidoOut)
def consultar(id_pedido: str, usuario: dict = Depends(usuario_actual)):
    return pedidos.obtener(usuario, id_pedido)


@router.get("/pedidos/{id_pedido}/historial", response_model=list[EventoOut])
def historial(id_pedido: str, usuario: dict = Depends(usuario_actual)):
    return pedidos.historial(usuario, id_pedido)


@router.get("/pedidos/{id_pedido}/qr", response_class=Response,
            responses={200: {"content": {"image/png": {}}}}, summary="QR del pedido (PNG)")
def qr(id_pedido: str, usuario: dict = Depends(usuario_actual)):
    return Response(content=pedidos.qr_png(usuario, id_pedido), media_type="image/png")


@router.post("/pedidos/{id_pedido}/aceptar", response_model=PedidoOut, summary="Aceptar (campesino)")
def aceptar(id_pedido: str, usuario: dict = Depends(usuario_actual)):
    return pedidos.aceptar(usuario, id_pedido)


@router.post("/pedidos/{id_pedido}/asignar", response_model=PedidoOut, summary="Asignar domiciliario (campesino)")
def asignar(id_pedido: str, datos: AsignarIn, usuario: dict = Depends(usuario_actual)):
    return pedidos.asignar_delivery(usuario, id_pedido, datos.email_delivery)


@router.post("/pedidos/{id_pedido}/estado", response_model=PedidoOut,
             summary="Cambiar estado (ACEPTADO, RECHAZADO, CANCELADO, EN_CAMINO, ENTREGADO)")
def cambiar_estado(id_pedido: str, datos: EstadoIn, usuario: dict = Depends(usuario_actual)):
    return pedidos.cambiar_estado(usuario, id_pedido, datos.estado, datos.motivo)


@router.post("/pedidos/{id_pedido}/cancelar", response_model=PedidoOut)
def cancelar(id_pedido: str, datos: MotivoIn | None = None, usuario: dict = Depends(usuario_actual)):
    return pedidos.cancelar(usuario, id_pedido, datos.motivo if datos else "")


@router.get("/domiciliarios", response_model=list[DomiciliarioOut], summary="Domiciliarios disponibles")
def domiciliarios(usuario: dict = Depends(usuario_actual)):
    return pedidos.listar_domiciliarios(usuario)
