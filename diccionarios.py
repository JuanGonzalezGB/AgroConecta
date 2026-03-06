from estilo import colorOscuro, colorClaro, colorRosa, colorVerde, colorAzul, colorByN, colorRojo, colorVinoTinto, colorMagenta

TEMAS = {
    "Oscuro": "dark",
    "Claro": "light",
    "Verde": "green",
    "Azul": "blue",
    "Blanco y Negro": "bnw",
    "Rojo": "red",
    "Rosa": "pink",
    "VinoTinto": "wine",
    "Magenta": "magenta"
}
CLASESTEMAS = {
    "dark": colorOscuro.ColorOscuro,
    "light": colorClaro.ColorClaro,
    "green": colorVerde.ColorVerde,
    "blue": colorAzul.ColorAzul,
    "bnw": colorByN.ColorByN,
    "red": colorRojo.ColorRojo,
    "pink":colorRosa.ColorRosa,
    "wine":colorVinoTinto.ColorVinotinto,
    "magenta":colorMagenta.ColorMagenta
}

TIPOSUSUARIOS = {
    "Campesino": "campesino",
    "Restaurante": "restaurante",
    "Delivery": "delivery"
}

LLAVESFORMUSUARIOS = {
    'Campesino':['nombre','email','password','telefono','fecha_nacimiento','direccion'],
    'Restaurante':['nombre','email','password','nit','telefono','direccion'],
    'Delivery': ['nombre','email','password','telefono','tipo_vehiculo']
}

LLAVESUSUARIOS = {
    "Campesino": "campesinos",
    "Restaurante": "restaurantes",
    "Delivery": "deliverys"    
}
RESWINDPROFILE = {
    "Campesino": "480x350",
    "Restaurante": "480x310",
    "Delivery": "480x300"  
}
RESWINDREGIS = {
    "Campesino": "480x460",
    "Restaurante": "480x440",
    "Delivery": "480x400"    
}

PERMISOS_CATEGORIAS = ["lectura", "escritura", "eliminacion", "administrativo", "otros"]  

PERMISOS_ALIAS = {
    "ver_inventario": ["leer_inventario"],
    "agregar_cultivo": ["añadir_cultivo"],
    "vender_cultivo": [],  
    "eliminar_cultivo": ["borrar_cultivo", "quitar_cultivo"],
    "ver_historial_compras": ["leer_historial_compras"],
    "realizar_compra": [],  
    "ver_entregas": ["leer_entregas"],
    "gestionar_roles": ["administrar_roles"],
    "gestionar_usuarios": ["administrar_usuarios"],
    "gestionar_permisos": ["administrar_permisos"]
}


USUARIOS_INICIALES = {
            "campesinos": [],
            "restaurantes": [],
            "deliverys": [],
            "admin": [
                {
                    "nombre": "ADMIN",
                    "email": "ADMIN",
                    "password": "835d6dc88b708bc646d6db82c853ef4182fabbd4a8de59c213f2b5ab3ae7d9be",
                    "roles": ["admin"],
                    "permisos": [
                        "gestionar_permisos",
                        "gestionar_usuarios",
                        "gestionar_roles"
                    ]
                }
            ]
        }

ROLES_INICIALES = [
    {
        "id": "campesino",
        "nombre": "Campesino",
        "permisos": {
            "lectura": [{"id": "ver_inventario", "nombre": "ver_inventario"}],
            "escritura": [
                {"id": "agregar_cultivo", "nombre": "agregar_cultivo"},
                {"id": "vender_cultivo", "nombre": "vender_cultivo"}
            ],
            "eliminacion": [{"id": "eliminar_cultivo", "nombre": "eliminar_cultivo"}],
            "administrativo": [],
            "otros": []
        },
        "vista": "open_campesino"
    },
    {
        "id": "restaurante",
        "nombre": "Restaurante",
        "permisos": {
            "lectura": [
                {"id": "ver_inventario", "nombre": "ver_inventario"},
                {"id": "ver_historial_compras", "nombre": "ver_historial_compras"}
            ],
            "escritura": [
                {"id": "realizar_compra", "nombre": "realizar_compra"}
            ],
            "eliminacion": [],
            "administrativo": [],
            "otros": []
        },
        "vista": "open_restaurante"
    },
    {
        "id": "delivery",
        "nombre": "Delivery",
        "permisos": {
            "lectura": [{"id": "ver_entregas", "nombre": "ver_entregas"}],
            "escritura": [],
            "eliminacion": [],
            "administrativo": [],
            "otros": []
        },
        "vista": "open_delivery"
    },
    {
        "id": "admin",
        "nombre": "Administrador",
        "permisos": {
            "lectura": [],
            "escritura": [],
            "eliminacion": [],
            "administrativo": [
                {"id": "gestionar_roles", "nombre": "gestionar_roles"},
                {"id": "gestionar_usuarios", "nombre": "gestionar_usuarios"},
                {"id": "gestionar_permisos", "nombre": "gestionar_permisos"}                
            ],
            "otros": []
        },
        "vista": "open_admin"
    }
]
