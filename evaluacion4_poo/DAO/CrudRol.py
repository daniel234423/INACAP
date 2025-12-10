from DAO.Conexion import Conexion
from DTO.Rol import Rol


class CrudRol:
    def __init__(self):
        self.conexion = Conexion()
    
    def obtener_rol(self, nombre_rol: str):
        try:
            cursor = self.conexion.db.cursor()
            sql = "SELECT id, tipo_rol FROM rol WHERE tipo_rol = %s"
            cursor.execute(sql, (nombre_rol,))
            resultado = cursor.fetchone()
            if resultado:
                rol = Rol(id_rol=resultado[0], nombre=resultado[1])
                return rol
            else:
                return None
        except Exception as e:
            print(f"Error al obtener rol: {e}")
            return None