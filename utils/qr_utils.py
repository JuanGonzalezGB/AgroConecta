# utils/qr_utils.py
import os

def generar_qr_pedido(id_pedido: str) -> str:
    """
    Genera un QR PNG si la librería qrcode está instalada.
    Si no está, genera un .txt como marcador de posición.
    Devuelve la ruta creada.
    """
    try:
        import qrcode  # type: ignore
        usa_qrcode = True
    except ImportError:
        usa_qrcode = False

    carpeta = "qrs"
    os.makedirs(carpeta, exist_ok=True)

    ruta_png = os.path.join(carpeta, f"{id_pedido}.png")
    ruta_txt = os.path.join(carpeta, f"{id_pedido}.txt")

    if usa_qrcode:
        data = {"id_pedido": id_pedido}
        img = qrcode.make(data)
        img.save(ruta_png)
        return ruta_png
    else:
        # Placeholder si no hay qrcode instalado
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write(f"QR para pedido {id_pedido}\n(instala 'qrcode' para generar imágenes PNG)")
        return ruta_txt
