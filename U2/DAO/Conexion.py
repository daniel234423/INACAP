import pymysql

from DTO.Usuarios import Usuario

class Conexion:
    def __init__(self, host, user, password, db):
        self.db = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db
        )
        self.cursor = self.db.cursor()

    def ejecuta_query(self, sql):
        self.cursor.execute(sql)
        return self.cursor

    def desconectar(self):
        self.db.close()

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()
    def obtener_usuario(self, username):
        try:
            sql = "SELECT * FROM USUARIOS WHERE username='{}'".format(username)
            cursor = self.cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print("Error al obtener el usuario:", e)
            return None
    def agregar_usuario(self, usuario: Usuario):
        try:
            sql = "INSERT INTO USUARIOS (username, password_hash, nombre, apellido, email, tipo_usuario) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(
                usuario.username,
                usuario.password_hash,
                usuario.nombre,
                usuario.apellido,
                usuario.email,
                usuario.tipo_usuario
            )
            self.cursor.execute(sql)
            self.commit()
            return True
        except Exception as e:
            print("Error al agregar el usuario:", e)
            self.rollback()
            return False