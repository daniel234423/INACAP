class Departamento:
    def __init__(self, id, nombre, manager_id=None):
        self.id = id
        self.nombre = nombre
        self.manager_id = manager_id

    def __str__(self):
        mgr = f", Manager ID: {self.manager_id}" if self.manager_id else ""
        return f"Departamento: {self.nombre} (ID: {self.id}{mgr})"