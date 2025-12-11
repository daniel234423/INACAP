from DTO.Destino import Destino


class PaqueteTurictico:
    def __init__(self, id_paquete: int, nombre: str, fecha_inicio: str, fecha_fin: str, precio: float | None = None, destinos: list[Destino] | None = None):
        self.id_paquete = id_paquete
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.precio = precio
        self.destinos = destinos or []

    def __str__(self):
        return (
            f"PaqueteTurictico(id_paquete={self.id_paquete}, nombre={self.nombre}, "
            f"fecha_inicio={self.fecha_inicio}, fecha_fin={self.fecha_fin}, precio={self.precio}, "
            f"destinos={self.destinos})"
        )