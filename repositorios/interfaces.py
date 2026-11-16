"""Contratos de la capa de repositorios.

El resto de la aplicación depende solo de estas interfaces. Los métodos devuelven y
reciben ``dict`` (el mismo formato que usaba la app con documentos), de modo que
vistas y controladores no conocen el ORM ni el motor de base de datos.
"""
from abc import ABC, abstractmethod


class UsuarioRepository(ABC):
    @abstractmethod
    def crear(self, datos: dict) -> dict:
        """Crea un usuario. ``DuplicadoError`` si el email ya existe."""

    @abstractmethod
    def obtener_por_email(self, email: str) -> dict | None: ...

    @abstractmethod
    def listar(self) -> list[dict]: ...

    @abstractmethod
    def listar_por_roles(self, roles_ids: list[str]) -> list[dict]:
        """Usuarios que tienen alguno de los roles indicados."""

    @abstractmethod
    def guardar(self, datos: dict) -> dict:
        """Crea o actualiza (por email). Si trae ``roles`` los reemplaza."""

    @abstractmethod
    def actualizar_password(self, email: str, password_hash: str) -> bool: ...

    @abstractmethod
    def establecer_roles(self, email: str, roles_ids: list[str]) -> bool: ...

    @abstractmethod
    def eliminar(self, email: str) -> bool: ...


class RolRepository(ABC):
    @abstractmethod
    def listar(self) -> list[dict]: ...

    @abstractmethod
    def obtener(self, rol_id: str) -> dict | None: ...

    @abstractmethod
    def crear(self, rol: dict) -> dict:
        """``DuplicadoError`` si el id ya existe."""

    @abstractmethod
    def guardar(self, rol: dict) -> dict:
        """Crea o reemplaza el rol (incluidos sus permisos)."""

    @abstractmethod
    def actualizar(self, rol_id: str, datos: dict) -> bool: ...

    @abstractmethod
    def eliminar(self, rol_id: str) -> bool: ...

    @abstractmethod
    def agregar_permiso(self, rol_id: str, categoria: str, permiso: dict) -> bool:
        """False si el permiso ya estaba en esa categoría. ``NoEncontradoError`` si no hay rol."""

    @abstractmethod
    def quitar_permiso(self, permiso_id: str) -> list[str]:
        """Quita el permiso de todos los roles. Devuelve los ids de roles afectados."""

    @abstractmethod
    def renombrar_permiso(self, permiso_id: str, nuevo_nombre: str) -> int: ...

    @abstractmethod
    def permisos_de_roles(self, roles_ids: list[str]) -> list[str]:
        """Ids de permiso (sin duplicados, ordenados) concedidos por esos roles."""


class CultivoRepository(ABC):
    @abstractmethod
    def listar(self, email_campesino: str) -> list[dict]: ...

    @abstractmethod
    def listar_todos(self) -> dict[str, list[dict]]:
        """{email_campesino: [cultivos]} (incluye campesinos sin cultivos)."""

    @abstractmethod
    def agregar_o_sumar(self, email_campesino: str, nombre: str, cantidad: int, precio: float) -> dict:
        """Si el cultivo existe suma la cantidad y actualiza el precio; si no, lo crea."""

    @abstractmethod
    def reemplazar(self, email_campesino: str, cultivos: list[dict]) -> None: ...

    @abstractmethod
    def eliminar(self, email_campesino: str, nombre: str) -> bool: ...

    @abstractmethod
    def actualizar_cantidad(self, email_campesino: str, nombre: str, cantidad: int) -> bool: ...

    @abstractmethod
    def descontar_stock(self, email_campesino: str, nombre: str, cantidad: int) -> bool:
        """Descuento atómico; False si no hay stock suficiente."""


class PedidoRepository(ABC):
    @abstractmethod
    def crear(self, pedido: dict) -> dict: ...

    @abstractmethod
    def obtener(self, id_pedido: str) -> dict | None: ...

    @abstractmethod
    def listar(self, restaurante_email: str | None = None, campesino_email: str | None = None,
               delivery_email: str | None = None, estado: str | None = None) -> list[dict]: ...

    @abstractmethod
    def actualizar(self, pedido: dict, estado_esperado: str | None = None) -> dict:
        """Persiste estado, domiciliario y los eventos nuevos del historial.

        Si se indica ``estado_esperado`` y el pedido ya cambió de estado, lanza
        ``ConflictoError`` (evita que dos clientes pisen la misma transición).
        """


class NotificacionRepository(ABC):
    @abstractmethod
    def guardar(self, data: dict) -> dict: ...

    @abstractmethod
    def listar(self, destinatario: str, solo_no_leidas: bool = False) -> list[dict]: ...

    @abstractmethod
    def listar_todas(self) -> list[dict]: ...

    @abstractmethod
    def marcar_como_leidas(self, destinatario: str) -> int: ...
