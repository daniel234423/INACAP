from dao.Conexion import Conexion
from dto.rol import Rol
from typing import List, Optional

class RolCRUD:
    
    def __init__(self):
        self.db = Conexion('localhost', 'root', '234423', 'evaluacion2')

    def crear(self, rol: Rol) -> Optional[int]:
        """ Crea un nuevo rol y retorna su ID """
        query = "INSERT INTO rol (nombre) VALUES (%s)"
        params = (rol.nombre,)
        
        try:
            return self.db.ejecuta_dml(query, params)
        except Exception as e:
            print(f"Error al crear rol: {e}")
            return None
        finally:
            self.db.desconectar()

    def listar(self) -> List[Rol]:
        """ Retorna una lista de todos los objetos Rol """
        query = "SELECT id, nombre FROM rol"
        try:
            resultados_dict = self.db.ejecuta_query(query)
            roles = []
            for item in resultados_dict:
                roles.append(Rol(item['id'], item['nombre']))
            return roles
        except Exception as e:
            print(f"Error al listar roles: {e}")
            return []
        finally:
            self.db.desconectar()

    def buscar_por_id(self, id_rol: int) -> Optional[Rol]:
        """ Busca un rol por su ID """
        query = "SELECT id, nombre FROM rol WHERE id = %s"
        params = (id_rol,)
        try:
            resultado = self.db.ejecuta_query(query, params)
            if resultado:
                item = resultado[0]
                return Rol(item['id'], item['nombre'])
            return None
        except Exception as e:
            print(f"Error al buscar rol: {e}")
            return None
        finally:
            self.db.desconectar()

    def buscar_por_nombre(self, nombre_rol: str) -> Optional[Rol]:
        """ Busca un rol por su nombre para validación. """
        query = "SELECT id, nombre FROM rol WHERE nombre = %s"
        params = (nombre_rol,)
        try:
            if not self.db.conexion:
                self.db.conectar()
            resultado = self.db.ejecuta_query(query, params)
            if resultado:
                item = resultado[0]
                return Rol(item['id'], item['nombre'])
            return None
        except Exception as e:
            print(f"Error al buscar rol por nombre: {e}")
            return None
        finally:
            self.db.desconectar()
