from fastapi import APIRouter, Depends, Response, status

from api.dependencias import requiere_permiso
from api.esquemas import CampesinoOut, CultivoIn, CultivoOut
from servicios import cultivos

router = APIRouter(tags=["Cultivos e inventario"])


@router.get("/cultivos", response_model=list[CultivoOut], summary="Mis cultivos (campesino)")
def mis_cultivos(usuario: dict = Depends(requiere_permiso("ver_inventario"))):
    return cultivos.listar_mis_cultivos(usuario)


@router.post("/cultivos", response_model=CultivoOut, status_code=status.HTTP_201_CREATED,
             summary="Agregar cultivo (si existe, suma cantidad y actualiza el precio)")
def agregar(datos: CultivoIn, usuario: dict = Depends(requiere_permiso("agregar_cultivo"))):
    return cultivos.agregar_cultivo(usuario, datos.nombre, datos.cantidad, datos.precio)


@router.delete("/cultivos/{nombre}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(nombre: str, usuario: dict = Depends(requiere_permiso("eliminar_cultivo"))):
    cultivos.eliminar_cultivo(usuario, nombre)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/campesinos", response_model=list[CampesinoOut], summary="Campesinos con stock (restaurante)")
def campesinos(usuario: dict = Depends(requiere_permiso("ver_inventario"))):
    return cultivos.listar_campesinos(usuario)


@router.get("/campesinos/{email}/inventario", response_model=CampesinoOut)
def inventario(email: str, usuario: dict = Depends(requiere_permiso("ver_inventario"))):
    return cultivos.inventario_de_campesino(usuario, email)
