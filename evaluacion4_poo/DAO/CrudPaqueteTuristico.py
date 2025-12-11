from time import time
from DAO.Conexion import Conexion
from DTO.PaqueteTurictico import PaqueteTurictico


class CrudPaquete:
    def __init__(self):
        self.conexion = Conexion()
    
    def Agregar(self, paquete_turistico: PaqueteTurictico):
        try:
            cursor = self.conexion.db.cursor()

            sql_paquete = "INSERT INTO paquete_turistico (nombre, fecha_inicio, fecha_fin, valor_total) VALUES (%s, %s, %s, %s)"
            valor_total = 0
            if paquete_turistico.destinos:
                valor_total = sum((destino._costo or 0) for destino in paquete_turistico.destinos)

            valores_paquete = (
                paquete_turistico.nombre,
                paquete_turistico.fecha_inicio,
                paquete_turistico.fecha_fin,
                valor_total,
            )
            cursor.execute(sql_paquete, valores_paquete)
            id_paquete = cursor.lastrowid

            if paquete_turistico.destinos:
                sql_puente = "INSERT INTO paquete_destino (id_paquete, id_destino) VALUES (%s, %s)"
                valores_destinos = []
                for destino in paquete_turistico.destinos:
                    id_destino = getattr(destino, "_id_destino", None)
                    if id_destino is None:
                        raise ValueError("Algún destino no tiene _id_destino definido")
                    valores_destinos.append((id_paquete, id_destino))

                cursor.executemany(sql_puente, valores_destinos)

            self.conexion.db.commit()
            return id_paquete
        except Exception as e:
            print(f"Error al crear paquete turístico: {e}")
            self.conexion.db.rollback()
            return None
    
    def Mostrar(self):
        try:
            cursor = self.conexion.db.cursor()
            sql = """
                SELECT p.id, p.nombre, p.fecha_inicio, p.fecha_fin, p.valor_total,
                       d.id, d.nombre, d.descripcion, d.actividades, d.costo
                FROM paquete_turistico p
                LEFT JOIN paquete_destino pd ON p.id = pd.id_paquete
                LEFT JOIN destino d ON pd.id_destino = d.id
                ORDER BY p.id
            """
            cursor.execute(sql)
            resultados = cursor.fetchall()

            paquetes = {}
            for fila in resultados:
                p_id = fila[0]
                if p_id not in paquetes:
                    paquetes[p_id] = PaqueteTurictico(
                        id_paquete=fila[0],
                        nombre=fila[1],
                        fecha_inicio=fila[2],
                        fecha_fin=fila[3],
                        precio=fila[4],
                        destinos=[]
                    )

                d_id = fila[5]
                if d_id is not None:
                    from DTO.Destino import Destino
                    destino = Destino(
                        id_destino=fila[5],
                        nombre=fila[6],
                        descripcion=fila[7],
                        actividades=fila[8],
                        costo=fila[9]
                    )
                    paquetes[p_id].destinos.append(destino)

            return list(paquetes.values())
        except Exception as e:
            print(f"Error al obtener paquetes turísticos: {e}")
            return []
    def Modificar(self, paquete_turistico: PaqueteTurictico):
        try:
            cursor = self.conexion.db.cursor()
            
            campos = []
            valores = []
            
            if paquete_turistico.nombre:
                campos.append("nombre=%s")
                valores.append(paquete_turistico.nombre)
                
            if paquete_turistico.fecha_inicio:
                campos.append("fecha_inicio=%s")
                valores.append(paquete_turistico.fecha_inicio)
                
            if paquete_turistico.fecha_fin:
                campos.append("fecha_fin=%s")
                valores.append(paquete_turistico.fecha_fin)
                
            valor_total = None
            if paquete_turistico.precio is not None:
                valor_total = paquete_turistico.precio
            elif paquete_turistico.destinos is not None:
                valor_total = sum((destino._costo or 0) for destino in paquete_turistico.destinos)
                
            if valor_total is not None:
                campos.append("valor_total=%s")
                valores.append(valor_total)
                
            if campos:
                sql_actualizar = f"UPDATE paquete_turistico SET {', '.join(campos)} WHERE id=%s"
                valores.append(paquete_turistico.id_paquete)
                cursor.execute(sql_actualizar, tuple(valores))
                
            if paquete_turistico.destinos is not None:
                sql_eliminar_destinos = "DELETE FROM paquete_destino WHERE id_paquete=%s"
                cursor.execute(sql_eliminar_destinos, (paquete_turistico.id_paquete,))
                
                if paquete_turistico.destinos:
                    sql_insertar_destinos = "INSERT INTO paquete_destino (id_paquete, id_destino) VALUES (%s, %s)"
                    valores_destinos = []
                    for destino in paquete_turistico.destinos:
                        id_destino = getattr(destino, "_id_destino", None)
                        if id_destino is None:
                            raise ValueError("Algún destino no tiene _id_destino definido")
                        valores_destinos.append((paquete_turistico.id_paquete, id_destino))
                        
                    cursor.executemany(sql_insertar_destinos, valores_destinos)
                    
            self.conexion.db.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar paquete turístico: {e}")
            self.conexion.db.rollback()
            return False
    
    def Eliminar(self, id_paquete: int):
        try:
            cursor = self.conexion.db.cursor()

            sql_eliminar_destinos = "DELETE FROM paquete_destino WHERE id_paquete=%s"
            cursor.execute(sql_eliminar_destinos, (id_paquete,))

            sql_Eliminar = "DELETE FROM paquete_turistico WHERE id=%s"
            cursor.execute(sql_Eliminar, (id_paquete,))

            self.conexion.db.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar paquete turístico: {e}")
            self.conexion.db.rollback()
            return False