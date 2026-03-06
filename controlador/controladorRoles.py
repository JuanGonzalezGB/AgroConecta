import logging
from modelo.rolesModel import cargar_roles, guardar_roles
from modelo.CRU import cargarUsuarios, guardarUsuarios

logger = logging.getLogger(__name__)

class ControladorRoles:
    def __init__(self):
        pass

    # ======================= ROLES CRUD =========================

    def obtener_roles(self):
        return cargar_roles()

    def crear_rol(self, nuevo_rol):
        roles = cargar_roles()
        if any(r["id"] == nuevo_rol["id"] for r in roles):
            return False, "Ya existe un rol con ese ID."

        roles.append(nuevo_rol)
        guardar_roles(roles)

        logger.info(f"Rol creado: {nuevo_rol}")
        return True, "Rol creado exitosamente."

    def actualizar_rol(self, id_rol, datos_actualizados):
        roles = cargar_roles()
        for i, r in enumerate(roles):
            if r["id"] == id_rol:
                roles[i] = datos_actualizados
                guardar_roles(roles)
                logger.info(f"Rol actualizado: {datos_actualizados}")
                return True, "Rol actualizado."
        return False, "No se encontró el rol."

    def eliminar_rol(self, id_rol):
        roles = cargar_roles()
        roles = [r for r in roles if r["id"] != id_rol]
        guardar_roles(roles)

        logger.info(f"Rol eliminado: {id_rol}")
        return True, "Rol eliminado exitosamente."

    # =================== ASIGNAR ROLES A USUARIO ==================

    def asignar_roles(self, email_usuario, roles_asignados):
        data = cargarUsuarios()
        roles = cargar_roles()

        # Unir permisos de todos los roles seleccionados
        permisos_finales = []
        for r in roles:
            if r["id"] in roles_asignados:
                permisos_finales.extend(r.get("permisos", []))  # ejemplo: ["inventario.ver", "reportes.leer"]

        permisos_finales = list(set(permisos_finales))  # eliminar duplicados

        encontrado = False
        for tipo, lista in data.items():
            for i, u in enumerate(lista):
                if u["email"] == email_usuario:

                    # Guardar roles y permisos
                    u["roles"] = roles_asignados  # ej ["campesino", "supervisor"]
                    u["permisos"] = permisos_finales  # ej ["inventario.ver","reportes.leer"]

                    data[tipo][i] = u
                    encontrado = True
                    break

            if encontrado:
                break

        if not encontrado:
            return False, "Usuario no encontrado."

        guardarUsuarios(data)
        logger.info(f"Roles asignados a {email_usuario}: {roles_asignados}")
        logger.info(f"Permisos generados: {permisos_finales}")

        return True, "Roles y permisos actualizados correctamente."

