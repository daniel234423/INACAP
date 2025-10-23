from datetime import datetime

class Persona:
    def __init__(self, id, username, password_hash, empleado_id, created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.empleado_id = empleado_id
        self.created_at = created_at or datetime.utcnow()

    def __str__(self):
        return f"Persona: {self.username} (ID: {self.id}, Empleado ID: {self.empleado_id})"