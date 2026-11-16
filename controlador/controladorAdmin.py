from modelo.CRU import cargarUsuarios, guardarUsuarios
from modelo.rolesModel import (
    cargar_roles, guardar_roles
)
from auth.permisos import require_permission
from diccionarios import ROLES_INICIALES,PERMISOS_CATEGORIAS
import logging
logger = logging.getLogger(__name__)


class ControladorAdmin():
    def __init__(self,user,root,notificationService):
        self.user = user
        self.root= root
        self.notificationService=notificationService

    # -------- Roles --------
    @require_permission("gestionar_roles")
    def obtener_roles(self,*,user):
        return cargar_roles()
    
    @require_permission("gestionar_roles")
    def agregar_nuevo_rol(self, id_rol, nombre, *, user):

        roles = cargar_roles()

        if any(r["id"] == id_rol for r in roles):
            return False, "Ya existe un rol con ese ID"

        nuevo = {
            "id": id_rol,
            "nombre": nombre,
            "permisos": {"lectura": [], "escritura": [], "eliminacion": [], "administrativo": [], "otros": []},
            "vista": "open_generica"
        }

        roles.append(nuevo)
        guardar_roles(roles)

        logger.info(f"Rol '{id_rol}' creado por {user.get('nombre')}.")
        return True, "Rol creado correctamente"

    @require_permission("gestionar_roles")
    def actualizar_nombre_rol(self, rol_id, nuevo_nombre, *, user):

        if not nuevo_nombre:
            return False, "El nombre del rol no puede estar vacío"

        roles = cargar_roles()
        for r in roles:
            if r["id"] == rol_id:
                r["nombre"] = nuevo_nombre
                guardar_roles(roles)
                logger.info(f"Nombre del rol '{rol_id}' actualizado a '{nuevo_nombre}' por {user.get('nombre')}.")
                return True, "Nombre del rol actualizado"
        return False, "Rol no encontrado"

    
    @require_permission("gestionar_roles")
    def eliminar_rol_por_id(self, rol_id, *, user):
        # No se pueden eliminar roles protegidos
        if self.es_rol_protegido(rol_id):
            return False, f"No se puede eliminar el rol protegido '{rol_id}'"

        # 1) verificar si existe
        roles = cargar_roles()
        if not any(r["id"] == rol_id for r in roles):
            return False, "Rol no existe"

        # 2) eliminar del JSON de roles
        roles = [r for r in roles if r["id"] != rol_id]
        guardar_roles(roles)

        # 3) eliminar de todos los usuarios
        data = cargarUsuarios()
        cambios = 0
        for grupo, lista in data.items():
            for u in lista:
                if rol_id in u.get("roles", []):
                    u["roles"].remove(rol_id)
                    cambios += 1

        if cambios > 0:
            guardarUsuarios(data)

        logger.info(f"Rol '{rol_id}' eliminado y removido de {cambios} usuarios por {user.get('nombre')}.")
        return True, f"Rol eliminado. Usuarios afectados: {cambios}"


    # -------- Permisos --------
    @require_permission("gestionar_roles")
    def obtener_permisos(self,*,user):
        roles = cargar_roles()

        permisos_unicos = {}

        for r in roles:
            permisos = r.get("permisos", {})
            if isinstance(permisos, dict):
                for lista in permisos.values():
                    for p in lista:
                        if isinstance(p, str):  # convertir string a dict visible
                            permisos_unicos[p] = {"id": p, "nombre": p}
                        else:
                            permisos_unicos[p["id"]] = p

        return list(permisos_unicos.values())


    @require_permission("gestionar_roles")
    @require_permission("gestionar_permisos")
    def agregar_permiso_a_rol(self, id_perm, nombre, rol_id, *, user):
        from modelo.rolesModel import agregar_permiso_a_rol as modelo_agregar_permiso

        permiso = {"id": id_perm, "nombre": nombre}

        categoria = self.categoria_por_prefijo(nombre)

        exito, msg = modelo_agregar_permiso(rol_id, permiso, categoria)
        return exito, msg

    
    @require_permission("gestionar_permisos")
    @require_permission("gestionar_roles")
    def eliminar_permiso_global(self, permiso_id, *, user):
        """
        Elimina un permiso de todos los roles y del JSON global.
        No permite borrar permisos protegidos de sus roles protegidos.
        """
        from modelo.rolesModel import eliminar_permiso_de_rol
        import logging
        logger = logging.getLogger(__name__)

        # Construir set de permisos protegidos
        permisos_protegidos = set()
        for rol in ROLES_INICIALES:
            rol_id = rol["id"]
            for cat, perms in rol["permisos"].items():
                for p in perms:
                    if isinstance(p, str):
                        permisos_protegidos.add((rol_id, p))
                    elif isinstance(p, dict):
                        permisos_protegidos.add((rol_id, p["id"]))

        # Revisar si el permiso está protegido en algún rol protegido
        for rol_id, pid in permisos_protegidos:
            if pid == permiso_id:
                logger.warning(f"Intento de eliminar permiso protegido '{permiso_id}' en rol '{rol_id}'")
                return False, f"No se puede eliminar el permiso protegido '{permiso_id}' del rol '{rol_id}'"

        # Si no es protegido, eliminar globalmente
        exito, msg = eliminar_permiso_de_rol(permiso_id)
        if exito:
            logger.info(f"Permiso '{permiso_id}' eliminado globalmente")
        else:
            logger.warning(f"Error eliminando permiso '{permiso_id}': {msg}")

        return exito, msg

    # -------- Permisos adicionales para edición --------
    @require_permission("gestionar_roles")
    @require_permission("gestionar_permisos")
    def roles_del_permiso(self, permiso_id, *, user):
        """
        Devuelve la lista de roles que tienen asignado un permiso dado,
        excluyendo el rol 'admin'.
        """
        roles = self.obtener_roles(user=user)
        roles_visibles = [r for r in roles if r["id"] != "admin"]
        roles_con_permiso = []

        for rol in roles_visibles:
            for categoria, permisos in rol.get("permisos", {}).items():
                # Normalizar: permisos pueden ser strings o dicts
                for p in permisos:
                    if isinstance(p, str) and p == permiso_id:
                        roles_con_permiso.append({"id": rol["id"], "nombre": rol["nombre"]})
                        break
                    elif isinstance(p, dict) and p.get("id") == permiso_id:
                        roles_con_permiso.append({"id": rol["id"], "nombre": rol["nombre"]})
                        break

        return roles_con_permiso

    def es_permiso_protegido(self, permiso_id):
        """Determina si un permiso pertenece a algún rol inicial"""
        for r in ROLES_INICIALES:
            for cat in r.get("permisos", {}).values():
                for p in cat:
                    p_id = p["id"] if isinstance(p, dict) else p
                    if p_id == permiso_id:
                        return True
        return False

    @require_permission("gestionar_permisos")
    def editar_permiso(self, permiso_id, nuevo_nombre, roles_ids, *, user):
        """
        Edita el nombre de un permiso y asigna el permiso a los roles indicados.
        Respeta los permisos protegidos de roles protegidos.
        Reasigna el permiso a la categoría correcta según el prefijo del nombre.
        """
        roles = cargar_roles()
        mensajes = []

        for rol in roles:
            rol_id = rol["id"]
            permisos = rol.get("permisos", {})

            # Eliminar cualquier aparición previa del permiso en este rol (salvo si es original protegido)
            for cat, lista in permisos.items():
                nueva_lista = []
                for p in lista:
                    p_dict = p if isinstance(p, dict) else {"id": p, "nombre": p}
                    if p_dict["id"] == permiso_id:
                        # Bloquear eliminación solo si es rol protegido y es permiso original
                        if self.es_rol_protegido(rol_id) and self.permiso_original_del_rol(rol_id, permiso_id):
                            mensajes.append(
                                f"No se puede quitar el permiso '{permiso_id}' del rol protegido '{rol_id}'"
                            )
                            nueva_lista.append(p_dict)
                        # si no está protegido como original, omitimos (lo eliminamos)
                    else:
                        nueva_lista.append(p_dict)
                permisos[cat] = nueva_lista

            # Solo agregar el permiso si el rol está seleccionado
            if rol_id in roles_ids:
                # Determinar categoría según el NOMBRE (nuevo_nombre), no por id
                cat = self.categoria_por_prefijo(nuevo_nombre)
                nuevo_perm = {"id": permiso_id, "nombre": nuevo_nombre}

                # Evitar duplicados en la categoría destino
                if not any(p.get("id") == permiso_id for p in permisos.get(cat, [])):
                    permisos.setdefault(cat, []).append(nuevo_perm)

        guardar_roles(roles)

        if mensajes:
            return False, "\n".join(mensajes)
        return True, "Permiso editado correctamente"

        
    def obtener_lista_roles(self, *, user):
        roles = self.obtener_roles(user=user)
        return [r for r in roles if r["id"].lower() != "admin"]


    def obtener_lista_permisos(self, *, user):
        return self.obtener_permisos(user=user)
    
    def obtener_ids_permisos_de_rol(self, rol_id):
        roles = cargar_roles()

        for rol in roles:
            if rol["id"] == rol_id:
                permisos = []
                for cat, lista in rol.get("permisos", {}).items():
                    for p in lista:
                        if isinstance(p, dict): 
                            permisos.append(p["id"])
                        else:
                            permisos.append(p)
                return permisos

        return []

    @require_permission("gestionar_roles")
    def editar_rol(self, rol_id, nuevos_permisos, *, user):
        """
        Actualiza los permisos de un rol (lista de ids).
        - No permite quitar permisos originales definidos en ROLES_INICIALES para ese rol protegido.
        - Preserva categoría si el permiso ya existía en el rol.
        - Para permisos nuevos, decide categoría por el prefijo del NOMBRE visible.
        """
        roles = cargar_roles()

        rol = next((r for r in roles if r["id"] == rol_id), None)
        if not rol:
            return False, f"Rol '{rol_id}' no encontrado"

        # permisos originales desde el diccionario inicial (protegidos para este rol)
        permisos_protegidos = self.obtener_ids_permisos_de_rol_desde_inicial(rol_id)

        # Validar intento de eliminar permisos protegidos (solo si el rol es protegido)
        if self.es_rol_protegido(rol_id):
            for p in permisos_protegidos:
                if p not in nuevos_permisos:
                    return False, f"No se puede quitar el permiso protegido '{p}' del rol '{rol_id}'"

        # Determinar lista de categorías a usar: preferir las del rol existente,
        # si no existen usar las globales en diccionarios.PERMISOS_CATEGORIAS
        categorias_existentes = list(rol.get("permisos", {}).keys())
        if not categorias_existentes:
            categorias_existentes = list(PERMISOS_CATEGORIAS)

        permisos_nuevos_dict = {cat: [] for cat in categorias_existentes}

        # Para cada permiso id solicitado, intentar:
        #  1) si ya existía en el rol, conservar su categoría
        #  2) si no, decidir categoría por prefijo del NOMBRE visible
        for pid in nuevos_permisos:
            nombre = self.obtener_nombre_permiso(pid) if hasattr(self, "obtener_nombre_permiso") else pid

            # 1) buscar en las categorias actuales del rol
            encontrado = False
            for cat, lista in rol.get("permisos", {}).items():
                for p in lista:
                    p_id = p["id"] if isinstance(p, dict) else p
                    if p_id == pid:
                        permisos_nuevos_dict.setdefault(cat, []).append({"id": pid, "nombre": nombre})
                        encontrado = True
                        break
                if encontrado:
                    break

            if encontrado:
                continue

            # 2) no estaba en el rol: decidir categoría por el prefijo del nombre
            cat_destino = self.categoria_por_prefijo(nombre)
            if cat_destino not in permisos_nuevos_dict:
                permisos_nuevos_dict[cat_destino] = []
            permisos_nuevos_dict[cat_destino].append({"id": pid, "nombre": nombre})

        # Guardar y retornar
        rol["permisos"] = permisos_nuevos_dict
        guardar_roles(roles)
        return True, "Rol actualizado correctamente"

    def categoria_por_prefijo(self, texto):
        t = texto.lower()
        if t.startswith(("ver_", "leer_")):
            return "lectura"
        elif t.startswith(("agregar_", "realizar_", "vender_")):
            return "escritura"
        elif t.startswith(("eliminar_", "borrar_", "quitar_")):
            return "eliminacion"
        elif t.startswith(("gestionar_", "reportesver_", "reportes_ver_")):
            return "administrativo"
        return "otros"
    def obtener_permisos_protegidos(self):
        # Buscar el rol admin dentro de ROLES_INICIALES
        rol_admin = next((rol for rol in ROLES_INICIALES if rol["id"] == "admin"), None)

        if not rol_admin:
            return []

        permisos_protegidos = []

        # recorrer categorías del rol admin
        for categoria, lista in rol_admin["permisos"].items():
            for permiso in lista:
                permisos_protegidos.append(permiso["id"])

        return permisos_protegidos
    def obtener_nombre_permiso(self, permiso_id):
        """
        Devuelve el nombre visible del permiso buscando en la lista global de permisos.
        Si no está, retorna el mismo permiso_id como fallback.
        Usa self.user (instancia del controlador) para llamar a obtener_permisos.
        """
        try:
            permisos = self.obtener_permisos(user=self.user)
        except Exception:
            # Si por alguna razón obtener_permisos necesita otro contexto, evitar crash y fallback
            permisos = []

        for p in permisos:
            if isinstance(p, dict) and p.get("id") == permiso_id:
                return p.get("nombre", permiso_id)
            # por seguridad, manejar si el permiso almacenado fuera string (aunque no debería)
            if isinstance(p, str) and p == permiso_id:
                return p

        # fallback: devolver id si no encontramos nombre
        return permiso_id


    def clasificar_permisos(self, lista_ids):
        """
        Recibe una lista de IDs de permisos y construye la estructura por categorías
        esperada por tus roles.json, usando el nombre visible obtenido por
        obtener_nombre_permiso() y la función categoria_por_prefijo().
        """
        # usar la lista oficial de categorías si está definida en diccionarios o en la variable local
        try:
            categorias = {cat: [] for cat in PERMISOS_CATEGORIAS}
        except Exception:
            categorias = {"lectura": [], "escritura": [], "eliminacion": [], "administrativo": [], "otros": []}

        for pid in lista_ids:
            nombre = self.obtener_nombre_permiso(pid)
            cat = self.categoria_por_prefijo(nombre)
            categorias.setdefault(cat, []).append({"id": pid, "nombre": nombre})

        return categorias
    def obtener_ids_permisos_de_rol_desde_inicial(self, rol_id):
        """Permisos originales (protegidos) del rol desde ROLES_INICIALES."""
        rol = next((r for r in ROLES_INICIALES if r["id"] == rol_id), None)
        if not rol:
            return []
        permisos = rol.get("permisos", {})
        lista = []
        for l in permisos.values():
            for p in l:
                lista.append(p["id"])
        return lista

    def permiso_original_del_rol(self, rol_id, permiso_id):
        """Retorna True si el permiso formaba parte del rol originalmente (en ROLES_INICIALES)."""
        return permiso_id in self.obtener_ids_permisos_de_rol_desde_inicial(rol_id)

    def es_rol_protegido(self, rol_id):
        """Solo los que están definidos en ROLES_INICIALES son protegidos."""
        return any(r["id"] == rol_id for r in ROLES_INICIALES)

        
    
    