"""API REST de AgroConecta.

Arranque:  uvicorn api.main:app --reload      (documentación en /docs)
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.routers import admin, auth, cultivos, notificaciones, pedidos
from modelo.inicializacion import inicializar_sistema
from servicios import errores

ESTADO_HTTP = {
    errores.ValidacionError: 422,
    errores.NoAutenticadoError: 401,
    errores.PermisoDenegadoError: 403,
    errores.NoEncontradoError: 404,
    errores.ConflictoError: 409,
}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    inicializar_sistema()  # tablas, roles iniciales y admin (idempotente)
    yield


app = FastAPI(
    title="AgroConecta API",
    version="1.0.0",
    description="Conecta campesinos, restaurantes y domiciliarios. La app de escritorio (Tkinter) "
                "usa los mismos servicios que esta API.",
    lifespan=lifespan,
)


@app.exception_handler(errores.ServicioError)
async def manejar_error_de_negocio(_request: Request, exc: errores.ServicioError):
    estado = next((c for t, c in ESTADO_HTTP.items() if isinstance(exc, t)), 400)
    cabeceras = {"WWW-Authenticate": "Bearer"} if estado == 401 else None
    return JSONResponse(status_code=estado, content={"detail": exc.mensaje, "codigo": exc.codigo}, headers=cabeceras)


for router in (auth.router, cultivos.router, pedidos.router, notificaciones.router, admin.router):
    app.include_router(router)


@app.get("/", tags=["Estado"])
def raiz():
    return {"servicio": "AgroConecta API", "docs": "/docs"}
