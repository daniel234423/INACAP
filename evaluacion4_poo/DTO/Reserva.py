class Reserva:
    def __init__(self, id_reserva, fecha_reserva: str, usuario: dict, paquete_turistico: dict):
        self.id_reserva = id_reserva
        self.fecha_reserva = fecha_reserva
        self.usuario = usuario
        self.paquete_turistico = paquete_turistico
    
    def __str__(self):
        return f"Reserva(id_reserva={self.id_reserva}, fecha_reserva={self.fecha_reserva}, usuario={self.usuario}, paquete_turistico={self.paquete_turistico})"