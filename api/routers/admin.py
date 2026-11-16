"""Administración de roles y permisos dinámicos: cada operación exige su permiso de gestión."""
from fastapi import APIRouter, Depends, Response, status

from api.dependencias import requiere_permiso
from api.esquemas import (
    AsignarRolIn, PermisoIn, PermisoRename, RolIn, RolOut, RolUpdate, UsuarioOut,
)
from servicios import roles

router = APIRouter(prefix="/admin", tags=["Administración (roles y permisos)"])

_roles = Depends(requiere_permiso("gestionar_roles"))
_permisos = Depends(requiere_permiso("gestionar_permisos"))
_usuarios = Depends(requiere_permiso("gestionar_usuarios"))


@router.get("/roles", response_model=list[RolOut])
def listar_roles(actor: dict = _roles):
    return roles.listar_roles(actor)


@router.post("/roles", response_model=RolOut, status_code=status.HTTP_201_CREATED)
def crear_rol(datos: RolIn, actor: dict = _roles):
    return roles.crear_rol(actor, datos.id, datos.nombre, datos.vista)


@router.put("/roles/{rol_id}", response_model=RolOut)
def actualizar_rol(rol_id: str, datos: RolUpdate, actor: dict = _roles):
    return roles.actualizar_rol(actor, rol_id, datos.nombre, datos.vista)


@router.delete("/roles/{rol_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_rol(rol_id: str, actor: dict = _roles):
    roles.eliminar_rol(actor, rol_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/roles/{rol_id}/permisos", response_model=RolOut, status_code=status.HTTP_201_CREATED)
def agregar_permiso(rol_id: str, datos: PermisoIn, actor: dict = _permisos):
    return roles.agregar_permiso(actor, rol_id, datos.categoria, datos.id, datos.nombre)


@router.put("/permisos/{permiso_id}", summary="Renombrar un permiso en todos los roles")
def renombrar_permiso(permiso_id: str, datos: PermisoRename, actor: dict = _permisos):
    return {"roles_actualizados": roles.renombrar_permiso(actor, permiso_id, datos.nombre)}


@router.delete("/permisos/{permiso_id}", summary="Quitar un permiso de todos los roles")
def quitar_permiso(permiso_id: str, actor: dict = _permisos):
    return {"roles_afectados": roles.quitar_permiso(actor, permiso_id)}


@router.get("/usuarios", response_model=list[UsuarioOut])
def listar_usuarios(actor: dict = _usuarios):
    return roles.listar_usuarios(actor)


@router.post("/usuarios/{email}/roles", response_model=UsuarioOut)
def asignar_rol(email: str, datos: AsignarRolIn, actor: dict = _usuarios):
    return roles.asignar_rol(actor, email, datos.rol_id)


@router.delete("/usuarios/{email}/roles/{rol_id}", response_model=UsuarioOut)
def quitar_rol(email: str, rol_id: str, actor: dict = _usuarios):
    return roles.quitar_rol(actor, email, rol_id)
