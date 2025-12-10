class PaqueteTurictico:
    def __init__(self, id_paquete: int, nombre: str, fecah_inicio: str, fecha_fin: str, valor: float, destino: dict):
        self.id_paquete = id_paquete
        self.nombre = nombre
        self.fecah_inicio = fecah_inicio
        self.fecha_fin = fecha_fin
        self.precio = valor
        self.destino = destino
    def __str__(self):
        return f"PaqueteTurictico(id_paquete={self.id_paquete}, nombre={self.nombre}, fecah_inicio={self.fecah_inicio}, fecha_fin={self.fecha_fin}, precio={self.precio}, destino={self.destino})"