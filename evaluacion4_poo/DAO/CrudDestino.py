from DAO.Conexion import Conexion
from DTO.Destino import Destino


class CrudDestino:
    def __init__(self):
        self.conexion = Conexion()
    
    def crear_destino(self, destino: Destino, id_rol: int):
        try:
            if id_rol != 1:
                print("Acceso denegado: solo administradores pueden crear destinos.")
                return None
            cursor = self.conexion.db.cursor()
            sql = "INSERT INTO destino (nombre, descripcion, actividades, costo) VALUES (%s, %s, %s, %s)"
            valores = (destino._nombre, destino._descripcion, destino._actividades, destino._costo)
            cursor.execute(sql, valores)
            self.conexion.db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error al crear destino: {e}")
            return None