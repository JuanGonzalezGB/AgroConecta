import tkinter as tk
from tkinter import Frame, Canvas, Scrollbar
from vistas.subventanas.interfaceSubViews import InterfaceSubViews

class VentanaNotificaciones(InterfaceSubViews):
    def __init__(self, root, user, estilo, notification_service):
        self.root = root
        self.user = user
        self.estilo = estilo
        self.titulo = "Notificaciones"
        
        self.notification_service = notification_service


        # Crear ventana
        self.win = tk.Toplevel(self.root)
        self.win.title(self.titulo)
        self.win.geometry("450x400")
        self.win.configure(bg=self.estilo.colorFondo())

        # Título
        tk.Label(
            self.win,
            text=f"Notificaciones de {self.user['nombre']}",
            font=("Arial", 14, "bold"),
            bg=self.estilo.colorFondo(),
            fg=self.estilo.colorLetra()
        ).pack(pady=10)
        tk.Button(self.win, text='Cerrar',fg=self.estilo.colorFondo(),bg=self.estilo.colorLetra(), command=self.botonCerrar).pack(anchor='s',pady=4)
        #self.bloquearRoot()   
        # Panel scrollable
        self._crear_panel_scroll()

        # Cargar notificaciones desde NotificationService
        self._cargar_notificaciones()
        self.notification_service.marcar_como_leidas(self.user["nombre"])
        self.root.wait_window(self.win)

    # PANEL SCROLLABLE
    def _crear_panel_scroll(self):
        frame_contenedor = Frame(self.win, bg=self.estilo.colorFondo())
        frame_contenedor.pack(fill="both", expand=True)

        self.canvas = Canvas(frame_contenedor, bg=self.estilo.colorFondo(), highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(frame_contenedor, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.frame_interno = Frame(self.canvas, bg=self.estilo.colorFondo())
        self.canvas.create_window((0, 0), window=self.frame_interno, anchor="nw")

        self.frame_interno.bind(
            "<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )


        # CARGAR NOTIFICACIONES DESDE NotificationService
    def _cargar_notificaciones(self):

        # Si no hay notification_service, usar el repositorio directo
        if self.notification_service is None:
            from notificaciones.notification_repository import NotificationRepository
            repo = NotificationRepository()
            notificaciones = repo.cargar(self.user["nombre"])
        else:
            notificaciones = self.notification_service.obtener_notificaciones(self.user["nombre"])

        if not notificaciones:
            tk.Label(
                self.frame_interno,
                text="No hay notificaciones",
                bg=self.estilo.colorFondo(),
                fg=self.estilo.colorLetra(),
                font=("Arial", 12)
            ).pack(pady=10)
            return

        # Mostrar más recientes arriba
        for n in reversed(notificaciones):
            self._crear_tarjeta(n)
        


    # TARJETA INDIVIDUAL
    def _crear_tarjeta(self, noti):
        tarjeta = Frame(self.frame_interno, bg=self.estilo.colorLetra(), bd=1, relief="solid")
        tarjeta.pack(fill="x", padx=10, pady=5)

        tk.Label(
            tarjeta,
            text=f"📌 {noti.get('titulo', 'Notificación')}",
            bg=self.estilo.colorLetra(),
            fg=self.estilo.colorFondo()
        ).pack(anchor="w", padx=5, pady=2)

        tk.Label(
            tarjeta,
            text=noti["mensaje"],
            font=("Arial", 10),
            bg=self.estilo.colorLetra(),
            fg=self.estilo.colorFondo(),
            wraplength=350,
            justify="left"
        ).pack(anchor="w", padx=5)

        tk.Label(
            tarjeta,
            text=noti["fecha_hora"],
            font=("Arial", 8),
            bg=self.estilo.colorLetra(),
            fg=self.estilo.colorFondo()
        ).pack(anchor="e", padx=5, pady=3)
