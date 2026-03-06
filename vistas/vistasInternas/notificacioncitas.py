import tkinter as tk

def mostrarNotificaciones(self,root,notiVentana,notificationService):
    self.root = root
    self.notificationService=notificationService
    ventana = notiVentana
    # Obtener notificaciones pendientes
    notificaciones = self.notificationService.obtener_notificaciones(ventana.user["nombre"])
    
    # Mostrar notificaciones en panel dentro de la ventana
    if notificaciones:
        panel_notif = tk.Frame(ventana.frame, bg=self.estilo.colorFondo(), bd=2, relief="groove")
        panel_notif.pack(pady=10, fill="x")

        tk.Label(panel_notif, text="Notificaciones pendientes:", font=("Arial", 12, "bold"),
                    bg=self.estilo.colorFondo(), fg=self.estilo.colorTitulo()).pack(anchor="w", padx=5, pady=5)

        for n in notificaciones:
            texto = f"{n['titulo']}: {n['mensaje']}"
            tk.Label(panel_notif, text=texto, wraplength=400, justify="left",
                        anchor="w", bg=self.estilo.colorFondo(), fg=self.estilo.colorLetra()).pack(anchor="w", padx=10, pady=2)