from dao .Conexion import Conexion 
from dto .departamento import Departamento 
from typing import List ,Optional 

class DepartamentoCRUD :

    def __init__ (self ):
        self .db =Conexion ('localhost','root','234423','evaluacion2')

    def crear (self ,depto :Departamento )->Optional [int ]:


        if getattr (depto ,'manager_id',None ):
            query ="INSERT INTO departamento (nombre, manager_id) VALUES (%s, %s)"
            params =(depto .nombre ,depto .manager_id )
        else :
            query ="INSERT INTO departamento (nombre) VALUES (%s)"
            params =(depto .nombre ,)

        try :
            res =self .db .ejecuta_dml (query ,params )

            try :
                print (f"Departamento creado: nombre='{depto .nombre }', retornado_id={res }")
            except Exception :
                pass 
            return res 
        except Exception as e :
            print (f"Error al crear departamento: {e }")
            return None 
        finally :
            self .db .desconectar ()

    def listar (self )->List [Departamento ]:

        query ="SELECT id, nombre, manager_id FROM departamento"
        try :
            resultados_dict =self .db .ejecuta_query (query )
            departamentos =[]
            for item in resultados_dict :
                departamentos .append (Departamento (item ['id'],item ['nombre'],item .get ('manager_id')))
            return departamentos 
        except Exception as e :
            print (f"Error al listar departamentos: {e }")
            return []
        finally :
            self .db .desconectar ()

    def buscar_por_id (self ,id_depto :int )->Optional [Departamento ]:

        query ="SELECT id, nombre, manager_id FROM departamento WHERE id = %s"
        params =(id_depto ,)
        try :
            resultado =self .db .ejecuta_query (query ,params )
            if resultado :
                item =resultado [0 ]
                return Departamento (item ['id'],item ['nombre'],item .get ('manager_id'))
            return None 
        except Exception as e :
            print (f"Error al buscar departamento: {e }")
            return None 
        finally :
            self .db .desconectar ()

    def editar (self ,depto :Departamento )->bool :

        query ="UPDATE departamento SET nombre = %s, manager_id = %s WHERE id = %s"
        params =(depto .nombre ,getattr (depto ,'manager_id',None ),depto .id )
        try :
            filas_afectadas =self .db .ejecuta_dml (query ,params )
            return filas_afectadas >0 
        except Exception as e :
            print (f"Error al editar departamento: {e }")
            return False 
        finally :
            self .db .desconectar ()

    def eliminar (self ,id_depto :int )->bool :

        query ="DELETE FROM departamento WHERE id = %s"
        params =(id_depto ,)
        try :
            filas_afectadas =self .db .ejecuta_dml (query ,params )
            return filas_afectadas >0 
        except Exception as e :
            print (f"Error al eliminar departamento (posible FK constraint): {e }")
            return False 
        finally :
            self .db .desconectar ()

    def asignar_empleado (self ,departamento_id :int ,empleado_id :int )->bool :

        query ="INSERT INTO departamento_empleado (departamento_id, empleado_id) VALUES (%s, %s)"
        try :
            res =self .db .ejecuta_dml (query ,(departamento_id ,empleado_id ))
            return bool (res )
        except Exception as e :
            print (f"Error al asignar empleado a departamento: {e }")
            return False 
        finally :
            self .db .desconectar ()

    def listar_empleados_por_departamento (self ,departamento_id :int )->List [int ]:

        query ="SELECT empleado_id FROM departamento_empleado WHERE departamento_id = %s"
        try :
            rows =self .db .ejecuta_query (query ,(departamento_id ,))
            return [r ['empleado_id']for r in rows ]if rows else []
        except Exception as e :
            print (f"Error al listar asignaciones: {e }")
            return []
        finally :
            self .db .desconectar ()

    def quitar_empleado (self ,departamento_id :int ,empleado_id :int )->bool :

        query ="DELETE FROM departamento_empleado WHERE departamento_id = %s AND empleado_id = %s"
        try :
            res =self .db .ejecuta_dml (query ,(departamento_id ,empleado_id ))
            return bool (res )
        except Exception as e :
            print (f"Error al quitar asignación: {e }")
            return False 
        finally :
            self .db .desconectar ()
