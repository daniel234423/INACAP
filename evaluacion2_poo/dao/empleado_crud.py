from dao.Conexion import Conexion
from dto.empleado import Empleado
from dto.rol import Rol
from typing import List, Optional
import bcrypt
from dao.persona_crud import PersonaCRUD


class EmpleadoCRUD:
    def __init__(self):
        self.db = Conexion('localhost', 'root', '234423', 'evaluacion2')

    def _empleado_has_persona_id(self) -> bool:
        """Detecta si la tabla 'empleado' posee la columna persona_id.
        Retorna False si hay error o no existe.
        """
        try:
            q = """
                SELECT COUNT(*) AS cnt
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'empleado'
                  AND COLUMN_NAME = 'persona_id'
            """
            res = self.db.ejecuta_query(q)
            if not res:
                return False
            return (res[0].get('cnt', 0) or 0) > 0
        except Exception:
            return False

    def crear(self, empleado: Empleado) -> Optional[int]:
        persona_dao = PersonaCRUD()
        from dto.persona import Persona
        persona = Persona(id=None, nombre=empleado.nombre, direccion=empleado.direccion, telefono=empleado.telefono,
            correo=empleado.correo, fecha_inicio=empleado.fecha_inicio,
            salario=getattr(empleado, 'salario', 0))
        try:
            pid = persona_dao.crear(persona)
            if not pid:
                print("Error: no se pudo crear persona asociada al empleado")
                return None

            hashed_password = bcrypt.hashpw(empleado.password_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if empleado.password_hash else None
            if self._empleado_has_persona_id():
                query = "INSERT INTO empleado (persona_id, password_hash, rol_id, departamento_id) VALUES (%s, %s, %s, %s)"
                params = (pid, hashed_password, empleado.rol.id if empleado.rol else None, empleado.departamento_id)
                emp_id = self.db.ejecuta_dml(query, params)
                # En este esquema, el id de empleado es autoincremental; devolvemos el id retornado
                return emp_id
            else:
                # Esquema antiguo: PK de empleado es el mismo id de persona (sin columna persona_id)
                query = "INSERT INTO empleado (id, password_hash, rol_id, departamento_id) VALUES (%s, %s, %s, %s)"
                params = (pid, hashed_password, empleado.rol.id if empleado.rol else None, empleado.departamento_id)
                _ = self.db.ejecuta_dml(query, params)
                # Devolvemos explícitamente el id utilizado (pid) para evitar confundir con filas afectadas
                return pid
        except Exception as e:
            print(f"Error al crear empleado: {e}")
            return None
        finally:
            self.db.desconectar()

    def listar(self) -> List[Empleado]:
        if self._empleado_has_persona_id():
            query = """SELECT e.id, e.persona_id, p.nombre, p.direccion, p.telefono, p.correo, p.fecha_inicio, e.password_hash, p.salario,
                              r.id as rol_id, r.nombre as rol_nombre, e.departamento_id
                       FROM empleado e
                       LEFT JOIN persona p ON e.persona_id = p.id
                       LEFT JOIN rol r ON e.rol_id = r.id"""
        else:
            query = """SELECT e.id, e.id AS persona_id, p.nombre, p.direccion, p.telefono, p.correo, p.fecha_inicio, e.password_hash, p.salario,
                              r.id as rol_id, r.nombre as rol_nombre, e.departamento_id
                       FROM empleado e
                       LEFT JOIN persona p ON e.id = p.id
                       LEFT JOIN rol r ON e.rol_id = r.id"""
        try:
            resultados_dict = self.db.ejecuta_query(query)
            empleados = []
            if not resultados_dict:
                return []
            for item in resultados_dict:
                rol = Rol(item['rol_id'], item['rol_nombre']) if item.get('rol_id') else None
                empleados.append(Empleado(
                    id=item['id'],
                    persona_id=item.get('persona_id'),
                    nombre=item.get('nombre'),
                    direccion=item.get('direccion'),
                    telefono=item.get('telefono'),
                    correo=item.get('correo'),
                    fecha_inicio=item.get('fecha_inicio'),
                    password_hash=item.get('password_hash'),
                    rol=rol,
                    departamento_id=item.get('departamento_id'),
                    salario=float(item.get('salario', 0) or 0)
                ))
            return empleados
        except Exception as e:
            print(f"Error al listar empleados: {e}")
            return []
        finally:
            self.db.desconectar()

    def buscar_por_id(self, id_empleado: int) -> Optional[Empleado]:
        if self._empleado_has_persona_id():
            query = """SELECT e.id, e.persona_id, p.nombre, p.direccion, p.telefono, p.correo, p.fecha_inicio, e.password_hash, p.salario,
                             r.id as rol_id, r.nombre as rol_nombre, e.departamento_id
                       FROM empleado e
                       LEFT JOIN persona p ON e.persona_id = p.id
                       LEFT JOIN rol r ON e.rol_id = r.id
                       WHERE e.id = %s"""
        else:
            query = """SELECT e.id, e.id AS persona_id, p.nombre, p.direccion, p.telefono, p.correo, p.fecha_inicio, e.password_hash, p.salario,
                             r.id as rol_id, r.nombre as rol_nombre, e.departamento_id
                       FROM empleado e
                       LEFT JOIN persona p ON e.id = p.id
                       LEFT JOIN rol r ON e.rol_id = r.id
                       WHERE e.id = %s"""
        params = (id_empleado,)
        try:
            resultado = self.db.ejecuta_query(query, params)
            if resultado:
                item = resultado[0]
                rol = Rol(item['rol_id'], item['rol_nombre']) if item.get('rol_id') else None
                return Empleado(
                    id=item['id'],
                    persona_id=item.get('persona_id'),
                    nombre=item.get('nombre'),
                    direccion=item.get('direccion'),
                    telefono=item.get('telefono'),
                    correo=item.get('correo'),
                    fecha_inicio=item.get('fecha_inicio'),
                    password_hash=item.get('password_hash'),
                    rol=rol,
                    departamento_id=item.get('departamento_id'),
                    salario=float(item.get('salario', 0) or 0)
                )
            return None
        except Exception as e:
            print(f"Error al buscar empleado: {e}")
            return None
        finally:
            self.db.desconectar()

    def autenticar(self, email: str, password: str) -> Optional[Empleado]:
        if self._empleado_has_persona_id():
            query = """SELECT e.id, e.persona_id, p.nombre, p.direccion, p.telefono, p.correo, p.fecha_inicio, e.password_hash, p.salario,
                              r.id as rol_id, r.nombre as rol_nombre, e.departamento_id
                       FROM persona p
                       JOIN empleado e ON e.persona_id = p.id
                       LEFT JOIN rol r ON e.rol_id = r.id
                       WHERE p.correo = %s"""
        else:
            query = """SELECT e.id, e.id AS persona_id, p.nombre, p.direccion, p.telefono, p.correo, p.fecha_inicio, e.password_hash, p.salario,
                              r.id as rol_id, r.nombre as rol_nombre, e.departamento_id
                       FROM persona p
                       JOIN empleado e ON e.id = p.id
                       LEFT JOIN rol r ON e.rol_id = r.id
                       WHERE p.correo = %s"""
        params = (email,)
        try:
            resultado = self.db.ejecuta_query(query, params)
            if resultado:
                item = resultado[0]
                stored_hash = item.get('password_hash')
                if stored_hash and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    rol = Rol(item['rol_id'], item['rol_nombre']) if item.get('rol_id') else None
                    return Empleado(
                        id=item['id'],
                        persona_id=item.get('persona_id'),
                        nombre=item.get('nombre'),
                        direccion=item.get('direccion'),
                        telefono=item.get('telefono'),
                        correo=item.get('correo'),
                        fecha_inicio=item.get('fecha_inicio'),
                        password_hash=item.get('password_hash'),
                        rol=rol,
                        departamento_id=item.get('departamento_id'),
                        salario=float(item.get('salario', 0) or 0)
                    )
            return None
        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None
        finally:
            self.db.desconectar()

    def editar(self, empleado: Empleado) -> bool:
        persona_query = """UPDATE persona SET nombre = %s, direccion = %s, telefono = %s, correo = %s, fecha_inicio = %s, salario = %s WHERE id = %s"""

        current_empleado = self.buscar_por_id(empleado.id)
        hashed_password = current_empleado.password_hash if current_empleado else None
        if empleado.password_hash and current_empleado and not bcrypt.checkpw(empleado.password_hash.encode('utf-8'), current_empleado.password_hash.encode('utf-8')):
            hashed_password = bcrypt.hashpw(empleado.password_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        empleado_query = """UPDATE empleado SET password_hash = %s, rol_id = %s, departamento_id = %s WHERE id = %s"""

        persona_params = (
            empleado.nombre,
            empleado.direccion,
            empleado.telefono,
            empleado.correo,
            empleado.fecha_inicio,
            empleado.salario,
            getattr(empleado, 'persona_id', None) or empleado.id
        )

        empleado_params = (
            hashed_password,
            empleado.rol.id if empleado.rol else None,
            empleado.departamento_id,
            empleado.id
        )

        try:
            p_res = self.db.ejecuta_dml(persona_query, persona_params)
            e_res = self.db.ejecuta_dml(empleado_query, empleado_params)
            return (p_res is not None) and (e_res is not None)
        except Exception as e:
            print(f"Error al editar empleado: {e}")
            return False
        finally:
            self.db.desconectar()

    def eliminar(self, id_empleado: int) -> bool:
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
        empleado_exists = self.buscar_por_id(empleado_id) is not None
        from dao.proyecto_crud import ProyectoCRUD
        proyecto_crud = ProyectoCRUD()
        proyecto_exists = proyecto_crud.buscar_por_id(proyecto_id) is not None

        if not empleado_exists or not proyecto_exists:
            print(f"Error: Empleado {empleado_id} o Proyecto {proyecto_id} no existen.")
            return False

        try:
            exists_q = "SELECT 1 AS ok FROM proyecto_empleado WHERE proyecto_id = %s AND empleado_id = %s LIMIT 1"
            try:
                ex = self.db.ejecuta_query(exists_q, (proyecto_id, empleado_id))
            except Exception:
                ex = None
            if ex:
                return True

            query = "INSERT INTO proyecto_empleado (proyecto_id, empleado_id) VALUES (%s, %s)"
            res = self.db.ejecuta_dml(query, (proyecto_id, empleado_id))
            return bool(res)
        except Exception as e:
            print(f"Error al asignar empleado a proyecto: {e}")
            return False
        finally:
            self.db.desconectar()
