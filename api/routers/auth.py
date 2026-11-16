from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencias import usuario_actual
from api.esquemas import LoginIn, RegistroIn, TokenOut, UsuarioOut
from api.jwt_utils import crear_token
from servicios import autenticacion

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registro(datos: RegistroIn):
    """Crea una cuenta de campesino, restaurante o domiciliario."""
    payload = datos.model_dump(exclude={"tipo"}, exclude_none=True)
    return autenticacion.registrar(datos.tipo, payload)


@router.post("/login", response_model=TokenOut)
def login(datos: LoginIn):
    usuario = autenticacion.login(datos.email, datos.password)
    return TokenOut(access_token=crear_token(usuario["email"]))


@router.post("/token", response_model=TokenOut, include_in_schema=True, summary="Login con formulario (botón Authorize de /docs)")
def token(form: OAuth2PasswordRequestForm = Depends()):
    usuario = autenticacion.login(form.username, form.password)
    return TokenOut(access_token=crear_token(usuario["email"]))


@router.get("/me", response_model=UsuarioOut)
def me(usuario: dict = Depends(usuario_actual)):
    return autenticacion.publico(usuario)
