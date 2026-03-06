import tkinter as tk
from controlador.controlador_pedidos_restaurante import ControladorPedidosRestaurante
from vistas.subventanas.restauranteSubventanas.historial_pedido_view import HistorialPedidoView
from io import BytesIO
from PIL import Image, ImageTk
import base64

class MisPedidosRestauranteView:
    def __init__(self, root, restaurante_actual: dict, estilo):
        self.root = root
        self.restaurante = restaurante_actual
        self.estilo = estilo

        self.controlador = ControladorPedidosRestaurante(self.restaurante)

        self.win = tk.Toplevel(root)
        self.win.title(f"Pedidos de {self.restaurante.get('nombre', '')}")
        self.win.geometry("600x500")
        self.win.configure(bg=self.estilo.colorFondo())

        tk.Label(
            self.win,
            text=f"Pedidos realizados por {self.restaurante.get('nombre', '')}",
            font=("Arial", 14, "bold"),
            bg=self.estilo.colorFondo(),
            fg=self.estilo.colorTitulo()
        ).pack(pady=10)

        frame = tk.Frame(self.win, bg=self.estilo.colorFondo())
        frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(frame, bg=self.estilo.colorFondo(), highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=self.estilo.colorFondo())

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cargar_pedidos()

    def cargar_pedidos(self):
        pedidos = self.controlador.listar_mis_pedidos()

        if not pedidos:
            tk.Label(
                self.scroll_frame,
                text="No has realizado pedidos a campesinos.",
                font=("Arial", 12),
                bg=self.estilo.colorFondo(),
                fg=self.estilo.colorLetra()
            ).pack(pady=10)
            return

        for pedido in pedidos:
            marco = tk.Frame(self.scroll_frame, bd=1, relief="groove",
                             background=self.estilo.colorFondo())
            marco.pack(fill="x", padx=10, pady=5)

            tk.Label(
                marco,
                text=f"ID: {pedido.get('id_pedido','')}",
                font=("Arial", 10, "bold"),
                bg=self.estilo.colorFondo(),
                fg=self.estilo.colorTitulo()
            ).pack(anchor="w")

            tk.Label(
                marco,
                text=f"Campesino: {pedido.get('campesino','')}",
                font=("Arial", 10),
                bg=self.estilo.colorFondo(),
                fg=self.estilo.colorLetra()
            ).pack(anchor="w")

            tk.Label(
                marco,
                text=f"Estado: {pedido.get('estado','')}",
                font=("Arial", 10),
                bg=self.estilo.colorFondo(),
                fg=self.estilo.colorLetra()
            ).pack(anchor="w", pady=(0, 4))

            tk.Button(
                marco,
                text="Ver historial",
                command=lambda p=pedido: HistorialPedidoView(self.root, p, self.estilo),
                bg=self.estilo.colorLetra(),
                fg=self.estilo.colorFondo()
            ).pack(side="left", padx=4)

            tk.Button(
                marco,
                text="Ver QR",
                command=lambda p=pedido: self.mostrar_qr(p),
                bg=self.estilo.colorLetra(),
                fg=self.estilo.colorFondo()
            ).pack(side="left", padx=4)

    def mostrar_qr(self, pedido: dict):
        qr_b64 = pedido.get("qr_base64")
        if not qr_b64:
            top = tk.Toplevel(self.root)
            top.title("Código QR")
            tk.Label(top, text="Este pedido aún no tiene QR generado.").pack(pady=10, padx=10)
            return

        from PIL import Image, ImageTk
        from io import BytesIO
        import base64

        # Decodificar base64 a imagen
        qr_bytes = base64.b64decode(qr_b64)
        img = Image.open(BytesIO(qr_bytes))
        img = img.resize((250, 250))

        img_tk = ImageTk.PhotoImage(img)

        top = tk.Toplevel(self.root)
        top.title(f"QR del pedido {pedido.get('id_pedido','')}")

        label_img = tk.Label(top, image=img_tk)
        label_img.image = img_tk  # mantener referencia para que no se borre
        label_img.pack(pady=10, padx=10)