from DTO.SocioNegocio import SocioNegocio
from DTO.Tipo import TipoUsuario

class Cliente(SocioNegocio):
    def __init__(self, run, nombre, apellido, direccioncion, fono, correo, tipo, montocredito=500, deudua=0):
        super().__init__(run, nombre, apellido, direccioncion, fono, correo)
        self.tipo=tipo
        self.montoCredito=montocredito
        self.deuda=deudua
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.tipo}"
    def pagar(self, monto):
        if monto > 0:
            self.deuda = self.deuda-monto
            print(f"Se pagaron {monto} pesos. Deuda actual: {self.deuda} pesos")
        else:
            print("El monto a pagar debe ser mayor que cero ")