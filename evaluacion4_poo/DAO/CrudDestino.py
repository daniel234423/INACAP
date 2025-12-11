from DAO.Conexion import Conexion
from DTO.Destino import Destino


class CrudDestino:
    def __init__(self):
        self.conexion = Conexion()
    
    def Agregar(self, destino: Destino, id_rol: int):
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
    
    def Mostrar(self):
        try:
            cursor = self.conexion.db.cursor()
            sql = "SELECT id, nombre, descripcion, actividades, costo FROM destino"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            destinos = []
            for fila in resultados:
                destino = Destino(
                    id_destino=fila[0],
                    nombre=fila[1],
                    descripcion=fila[2],
                    actividades=fila[3],
                    costo=fila[4]
                )
                destinos.append(destino)
            return destinos
        except Exception as e:
            print(f"Error al obtener destinos: {e}")
            return []
    
    def Modificar(self, destino: Destino, id_rol: int):
        try:
            if id_rol != 1:
                print("Acceso denegado: solo administradores pueden actualizar destinos.")
                return False
            cursor = self.conexion.db.cursor()
            
            campos = []
            valores = []
            
            if destino._nombre:
                campos.append("nombre=%s")
                valores.append(destino._nombre)
            if destino._descripcion:
                campos.append("descripcion=%s")
                valores.append(destino._descripcion)
            if destino._actividades:
                campos.append("actividades=%s")
                valores.append(destino._actividades)
            if destino._costo:
                campos.append("costo=%s")
                valores.append(destino._costo)
            
            if not campos:
                return False
            
            valores.append(destino._id_destino)
            sql = f"UPDATE destino SET {', '.join(campos)} WHERE id=%s"
            cursor.execute(sql, valores)
            self.conexion.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar destino: {e}")
            return False
        
    def Eliminar(self, id_destino: int, id_rol: int):
        try:
            if id_rol != 1:
                print("Acceso denegado: solo administradores pueden eliminar destinos.")
                return False
            cursor = self.conexion.db.cursor()
            sql = "DELETE FROM destino WHERE id=%s"
            cursor.execute(sql, (id_destino,))
            self.conexion.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar destino: {e}")
            return False