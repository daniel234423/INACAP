class Persona:
    def __init__(self,id: int, nombre: str, apellido:str, email: str, run: str, fono: str):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.run = run
        self.fono = fono

    def __str__(self):
        return f"Persona(nombre={self.nombre}, apellido={self.apellido}, email={self.email}, run={self.run}, fono={self.fono})"