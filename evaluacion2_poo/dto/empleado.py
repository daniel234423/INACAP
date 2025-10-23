from dto.rol import Rol

class Empleado:
    def __init__(self, id, nombre, direccion, telefono, correo, fecha_inicio, password_hash, rol: Rol, departamento_id, salario: float = 0.0):
        self.id = id
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.correo = correo
        self.fecha_inicio = fecha_inicio
        self.password_hash = password_hash
        self.rol = rol
        self.departamento_id = departamento_id
        self.salario = salario

    def __str__(self):
        return f"Empleado: {self.nombre} (ID: {self.id}, Correo: {self.correo}, Salario: {getattr(self,'salario',0)})"