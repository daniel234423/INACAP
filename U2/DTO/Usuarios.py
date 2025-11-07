from DAO.Conexion import Conexion
import bcrypt

host = 'localhost'
user = 'root'
password = ''
db = 'poo_bd'

class Usuario:
    def __init__(self, username, password_hash, nombre, apellido, email, tipo_usuario):
        self.username = username
        self.password_hash = password_hash
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.tipo_usuario = tipo_usuario
    
    @staticmethod
    def login(username, password):
        con = Conexion(host, user, password, db)
        usuario_data = con.obtener_usuario(username)
        if usuario_data and len(usuario_data):
            usuario_data = usuario_data[0]
            hashed_password = usuario_data[2].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return Usuario(
                    username=usuario_data[1],
                    password_hash=usuario_data[2],
                    nombre=usuario_data[3],
                    apellido=usuario_data[4],
                    email=usuario_data[5],
                    tipo_usuario=usuario_data[6]
                )
    @staticmethod
    def registrar_usuario(username, password, nombre, apellido, email, tipo_usuario):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        nuevo_usuaruio =Usuario(
            username=username,
            password_hash=hashed_password.decode('utf-8'),
            nombre=nombre,
            apellido=apellido,
            email=email,
            tipo_usuario=tipo_usuario
        )
        con = Conexion(host, user, password, db)
        exito = con.agregar_usuario(nuevo_usuaruio)
        if exito:
            print("Usuario registrado exitosamente.")
            return nuevo_usuaruio
        else:
            print("Error al registrar el usuario.")
            return None