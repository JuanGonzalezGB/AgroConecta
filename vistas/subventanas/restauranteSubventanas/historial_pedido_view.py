import tkinter as tk

class HistorialPedidoView:
    def __init__(self, root, pedido: dict, estilo):
        self.root = root
        self.pedido = pedido
        self.estilo = estilo

        self.win = tk.Toplevel(root)
        self.win.title(f"Historial del pedido {pedido.get('id_pedido', '')}")
        self.win.geometry("550x600")
        self.win.configure(bg=self.estilo.colorFondo())

        # TÍTULO
        tk.Label(
            self.win,
            text=f"Historial del Pedido #{pedido.get('id_pedido','')}",
            font=("Arial", 16, "bold"),
            bg=self.estilo.colorFondo(),
            fg=self.estilo.colorTitulo()
        ).pack(pady=10)

        # MARCO PRINCIPAL
        frame_principal = tk.Frame(self.win, bg=self.estilo.colorFondo())
        frame_principal.pack(fill="both", expand=True, padx=15, pady=10)

        # ========================================
        #     INFORMACIÓN GENERAL DEL PEDIDO
        # ========================================
        tk.Label(
            frame_principal,
            text="Información del pedido",
            font=("Arial", 14, "bold"),
            bg=self.estilo.colorFondo(),
            fg=self.estilo.colorTitulo()
        ).pack(anchor="w", pady=5)

        datos_generales = [
            f"Campesino: {pedido.get('campesino', '-')}",
            f"Restaurante: {pedido.get('restaurante', '-')}",
            f"Producto: {pedido.get('producto', '-')}",
            f"Cantidad: {pedido.get('cantidad', '-')}",
            f"Estado actual: {pedido.get('estado', '-')}",
            f"Fecha de creación: {pedido.get('fecha_creacion', '-')}"
        ]

        # Mostrar datos
        for linea in datos_generales:
            tk.Label(
                frame_principal,
                text=linea,
                font=("Arial", 12),
                bg=self.estilo.colorFondo(),
                fg=self.estilo.colorLetra(),
                anchor="w"
            ).pack(fill="x")

        # ========================================
        #       HISTORIAL COMPLETO DEL PROCESO
        # ========================================
        tk.Label(
            frame_principal,
            text="\nHistorial del proceso:",
            font=("Arial", 14, "bold"),
            bg=self.estilo.colorFondo(),
            fg=self.estilo.colorTitulo()
        ).pack(anchor="w", pady=10)

        frame_historial = tk.Frame(frame_principal, bg=self.estilo.colorFondo())
        frame_historial.pack(fill="x")

        historial = pedido.get("historial", [])

        if not historial:
            tk.Label(
                frame_historial,
                text="No hay eventos registrados.",
                font=("Arial", 12),
                bg=self.estilo.colorFondo(),
                fg=self.estilo.colorLetra()
            ).pack()
        else:
            for evento in historial:
                linea = f"{evento['fecha']} — {evento['evento']}"
                tk.Label(
                    frame_historial,
                    text=linea,
                    wraplength=500,
                    justify="left",
                    anchor="w",
                    bg=self.estilo.colorFondo(),
                    fg=self.estilo.colorLetra()
                ).pack(fill="x", pady=4)
