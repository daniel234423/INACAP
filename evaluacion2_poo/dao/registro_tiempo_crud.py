from dao .Conexion import Conexion 
from dto .registro_tiempo import RegistroTiempo 
from typing import List ,Optional 
from datetime import date 

class RegistroTiempoCRUD :

    def __init__ (self ):
        self .db =Conexion ('localhost','root','234423','evaluacion2')

    def crear (self ,registro :RegistroTiempo )->Optional [int ]:

        query ="INSERT INTO registro_tiempo (empleado_id, proyecto_id, fecha, horas_trabajadas, descripcion) VALUES (%s, %s, %s, %s, %s)"
        params =(registro .empleado_id ,registro .proyecto_id ,registro .fecha ,registro .horas_trabajadas ,registro .descripcion )

        try :
            return self .db .ejecuta_dml (query ,params )
        except Exception as e :
            print (f"Error al crear registro de tiempo: {e }")
            return None 
        finally :
            self .db .desconectar ()

    def listar (self )->List [RegistroTiempo ]:

        query ="SELECT id, empleado_id, proyecto_id, fecha, horas_trabajadas, descripcion FROM registro_tiempo"
        try :
            resultados_dict =self .db .ejecuta_query (query )
            registros =[]
            for item in resultados_dict :
                registros .append (RegistroTiempo (
                id =item ['id'],
                empleado_id =item ['empleado_id'],
                proyecto_id =item ['proyecto_id'],
                fecha =item ['fecha'],
                horas_trabajadas =item ['horas_trabajadas'],
                descripcion =item ['descripcion']
                ))
            return registros 
        except Exception as e :
            print (f"Error al listar registros de tiempo: {e }")
            return []
        finally :
            self .db .desconectar ()

    def buscar_por_id (self ,id_registro :int )->Optional [RegistroTiempo ]:

        query ="SELECT id, empleado_id, proyecto_id, fecha, horas_trabajadas, descripcion FROM registro_tiempo WHERE id = %s"
        params =(id_registro ,)
        try :
            resultado =self .db .ejecuta_query (query ,params )
            if resultado :
                item =resultado [0 ]
                return RegistroTiempo (
                id =item ['id'],
                empleado_id =item ['empleado_id'],
                proyecto_id =item ['proyecto_id'],
                fecha =item ['fecha'],
                horas_trabajadas =item ['horas_trabajadas'],
                descripcion =item ['descripcion']
                )
            return None 
        except Exception as e :
            print (f"Error al buscar registro de tiempo: {e }")
            return None 
        finally :
            self .db .desconectar ()

    def editar (self ,registro :RegistroTiempo )->bool :

        query ="""UPDATE registro_tiempo SET 
                      empleado_id = %s, proyecto_id = %s, fecha = %s, 
                      horas_trabajadas = %s, descripcion = %s
                   WHERE id = %s"""
        params =(
        registro .empleado_id ,
        registro .proyecto_id ,
        registro .fecha ,
        registro .horas_trabajadas ,
        registro .descripcion ,
        registro .id 
        )
        try :
            filas_afectadas =self .db .ejecuta_dml (query ,params )
            return filas_afectadas >0 
        except Exception as e :
            print (f"Error al editar registro de tiempo: {e }")
            return False 
        finally :
            self .db .desconectar ()

    def eliminar (self ,id_registro :int )->bool :

        query ="DELETE FROM registro_tiempo WHERE id = %s"
        params =(id_registro ,)
        try :
            filas_afectadas =self .db .ejecuta_dml (query ,params )
            return filas_afectadas >0 
        except Exception as e :
            print (f"Error al eliminar registro de tiempo: {e }")
            return False 
        finally :
            self .db .desconectar ()

    def listar_por_empleado (self ,empleado_id :int )->List [RegistroTiempo ]:

        query ="SELECT id, empleado_id, proyecto_id, fecha, horas_trabajadas, descripcion FROM registro_tiempo WHERE empleado_id = %s"
        params =(empleado_id ,)
        try :
            resultados_dict =self .db .ejecuta_query (query ,params )
            registros =[]
            for item in resultados_dict :
                registros .append (RegistroTiempo (
                id =item ['id'],
                empleado_id =item ['empleado_id'],
                proyecto_id =item ['proyecto_id'],
                fecha =item ['fecha'],
                horas_trabajadas =item ['horas_trabajadas'],
                descripcion =item ['descripcion']
                ))
            return registros 
        except Exception as e :
            print (f"Error al listar registros de tiempo por empleado: {e }")
            return []
        finally :
            self .db .desconectar ()
