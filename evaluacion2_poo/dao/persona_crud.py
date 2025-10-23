from dao .Conexion import Conexion 
from dto .persona import Persona 
from typing import Optional ,List 


class PersonaCRUD :
    def __init__ (self ):
        self .db =Conexion ('localhost','root','234423','evaluacion2')

    def crear (self ,persona :Persona )->Optional [int ]:


        if getattr (persona ,'id',None ):
            query ="INSERT INTO persona (id, nombre, direccion, telefono, correo, fecha_inicio, salario, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())"
            params =(persona .id ,persona .nombre ,persona .direccion ,persona .telefono ,persona .correo ,persona .fecha_inicio ,persona .salario )
        else :
            query ="INSERT INTO persona (nombre, direccion, telefono, correo, fecha_inicio, salario, created_at) VALUES (%s,%s,%s,%s,%s,%s,NOW())"
            params =(persona .nombre ,persona .direccion ,persona .telefono ,persona .correo ,persona .fecha_inicio ,persona .salario )
        try :
            return self .db .ejecuta_dml (query ,params )
        except Exception as e :
            print (f"Error al crear persona: {e }")
            return None 
        finally :
            self .db .desconectar ()

    def listar (self )->List [Persona ]:
        query ="SELECT id, nombre, direccion, telefono, correo, fecha_inicio, salario, created_at FROM persona"
        try :
            rows =self .db .ejecuta_query (query )
            personas =[]
            if not rows :
                return []
            for r in rows :
                personas .append (Persona (id =r ['id'],nombre =r .get ('nombre'),direccion =r .get ('direccion'),telefono =r .get ('telefono'),correo =r .get ('correo'),fecha_inicio =r .get ('fecha_inicio'),salario =float (r .get ('salario',0 )or 0 ),created_at =r .get ('created_at')))
            return personas 
        except Exception as e :
            print (f"Error al listar personas: {e }")
            return []
        finally :
            self .db .desconectar ()

    def buscar_por_id (self ,id_persona :int )->Optional [Persona ]:
        query ="SELECT id, nombre, direccion, telefono, correo, fecha_inicio, salario, created_at FROM persona WHERE id = %s"
        try :
            rows =self .db .ejecuta_query (query ,(id_persona ,))
            if rows :
                r =rows [0 ]
                return Persona (id =r ['id'],nombre =r .get ('nombre'),direccion =r .get ('direccion'),telefono =r .get ('telefono'),correo =r .get ('correo'),fecha_inicio =r .get ('fecha_inicio'),salario =float (r .get ('salario',0 )or 0 ),created_at =r .get ('created_at'))
            return None 
        except Exception as e :
            print (f"Error al buscar persona por id: {e }")
            return None 
        finally :
            self .db .desconectar ()
