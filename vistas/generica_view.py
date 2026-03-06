import tkinter as tk
from vistas.interfaceViewPerfiles import InterfaceViewsPerfiles

class GenericaView(InterfaceViewsPerfiles):
    def __init__(self, root, user, estilo, notificationService, rol_id, permisos_dict, permisos_protegidos=None):
        """
        :param permisos_dict: dict con las categorías como claves y listas de permisos,
                              ej. {"lectura": ["ver_inventario"], "escritura": ["agregar_cultivo"], ...}
        :param permisos_protegidos: lista de IDs de permisos protegidos dentro de este rol
        """
        self.root = root
        self.user = user
        self.estilo = estilo
        self.notificationService = notificationService
        self.rol_id = rol_id
        self.permisos_dict = permisos_dict
        self.permisos_protegidos = permisos_protegidos or []
        self.frame = tk.Frame(root, bg=self.estilo.colorFondo(), padx=10, pady=10)
        self.frame.pack(fill='both', expand=True)

        # Título dinámico
        tk.Label(
            self.frame,
            text=f'Rol: {self.rol_id} - Usuario: {user.get("nombre","-")}',
            bg=estilo.colorFondo(),
            fg=estilo.colorTitulo(),
            font=('Arial', 14, 'bold')
        ).pack(pady=6)

        # Crear botones agrupados por categoría
        for categoria, permisos in self.permisos_dict.items():
            if not permisos:
                continue  # omitimos categorías vacías

            # Título de categoría
            tk.Label(
                self.frame,
                text=f'{categoria.capitalize()}',
                bg=estilo.colorFondo(),
                fg=estilo.colorLetraH(),
                font=('Arial', 12, 'bold')
            ).pack(pady=(10, 2), anchor='w')

            # Botones de permisos
            for pid in permisos:
                color_fondo = estilo.colorFondoH() if pid in self.permisos_protegidos else estilo.colorLetra()
                color_letra = estilo.colorLetraH() if pid in self.permisos_protegidos else estilo.colorFondo()
                btn = tk.Button(
                    self.frame,
                    text=pid.replace("_", " ").capitalize(),
                    bg=color_fondo,
                    fg=color_letra,
                    command=lambda p=pid: self.accion_permiso(p)
                )
                btn.pack(fill='x', pady=2)

        # Botón de cerrar sesión
        tk.Button(
            self.frame, text='Cerrar sesión', bg=estilo.colorLetra(),
            fg=estilo.colorFondo(), command=self.cerrarSesion
        ).pack(pady=8)

        # Botón de perfil
        tk.Button(
            self.frame, text='👥 Perfil', bg=estilo.colorLetra(),
            fg=estilo.colorFondo(), command=self.openPerfil
        ).pack(anchor='w', pady=7)

        # Botón de notificaciones
        tk.Button(
            self.frame, text='🔔 Ver notificaciones',
            bg=self.estilo.colorLetra(),
            fg=self.estilo.colorFondo(),
            command=self.openNotificaciones
        ).pack(pady=10)

    def accion_permiso(self, permiso_id):
        """Método genérico para manejar la acción de cada permiso."""
        from tkinter import messagebox
        messagebox.showinfo("Permiso activado", f"Se ejecutó la acción del permiso: {permiso_id}")

