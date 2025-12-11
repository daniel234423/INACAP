from datetime import datetime

from DAO.Conexion import Conexion


class CrudReserva:
    def __init__(self):
        self.conexion = Conexion()
    
    def Agregar(self, id_usuario: int, id_paquete: int, fecha_reserva: str = None):
        try:
            cursor = self.conexion.db.cursor()
            fecha_final = fecha_reserva or datetime.now().strftime("%Y-%m-%d")
            sql = "INSERT INTO reserva (id_usuario, id_paquete, fecha_reserva) VALUES (%s, %s, %s)"
            valores = (id_usuario, id_paquete, fecha_final)
            cursor.execute(sql, valores)
            self.conexion.db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error al agregar reserva: {e}")
            return None
    def Mostrar(self, id_usuario: int):
        try:
            cursor = self.conexion.db.cursor()
            sql = """
                SELECT r.id, r.id_usuario, r.id_paquete, r.fecha_reserva,
                       p.nombre, p.fecha_inicio, p.fecha_fin, p.valor_total,
                       u.nombre, u.apellido, u.username
                FROM reserva r
                JOIN paquete_turistico p ON r.id_paquete = p.id
                JOIN usuario u ON r.id_usuario = u.id
                WHERE r.id_usuario = %s
            """
            cursor.execute(sql, (id_usuario,))
            resultados = cursor.fetchall()
            reservas = []
            for fila in resultados:
                reserva = {
                    "id": fila[0],
                    "id_usuario": fila[1],
                    "id_paquete": fila[2],
                    "fecha_reserva": fila[3],
                    "paquete": {
                        "nombre": fila[4],
                        "fecha_inicio": fila[5],
                        "fecha_fin": fila[6],
                        "valor_total": fila[7],
                    },
                    "usuario": {
                        "nombre": fila[8],
                        "apellido": fila[9],
                        "username": fila[10],
                    },
                    "nombre_usuario": f"{fila[8]} {fila[9]}".strip(),
                    "username_usuario": fila[10],
                }
                reservas.append(reserva)
            return reservas
        except Exception as e:
            print(f"Error al obtener reservas: {e}")
            return []
    def Mostrar_Admin(self, id_rol: int):
        try:
            if id_rol != 1:
                print("Acceso denegado: solo administradores pueden ver todas las reservas.")
                return []
            cursor = self.conexion.db.cursor()
            sql = """
                SELECT r.id, r.id_usuario, r.id_paquete, r.fecha_reserva,
                       p.nombre, p.fecha_inicio, p.fecha_fin, p.valor_total,
                       u.nombre, u.apellido, u.username
                FROM reserva r
                JOIN paquete_turistico p ON r.id_paquete = p.id
                JOIN usuario u ON r.id_usuario = u.id
            """
            cursor.execute(sql)
            resultados = cursor.fetchall()
            reservas = []
            for fila in resultados:
                reserva = {
                    "id": fila[0],
                    "id_usuario": fila[1],
                    "id_paquete": fila[2],
                    "fecha_reserva": fila[3],
                    "paquete": {
                        "nombre": fila[4],
                        "fecha_inicio": fila[5],
                        "fecha_fin": fila[6],
                        "valor_total": fila[7],
                    },
                    "usuario": {
                        "nombre": fila[8],
                        "apellido": fila[9],
                        "username": fila[10],
                    },
                    "nombre_usuario": f"{fila[8]} {fila[9]}".strip(),
                    "username_usuario": fila[10],
                }
                reservas.append(reserva)
            return reservas
        except Exception as e:
            print(f"Error al obtener reservas: {e}")
            return []
    def Eliminar(self, id_reserva: int):
        try:
            cursor = self.conexion.db.cursor()
            sql = "DELETE FROM reserva WHERE id=%s"
            cursor.execute(sql, (id_reserva,))
            self.conexion.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar reserva: {e}")
            return False