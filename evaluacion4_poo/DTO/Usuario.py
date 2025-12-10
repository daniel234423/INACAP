from DTO.Rol import Rol
from DTO.Persona import Persona


class Usuario(Persona):
    def __init__(self, id: int, nombre: str, apellido: str, email: str, run: str, fono: str, username: str, hash_password: str, rol: Rol):
        super().__init__(id, nombre, apellido, email, run, fono)
        self.username = username
        self.password = hash_password
        self.rol = rol

    def __str__(self):
        return f"Usuario(username={self.username}, rol={self.rol}, nombre={self.nombre}, apellido={self.apellido}, email={self.email}, run={self.run}, fono={self.fono})"