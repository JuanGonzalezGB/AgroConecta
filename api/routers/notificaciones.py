from fastapi import APIRouter, Depends, Query

from api.dependencias import usuario_actual
from api.esquemas import NotificacionOut
from servicios import notificaciones

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("", response_model=list[NotificacionOut])
def listar(solo_no_leidas: bool = Query(False), usuario: dict = Depends(usuario_actual)):
    return notificaciones.listar(usuario, solo_no_leidas)


@router.post("/leer", summary="Marcar todas como leídas")
def marcar_leidas(usuario: dict = Depends(usuario_actual)):
    return {"marcadas": notificaciones.marcar_leidas(usuario)}
