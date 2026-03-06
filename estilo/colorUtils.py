from kivy.utils import get_color_from_hex

def normalizar_color(color):

    if isinstance(color, str):
        return get_color_from_hex(color)

    if isinstance(color, (tuple, list)):

        if max(color) > 1:
            color = [c / 255 for c in color]

        if len(color) == 3:
            color = (*color, 1)

        return tuple(color)

    return color