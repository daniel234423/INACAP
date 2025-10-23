from dao.Conexion import Conexion
from dto.persona import Persona
from typing import Optional, List
import bcrypt

class PersonaCRUD:
    def __init__(self):
        # Use same DB credentials as other DAOs
        self.db = Conexion('localhost', 'root', '234423', 'evaluacion2')

    def crear(self, persona: Persona) -> Optional[int]:
        import datetime as _dt
        query = "INSERT INTO persona (username, password_hash, empleado_id, created_at) VALUES (%s, %s, %s, %s)"
        hashed = bcrypt.hashpw(persona.password_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        created_at = persona.created_at or _dt.datetime.now()
        params = (persona.username, hashed, persona.empleado_id, created_at)
        try:
            return self.db.ejecuta_dml(query, params)
        except Exception as e:
            print(f"Error al crear persona: {e}")
            return None
        finally:
            self.db.desconectar()

    def listar(self) -> List[Persona]:
        query = "SELECT id, username, password_hash, empleado_id, created_at FROM persona"
        try:
            rows = self.db.ejecuta_query(query)
            personas = []
            if not rows:
                return []
            for r in rows:
                personas.append(Persona(r['id'], r['username'], r['password_hash'], r['empleado_id'], r['created_at']))
            return personas
        except Exception as e:
            print(f"Error al listar personas: {e}")
            return []
        finally:
            self.db.desconectar()

    def buscar_por_username(self, username: str) -> Optional[Persona]:
        query = "SELECT id, username, password_hash, empleado_id, created_at FROM persona WHERE username = %s"
        try:
            rows = self.db.ejecuta_query(query, (username,))
            if rows:
                r = rows[0]
                return Persona(r['id'], r['username'], r['password_hash'], r['empleado_id'], r['created_at'])
            return None
        except Exception as e:
            print(f"Error al buscar persona: {e}")
            return None
        finally:
            self.db.desconectar()
    
    def autenticar(self, username: str, password: str) -> Optional[Persona]:
        # Realizar la consulta y la verificación en la misma conexión para evitar problemas
        query = "SELECT id, username, password_hash, empleado_id, created_at FROM persona WHERE username = %s"
        try:
            rows = self.db.ejecuta_query(query, (username,))
            if not rows:
                return None
            r = rows[0]
            stored = r.get('password_hash') or ''
            try:
                # bcrypt hashes usually start with $2b$ or $2a$
                if isinstance(stored, str) and stored.startswith('$2'):
                    ok = bcrypt.checkpw(password.encode('utf-8'), stored.encode('utf-8'))
                else:
                    # Fallback: direct comparison (backwards compatibility)
                    ok = (password == stored)
            except Exception as e:
                print(f"Error verificando contraseña: {e}")
                ok = False

            if ok:
                return Persona(r['id'], r['username'], r['password_hash'], r['empleado_id'], r['created_at'])
            return None
        except Exception as e:
            print(f"Error en autenticación persona: {e}")
            return None
        finally:
            self.db.desconectar()

    def buscar_por_id(self, id_persona: int) -> Optional[Persona]:
        query = "SELECT id, username, password_hash, empleado_id, created_at FROM persona WHERE id = %s"
        try:
            rows = self.db.ejecuta_query(query, (id_persona,))
            if rows:
                r = rows[0]
                return Persona(r['id'], r['username'], r['password_hash'], r['empleado_id'], r['created_at'])
            return None
        except Exception as e:
            print(f"Error al buscar persona por id: {e}")
            return None
        finally:
            self.db.desconectar()
