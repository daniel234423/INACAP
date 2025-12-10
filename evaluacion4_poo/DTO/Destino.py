class Destino:
    def __init__(self, id_destino: int, nombre: str, descripcion: str = None, actividades: str = None, costo: float = None):
        self._id_destino = id_destino
        self._nombre = nombre
        self._descripcion = descripcion
        self._actividades = actividades
        self._costo = costo
    
    def __str__(self):
        return f"Destrino(id_destrino={self._id_destrino}, nombre={self._nombre}, descripcion={self._descripcion}, actividades={self._actividades}, costo={self._costo})"