from datetime import date

class RegistroTiempo:
    def __init__(self, id, empleado_id, proyecto_id, fecha: date, horas_trabajadas: float, descripcion: str):
        self.id = id
        self.empleado_id = empleado_id
        self.proyecto_id = proyecto_id
        self.fecha = fecha
        self.horas_trabajadas = horas_trabajadas
        self.descripcion = descripcion

    def __str__(self):
        return f"Registro (ID: {self.id}) - Empleado {self.empleado_id} en Proyecto {self.proyecto_id}: {self.horas_trabajadas}h"