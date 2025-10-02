class TipoUsuario:
    def __init__(self, codigo, nombre):
        self.id = codigo
        self.nombre = nombre
    def __str__(self):
        return f"Cod: {self.id} - {self.nombre}"