from sqlalchemy import select

from diccionarios import PERMISOS_CATEGORIAS
from repositorios._base import SQLAlchemyRepo
from repositorios.errores import DuplicadoError, NoEncontradoError
from repositorios.interfaces import RolRepository
from repositorios.modelos import Rol, RolPermiso


def _normalizar_permiso(p) -> dict:
    """Acepta 'permiso' (str) o {'id', 'nombre'} y devuelve siempre un dict."""
    if isinstance(p, dict):
        return {"id": p["id"], "nombre": p.get("nombre", p["id"])}
    return {"id": p, "nombre": p}


def _rol_a_dict(rol: Rol) -> dict:
    permisos = {cat: [] for cat in PERMISOS_CATEGORIAS}
    for rp in rol.permisos:
        permisos.setdefault(rp.categoria, []).append({"id": rp.permiso_id, "nombre": rp.nombre})
    return {"id": rol.id, "nombre": rol.nombre, "permisos": permisos, "vista": rol.vista or ""}


def _reemplazar_permisos(rol: Rol, permisos) -> None:
    """Reemplaza todos los permisos del rol. ``permisos`` es {categoria: [permiso, ...]}."""
    rol.permisos.clear()
    vistos = set()
    orden = 0
    for categoria, lista in (permisos or {}).items():
        for p in lista:
            p = _normalizar_permiso(p)
            if (categoria, p["id"]) in vistos:
                continue
            vistos.add((categoria, p["id"]))
            rol.permisos.append(
                RolPermiso(categoria=categoria, permiso_id=p["id"], nombre=p["nombre"], orden=orden)
            )
            orden += 1


class SQLAlchemyRolRepository(SQLAlchemyRepo, RolRepository):
    def listar(self) -> list[dict]:
        with self._session() as s:
            roles = s.scalars(select(Rol).order_by(Rol.id)).all()
            return [_rol_a_dict(r) for r in roles]

    def obtener(self, rol_id: str) -> dict | None:
        with self._session() as s:
            rol = s.get(Rol, rol_id)
            return _rol_a_dict(rol) if rol else None

    def crear(self, rol: dict) -> dict:
        with self._session() as s:
            if s.get(Rol, rol["id"]):
                raise DuplicadoError(f"Ya existe un rol con ID {rol['id']}")
            nuevo = Rol(id=rol["id"], nombre=rol.get("nombre", rol["id"]), vista=rol.get("vista", ""))
            _reemplazar_permisos(nuevo, rol.get("permisos"))
            s.add(nuevo)
            s.flush()
            return _rol_a_dict(nuevo)

    def guardar(self, rol: dict) -> dict:
        with self._session() as s:
            actual = s.get(Rol, rol["id"])
            if actual is None:
                actual = Rol(id=rol["id"], nombre=rol.get("nombre", rol["id"]), vista=rol.get("vista", ""))
                s.add(actual)
            else:
                actual.nombre = rol.get("nombre", actual.nombre)
                actual.vista = rol.get("vista", actual.vista)
            if "permisos" in rol:
                _reemplazar_permisos(actual, rol["permisos"])
            s.flush()
            return _rol_a_dict(actual)

    def actualizar(self, rol_id: str, datos: dict) -> bool:
        with self._session() as s:
            rol = s.get(Rol, rol_id)
            if rol is None:
                return False
            if "nombre" in datos:
                rol.nombre = datos["nombre"]
            if "vista" in datos:
                rol.vista = datos["vista"]
            if "permisos" in datos:
                _reemplazar_permisos(rol, datos["permisos"])
            return True

    def eliminar(self, rol_id: str) -> bool:
        with self._session() as s:
            rol = s.get(Rol, rol_id)
            if rol is None:
                return False
            s.delete(rol)  # cascade: rol_permisos; usuario_roles por ON DELETE CASCADE
            return True

    def agregar_permiso(self, rol_id: str, categoria: str, permiso: dict) -> bool:
        permiso = _normalizar_permiso(permiso)
        with self._session() as s:
            rol = s.get(Rol, rol_id)
            if rol is None:
                raise NoEncontradoError(f"Rol '{rol_id}' no encontrado")
            if any(rp.categoria == categoria and rp.permiso_id == permiso["id"] for rp in rol.permisos):
                return False
            siguiente = max((rp.orden for rp in rol.permisos), default=-1) + 1
            rol.permisos.append(
                RolPermiso(categoria=categoria, permiso_id=permiso["id"], nombre=permiso["nombre"], orden=siguiente)
            )
            return True

    def quitar_permiso(self, permiso_id: str) -> list[str]:
        with self._session() as s:
            filas = s.scalars(select(RolPermiso).where(RolPermiso.permiso_id == permiso_id)).all()
            afectados = sorted({f.rol_id for f in filas})
            for f in filas:
                s.delete(f)
            return afectados

    def renombrar_permiso(self, permiso_id: str, nuevo_nombre: str) -> int:
        with self._session() as s:
            filas = s.scalars(select(RolPermiso).where(RolPermiso.permiso_id == permiso_id)).all()
            for f in filas:
                f.nombre = nuevo_nombre
            return len(filas)

    def permisos_de_roles(self, roles_ids: list[str]) -> list[str]:
        if not roles_ids:
            return []
        with self._session() as s:
            ids = s.scalars(
                select(RolPermiso.permiso_id).where(RolPermiso.rol_id.in_(list(roles_ids))).distinct()
            ).all()
            return sorted(ids)
