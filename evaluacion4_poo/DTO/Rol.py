class Rol:
    def __init__(self, id_rol: int = None, nombre: str = None):
        self._id_rol = id_rol
        self._nombre = nombre
    
    def __str__(self):
        return f"Rol(id_rol={self._id_rol}, nombre={self._nombre})"