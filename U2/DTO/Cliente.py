from DTO.SocioNegocio import SocioNegocio
from DTO.Tipo import Tipo_Usuario

class Cliente(SocioNegocio):

    def __init__(self, run, nombre, apellido, direccion, fono, correo, tipo, montoCredito=500, deuda=0):
        super().__init__(run, nombre, apellido, direccion, fono, correo)
        self.tipo = tipo
        self.montoCredito = montoCredito
        self.deuda = deuda

    def __str__(self):
        return f"{super().nombre} {super().apellido} - {self.tipo.nombre}"

    def pagar(self, monto):
        if monto > 0:
            self.deuda = self.deuda - monto
            print(f"Se pagaron {monto} pesos. Deuda actual: {self.deuda} pesos")
        else:
            print("El monto a pagar debe ser mayor que cero.")
