from dao.Conexion import Conexion
from dto.empleado import Empleado
from dto.rol import Rol
from typing import List, Optional
import bcrypt # For password hashing

class EmpleadoCRUD:
    
    def __init__(self):
        # Replace with your actual DB credentials
        self.db = Conexion('localhost', 'root', '234423', 'evaluacion2')

    def crear(self, empleado: Empleado) -> Optional[int]:
        """ Crea un nuevo empleado y retorna su ID """
        query = """INSERT INTO empleado (nombre, direccion, telefono, correo, fecha_inicio, password_hash, salario, rol_id, departamento_id) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        # Hash the password before storing
        hashed_password = bcrypt.hashpw(empleado.password_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        params = (
            empleado.nombre,
            empleado.direccion,
            empleado.telefono,
            empleado.correo,
            empleado.fecha_inicio,
            hashed_password,
            empleado.salario,
            empleado.rol.id if empleado.rol else None,
            empleado.departamento_id
        )
        
        try:
            return self.db.ejecuta_dml(query, params)
        except Exception as e:
            print(f"Error al crear empleado: {e}")
            return None
        finally:
            self.db.desconectar()

    def listar(self) -> List[Empleado]:
        """ Retorna una lista de todos los objetos Empleado """
        query = """SELECT e.id, e.nombre, e.direccion, e.telefono, e.correo, e.fecha_inicio, e.password_hash, e.salario,
                          r.id as rol_id, r.nombre as rol_nombre, e.departamento_id
                   FROM empleado e LEFT JOIN rol r ON e.rol_id = r.id"""
        try:
            resultados_dict = self.db.ejecuta_query(query)
            empleados = []
            for item in resultados_dict:
                rol = Rol(item['rol_id'], item['rol_nombre']) if item.get('rol_id') else None
                empleados.append(Empleado(
                    id=item['id'],
                    nombre=item['nombre'],
                    direccion=item['direccion'],
                    telefono=item['telefono'],
                    correo=item['correo'],
                    fecha_inicio=item['fecha_inicio'],
                    password_hash=item['password_hash'],
                    rol=rol,
                    departamento_id=item['departamento_id'],
                    salario=float(item.get('salario', 0) or 0)
                ))
            return empleados
        except Exception as e:
            print(f"Error al listar empleados: {e}")
            return []
        finally:
            self.db.desconectar()

    def buscar_por_id(self, id_empleado: int) -> Optional[Empleado]:
        """ Busca un empleado por su ID """
        query = """SELECT e.id, e.nombre, e.direccion, e.telefono, e.correo, e.fecha_inicio, e.password_hash, e.salario,
                         r.id as rol_id, r.nombre as rol_nombre, e.departamento_id
                   FROM empleado e LEFT JOIN rol r ON e.rol_id = r.id
                   WHERE e.id = %s"""
        params = (id_empleado,)
        try:
            resultado = self.db.ejecuta_query(query, params)
            if resultado:
                item = resultado[0]
                rol = Rol(item['rol_id'], item['rol_nombre']) if item.get('rol_id') else None
                return Empleado(
                    id=item['id'],
                    nombre=item['nombre'],
                    direccion=item['direccion'],
                    telefono=item['telefono'],
                    correo=item['correo'],
                    fecha_inicio=item['fecha_inicio'],
                    password_hash=item['password_hash'],
                    rol=rol,
                    departamento_id=item['departamento_id'],
                    salario=float(item.get('salario', 0) or 0)
                )
            return None
        except Exception as e:
            print(f"Error al buscar empleado: {e}")
            return None
        finally:
            self.db.desconectar()
            
    def autenticar(self, email: str, password: str) -> Optional[Empleado]:
        """ Busca un empleado por su email y compara la contraseña hasheada. """
        query = """SELECT e.id, e.nombre, e.direccion, e.telefono, e.correo, e.fecha_inicio, e.password_hash, e.salario,
                          r.id as rol_id, r.nombre as rol_nombre, e.departamento_id
                   FROM empleado e LEFT JOIN rol r ON e.rol_id = r.id
                   WHERE e.correo = %s"""
        params = (email,)
        try:
            resultado = self.db.ejecuta_query(query, params)
            if resultado:
                item = resultado[0]
                # Verify the hashed password
                if bcrypt.checkpw(password.encode('utf-8'), item['password_hash'].encode('utf-8')):
                    rol = Rol(item['rol_id'], item['rol_nombre']) if item.get('rol_id') else None
                    return Empleado(
                        id=item['id'],
                        nombre=item['nombre'],
                        direccion=item['direccion'],
                        telefono=item['telefono'],
                        correo=item['correo'],
                        fecha_inicio=item['fecha_inicio'],
                        password_hash=item['password_hash'],
                        rol=rol,
                        departamento_id=item['departamento_id'],
                        salario=float(item.get('salario', 0) or 0)
                    )
            return None
        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None
        finally:
            self.db.desconectar()

    def editar(self, empleado: Empleado) -> bool:
        """ Actualiza un empleado """
        query = """UPDATE empleado SET 
                      nombre = %s, direccion = %s, telefono = %s, correo = %s, 
                      fecha_inicio = %s, password_hash = %s, salario = %s, rol_id = %s, departamento_id = %s
                   WHERE id = %s"""
        
        # Only hash password if it's provided and different
        current_empleado = self.buscar_por_id(empleado.id)
        hashed_password = current_empleado.password_hash if current_empleado else None
        if empleado.password_hash and current_empleado and not bcrypt.checkpw(empleado.password_hash.encode('utf-8'), current_empleado.password_hash.encode('utf-8')):
             hashed_password = bcrypt.hashpw(empleado.password_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        params = (
            empleado.nombre,
            empleado.direccion,
            empleado.telefono,
            empleado.correo,
            empleado.fecha_inicio,
            hashed_password,
            empleado.salario,
            empleado.rol.id if empleado.rol else None,
            empleado.departamento_id,
            empleado.id
        )
        try:
            filas_afectadas = self.db.ejecuta_dml(query, params)
            return filas_afectadas > 0
        except Exception as e:
            print(f"Error al editar empleado: {e}")
            return False
        finally:
            self.db.desconectar()

    def eliminar(self, id_empleado: int) -> bool:
        """ Elimina un empleado por su ID """
        query = "DELETE FROM empleado WHERE id = %s"
        params = (id_empleado,)
        try:
            filas_afectadas = self.db.ejecuta_dml(query, params)
            return filas_afectadas > 0
        except Exception as e:
            print(f"Error al eliminar empleado: {e}")
            return False
        finally:
            self.db.desconectar()

    def asignar_a_departamento(self, empleado_id: int, departamento_id: int) -> bool:
        """ Asigna un empleado a un departamento """
        query = "UPDATE empleado SET departamento_id = %s WHERE id = %s"
        params = (departamento_id, empleado_id)
        try:
            filas_afectadas = self.db.ejecuta_dml(query, params)
            return filas_afectadas > 0
        except Exception as e:
            print(f"Error al asignar empleado a departamento: {e}")
            return False
        finally:
            self.db.desconectar()

    def asignar_empleado_a_proyecto(self, empleado_id: int, proyecto_id: int) -> bool:
        """ Asigna un empleado a un proyecto (a través de registro_tiempo si es necesario, o una tabla pivote) """
        # Persist assignment in pivot table proyecto_empleado
        # Check if employee and project exist
        empleado_exists = self.buscar_por_id(empleado_id) is not None
        from dao.proyecto_crud import ProyectoCRUD
        proyecto_crud = ProyectoCRUD()
        proyecto_exists = proyecto_crud.buscar_por_id(proyecto_id) is not None

        if not empleado_exists or not proyecto_exists:
            print(f"Error: Empleado {empleado_id} o Proyecto {proyecto_id} no existen.")
            return False

        # Insert into pivot table (idempotent: ignore duplicates)
        try:
            query = "INSERT INTO proyecto_empleado (proyecto_id, empleado_id) VALUES (%s, %s)"
            self.db.ejecuta_dml(query, (proyecto_id, empleado_id))
            return True
        except Exception as e:
            # If duplicate primary key, treat as success; otherwise print and fail
            if 'Duplicate' in str(e) or 'duplicate' in str(e).lower():
                return True
            print(f"Error al asignar empleado a proyecto: {e}")
            return False
        finally:
            self.db.desconectar()