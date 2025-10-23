from dao.Conexion import Conexion
from dto.proyecto import Proyecto
from typing import List, Optional

class ProyectoCRUD:
    
    def __init__(self):
        # Replace the literals below with your actual DB credentials
        self.db = Conexion('localhost', 'root', '234423', 'evaluacion2')

    def crear(self, proyecto: Proyecto) -> Optional[int]:
        """ Crea un nuevo proyecto y retorna su ID """
        query = "INSERT INTO proyecto (nombre, fecha_inicio, fecha_fin) VALUES (%s, %s, %s)"
        params = (proyecto.nombre, proyecto.fecha_inicio, proyecto.fecha_fin)
        
        try:
            return self.db.ejecuta_dml(query, params)
        except Exception as e:
            print(f"Error al crear proyecto: {e}")
            return None
        finally:
            self.db.desconectar()

    def listar(self) -> List[Proyecto]:
        """ Retorna una lista de todos los objetos Proyecto """
        query = "SELECT id, nombre, fecha_inicio, fecha_fin FROM proyecto"
        try:
            resultados_dict = self.db.ejecuta_query(query)
            proyectos = []
            for item in resultados_dict:
                proyectos.append(Proyecto(item['id'], item['nombre'], item['fecha_inicio'], item['fecha_fin']))
            return proyectos
        except Exception as e:
            print(f"Error al listar proyectos: {e}")
            return []
        finally:
            self.db.desconectar()

    def buscar_por_id(self, id_proyecto: int) -> Optional[Proyecto]:
        """ Busca un proyecto por su ID """
        query = "SELECT id, nombre, fecha_inicio, fecha_fin FROM proyecto WHERE id = %s"
        params = (id_proyecto,)
        try:
            resultado = self.db.ejecuta_query(query, params)
            if resultado:
                item = resultado[0]
                return Proyecto(item['id'], item['nombre'], item['fecha_inicio'], item['fecha_fin'])
            return None
        except Exception as e:
            print(f"Error al buscar proyecto: {e}")
            return None
        finally:
            self.db.desconectar()
            
    def editar(self, proyecto: Proyecto) -> bool:
        """ Actualiza un proyecto """
        query = "UPDATE proyecto SET nombre = %s, fecha_inicio = %s, fecha_fin = %s WHERE id = %s"
        params = (proyecto.nombre, proyecto.fecha_inicio, proyecto.fecha_fin, proyecto.id)
        try:
            filas_afectadas = self.db.ejecuta_dml(query, params)
            return filas_afectadas > 0
        except Exception as e:
            print(f"Error al editar proyecto: {e}")
            return False
        finally:
            self.db.desconectar()

    def eliminar(self, id_proyecto: int) -> bool:
        """ Elimina un proyecto por su ID """
        query = "DELETE FROM proyecto WHERE id = %s"
        params = (id_proyecto,)
        try:
            filas_afectadas = self.db.ejecuta_dml(query, params)
            return filas_afectadas > 0
        except Exception as e:
            print(f"Error al eliminar proyecto: {e}")
            return False
        finally:
            self.db.desconectar()
