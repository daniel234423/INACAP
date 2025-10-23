import pymysql
import os

class Conexion:
    def __init__(self, host, user, password, db):
        """Inicializa la conexión con parámetros explícitos (no usa config.ini).

        Parámetros:
            host: host de la base de datos
            user: usuario
            password: contraseña
            db: nombre de la base de datos
        """
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.conexion = None
        self.cursor = None

        try:
            self.conexion = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db
            )
            self.cursor = self.conexion.cursor(pymysql.cursors.DictCursor)
        except pymysql.MySQLError as e:
            # Fail fast: raise an exception so callers know the DB is not available.
            raise RuntimeError(f"Error al conectar a la base de datos en __init__: {e}")

    def conectar(self):
        try:
            self.conexion = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db
            )
            self.cursor = self.conexion.cursor(pymysql.cursors.DictCursor) # Usar DictCursor es muy útil
        except pymysql.MySQLError as e:
            # Propagate as runtime error so higher-level code can decide to abort.
            raise RuntimeError(f"Error al conectar a la base de datos: {e}")

    def desconectar(self):
        if self.conexion:
            self.conexion.close()
            self.conexion = None
            self.cursor = None
            # print("Conexión cerrada.")

    def ejecuta_query(self, query, params=None):
        """ Ejecuta un query (SELECT) y retorna resultados """
        if not self.conexion:
            self.conectar()
        
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"Error en consulta: {e}")
            return None

    def ejecuta_dml(self, query, params=None):
        """ Ejecuta DML (INSERT, UPDATE, DELETE) y retorna el ID (o filas afectadas) """
        if not self.conexion:
            self.conectar()
            
        try:
            filas_afectadas = self.cursor.execute(query, params)
            self.conexion.commit()
            return self.cursor.lastrowid if self.cursor.lastrowid else filas_afectadas
        except pymysql.MySQLError as e:
            print(f"Error en DML: {e}")
            self.conexion.rollback() # Hacer rollback si algo falla
            return None
        finally:
            # Opcional: desconectar después de cada operación DML
            # self.desconectar()
            pass
