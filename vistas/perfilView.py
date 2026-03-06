import tkinter as tk
from tkinter import simpledialog, messagebox
from controlador.controladorPerfil import ControladorPerfil

class PerfilView:
    def __init__(self, root, user, estilo, notificationService):
        self.notificationService = notificationService
        self.estilo = estilo
        self.root = root
        self.user = user
        self.root.geometry("")          
        self.frame = tk.Frame(root, bg=self.estilo.colorFondo(), padx=10, pady=10)
        self.frame.pack(fill='both', expand=True)

        tk.Label(
            self.frame,
            text='⚪Perfil de Usuario',
            bg=estilo.colorFondo(),
            fg=estilo.colorTitulo(),
            font=('Arial', 18, 'bold')
        ).pack(pady=6)

        self.form_frame = tk.Frame(self.frame, bg=estilo.colorFondo())
        self.form_frame.pack(fill='both', expand=True, pady=6)
        # Inicializar controlador de perfil
        self.controladorPerfil = ControladorPerfil(self.user)

        self.fields = {}
        self.mostrarInfo()



        # Botones de acciones
        tk.Button(
            self.frame,
            text='Cambiar contraseña',
            bg=self.estilo.colorLetra(),
            fg=self.estilo.colorFondo(),
            command=self.abrir_cambiar_contrasena
        ).pack(fill='x', pady=4)

        tk.Button(
            self.frame,
            text='Salir',
            bg=self.estilo.colorLetra(),
            fg=self.estilo.colorFondo(),
            command=self.back
        ).pack(fill='x', pady=7)

        # Controlador para volver a otras vistas
        from controlador.controladorVistas import ControladorVistas
        self.controladorVistas = ControladorVistas(
            self.frame, self.root, self.user, None, self.estilo, self.notificationService
        )

    def mostrarInfo(self):
        print("DEBUG: contenido de self.user =", self.user)

        """Muestra la información del usuario filtrando campos sensibles."""
        user_filtrado = self.controladorPerfil.datos_filtrados_usuario()

        # Limpiar form_frame
        for w in self.form_frame.winfo_children():
            w.destroy()
        self.fields = {}

        row = 0
        for clave, valor in user_filtrado.items():
            tk.Label(
                self.form_frame,
                text=f"{clave.replace('_', ' ').capitalize()}:",
                bg=self.estilo.colorFondo(),
                fg=self.estilo.colorTitulo(),
                anchor='w',
                width=15,
                font=('Arial', 15, 'bold')
            ).grid(row=row, column=0, sticky='w', padx=0, pady=4)

            tk.Label(
                self.form_frame,
                text=valor,
                bg=self.estilo.colorFondo(),
                fg=self.estilo.colorLetra(),
                anchor='w',
                width=25,
                font=('Arial', 15)
            ).grid(row=row, column=1, sticky='w', padx=10, pady=4)

            row += 1

    def abrir_cambiar_contrasena(self):
        """Abre un diálogo para cambiar la contraseña del usuario."""
        # Pedir contraseña actual
        actual = simpledialog.askstring(
            "Contraseña actual", "Ingresa tu contraseña actual:", show="*"
        )
        if actual is None:
            return  # Usuario canceló

        # Pedir nueva contraseña
        nueva = simpledialog.askstring(
            "Nueva contraseña", "Ingresa tu nueva contraseña:", show="*"
        )
        if nueva is None:
            return  # Usuario canceló

        # Intentar cambiar la contraseña usando el controlador
        exito, msg = self.controladorPerfil.cambiar_contraseña(actual, nueva)
        if exito:
            messagebox.showinfo("Éxito", msg)
            # Actualizar la info en la vista
            self.user = self.controladorPerfil.user
        else:
            messagebox.showwarning("Error", msg)

    def back(self):   
        """Vuelve a la vista principal según roles del usuario."""
        self.controladorVistas.abrir_vista_por_roles()
