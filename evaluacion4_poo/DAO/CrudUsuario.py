import bcrypt
from DAO.Conexion import Conexion
from DTO.Usuario import Usuario


class CrudUsuario:
    def __init__(self):
        self.conexion = Conexion()
        
    def AgregarUsuario(self, usuario:Usuario):
        try:
            cursor = self.conexion.db.cursor()
            sql = "INSERT INTO usuario (nombre, apellido, email, run, fono, username, password_hash, id_rol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            valores = (usuario.nombre, usuario.apellido, usuario.email, usuario.run, usuario.fono, usuario.username, usuario.password, usuario.rol._id_rol)
            cursor.execute(sql, valores)
            self.conexion.db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error al agregar usuario: {e}")
            self.conexion.db.rollback()
            return None
    
    def ObtenerUsuarioPorUsername(self, username: str):
        try:
            cursor = self.conexion.db.cursor()
            sql = "SELECT u.id, u.nombre, u.apellido, u.email, u.run, u.fono, u.username, u.password_hash, r.id, r.tipo_rol FROM usuario u JOIN rol r ON u.id_rol = r.id WHERE u.username = %s"
            cursor.execute(sql, (username,))
            resultado = cursor.fetchone()
            if resultado:
                from DTO.Rol import Rol
                rol = Rol(id_rol=resultado[8], nombre=resultado[9])
                usuario = Usuario(
                    id=resultado[0],
                    nombre=resultado[1],
                    apellido=resultado[2],
                    email=resultado[3],
                    run=resultado[4],
                    fono=resultado[5],
                    username=resultado[6],
                    hash_password=resultado[7],
                    rol=rol
                )
                return usuario
            else:
                return None
        except Exception as e:
            print(f"Error al obtener usuario por username: {e}")
            return None
    
    def IniciarSesion(self, username: str, password: str):
        try:
            usuario = self.ObtenerUsuarioPorUsername(username)
            if not usuario:
                return None

            stored_hash = usuario.password
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return usuario
            return None
        except Exception as e:
            print(f"Error al iniciar sesión: {e}")
            return None