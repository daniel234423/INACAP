import pymysql 
import os 

class Conexion :
    def __init__ (self ,host ,user ,password ,db ):

        self .host =host 
        self .user =user 
        self .password =password 
        self .db =db 
        self .conexion =None 
        self .cursor =None 

        try :
            self .conexion =pymysql .connect (
            host =self .host ,
            user =self .user ,
            password =self .password ,
            db =self .db 
            )
            self .cursor =self .conexion .cursor (pymysql .cursors .DictCursor )
        except pymysql .MySQLError as e :

            raise RuntimeError (f"Error al conectar a la base de datos en __init__: {e }")

    def conectar (self ):
        try :
            self .conexion =pymysql .connect (
            host =self .host ,
            user =self .user ,
            password =self .password ,
            db =self .db 
            )
            self .cursor =self .conexion .cursor (pymysql .cursors .DictCursor )
        except pymysql .MySQLError as e :

            raise RuntimeError (f"Error al conectar a la base de datos: {e }")

    def desconectar (self ):
        if self .conexion :
            self .conexion .close ()
            self .conexion =None 
            self .cursor =None 


    def ejecuta_query (self ,query ,params =None ):

        if not self .conexion :
            self .conectar ()

        try :
            self .cursor .execute (query ,params )
            return self .cursor .fetchall ()
        except pymysql .MySQLError as e :
            print (f"Error en consulta: {e }")
            return None 

    def ejecuta_dml (self ,query ,params =None ):

        if not self .conexion :
            self .conectar ()

        try :

            try :
                print (f"Executing DML: {query } | params={params }")
            except Exception :
                pass 
            filas_afectadas =self .cursor .execute (query ,params )
            self .conexion .commit ()



            try :
                sql_op =query .strip ().split ()[0 ].upper ()
            except Exception :
                sql_op =''
            if sql_op =='INSERT':
                return self .cursor .lastrowid if self .cursor .lastrowid else filas_afectadas 
            return filas_afectadas 
        except pymysql .MySQLError as e :
            try :
                print (f"Error en DML: {e } -- Query: {query } | params={params }")
            except Exception :
                print (f"Error en DML: {e }")
            self .conexion .rollback ()
            return None 
        finally :


            pass 
