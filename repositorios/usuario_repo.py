from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from repositorios._base import SQLAlchemyRepo
from repositorios.errores import DuplicadoError, NoEncontradoError
from repositorios.interfaces import UsuarioRepository
from repositorios.modelos import Rol, RolPermiso, Usuario, UsuarioRol

CAMPOS_OPCIONALES = ("telefono", "direccion", "fecha_nacimiento", "nit", "tipo_vehiculo")


def _permisos_por_rol(s) -> dict[str, set[str]]:
    mapa: dict[str, set[str]] = {}
    for rol_id, permiso_id in s.execute(select(RolPermiso.rol_id, RolPermiso.permiso_id)):
        mapa.setdefault(rol_id, set()).add(permiso_id)
    return mapa


def _a_dict(u: Usuario, permisos_rol: dict[str, set[str]]) -> dict:
    roles = [ur.rol_id for ur in u.roles]
    permisos: set[str] = set()
    for r in roles:
        permisos |= permisos_rol.get(r, set())
    d = {
        "nombre": u.nombre,
        "email": u.email,
        "password": u.password_hash,
        "tipo": u.tipo,
        "roles": roles,
        "permisos": sorted(permisos),
    }
    for campo in CAMPOS_OPCIONALES:
        valor = getattr(u, campo)
        if valor is not None:
            d[campo] = valor
    return d


def _asignar_roles(s, u: Usuario, roles_ids: list[str]) -> None:
    ids = list(dict.fromkeys(roles_ids))  # sin duplicados, conserva orden
    existentes = set(s.scalars(select(Rol.id).where(Rol.id.in_(ids))).all()) if ids else set()
    faltan = [r for r in ids if r not in existentes]
    if faltan:
        raise NoEncontradoError(f"Roles inexistentes: {faltan}")
    u.roles.clear()
    s.flush()  # evita colisión de PK al re-insertar el mismo (usuario, rol)
    for r in ids:
        u.roles.append(UsuarioRol(rol_id=r))


class SQLAlchemyUsuarioRepository(SQLAlchemyRepo, UsuarioRepository):
    def crear(self, datos: dict) -> dict:
        with self._session() as s:
            u = Usuario(
                email=datos["email"],
                nombre=datos.get("nombre", ""),
                password_hash=datos.get("password", ""),
                tipo=datos["tipo"],
                **{c: datos.get(c) for c in CAMPOS_OPCIONALES},
            )
            s.add(u)
            try:
                s.flush()
            except IntegrityError as e:
                raise DuplicadoError("Ya existe un usuario con ese email.") from e
            _asignar_roles(s, u, datos.get("roles", []))
            s.flush()
            s.refresh(u)
            return _a_dict(u, _permisos_por_rol(s))

    def obtener_por_email(self, email: str) -> dict | None:
        with self._session() as s:
            u = s.scalar(select(Usuario).where(Usuario.email == email))
            return _a_dict(u, _permisos_por_rol(s)) if u else None

    def listar(self) -> list[dict]:
        with self._session() as s:
            mapa = _permisos_por_rol(s)
            return [_a_dict(u, mapa) for u in s.scalars(select(Usuario).order_by(Usuario.id)).all()]

    def listar_por_roles(self, roles_ids: list[str]) -> list[dict]:
        if not roles_ids:
            return []
        with self._session() as s:
            mapa = _permisos_por_rol(s)
            q = (select(Usuario).join(UsuarioRol).where(UsuarioRol.rol_id.in_(list(roles_ids)))
                 .distinct().order_by(Usuario.id))
            return [_a_dict(u, mapa) for u in s.scalars(q).all()]

    def guardar(self, datos: dict) -> dict:
        with self._session() as s:
            u = s.scalar(select(Usuario).where(Usuario.email == datos["email"]))
            if u is None:
                u = Usuario(email=datos["email"], nombre="", password_hash="", tipo=datos.get("tipo", "otros"))
                s.add(u)
            if "nombre" in datos:
                u.nombre = datos["nombre"]
            if "password" in datos:
                u.password_hash = datos["password"]
            if "tipo" in datos:
                u.tipo = datos["tipo"]
            for c in CAMPOS_OPCIONALES:
                if c in datos:
                    setattr(u, c, datos[c])
            s.flush()
            if "roles" in datos:
                # Roles borrados entre la lectura y el guardado se descartan en silencio.
                vigentes = set(s.scalars(select(Rol.id)).all())
                _asignar_roles(s, u, [r for r in datos["roles"] if r in vigentes])
            s.flush()
            s.refresh(u)
            return _a_dict(u, _permisos_por_rol(s))

    def actualizar_password(self, email: str, password_hash: str) -> bool:
        with self._session() as s:
            u = s.scalar(select(Usuario).where(Usuario.email == email))
            if u is None:
                return False
            u.password_hash = password_hash
            return True

    def establecer_roles(self, email: str, roles_ids: list[str]) -> bool:
        with self._session() as s:
            u = s.scalar(select(Usuario).where(Usuario.email == email))
            if u is None:
                return False
            _asignar_roles(s, u, roles_ids)
            return True

    def eliminar(self, email: str) -> bool:
        with self._session() as s:
            u = s.scalar(select(Usuario).where(Usuario.email == email))
            if u is None:
                return False
            s.delete(u)
            return True
