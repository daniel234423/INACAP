from DAO.Conexion import Conexion
import time

host = 'localhost'
user = 'root'
password = "234423"
db = 'clase'

def agregar(c):
    try:
        con = Conexion(host, user, password, db)
        sql = f"""
        INSERT INTO Cliente (run, nombre, apellido, direccion, fono, correo, monto_credito, id_tipo)
        VALUES ('{c.run}', '{c.nombre}', '{c.apellido}', '{c.direccion}', '{c.fono}', '{c.correo}', {c.montoCredito}, {c.tipo})
        """
        con.ejecuta_query(sql)
        con.commit()
        print("\n\n¡Datos ingresados satisfactoriamente!")
        time.sleep(2)
        con.desconectar()
    except Exception as e:
        print("Error al agregar cliente:", e)

def editar(c, id_cliente):
    try:
        con = Conexion(host, user, password, db)
        sql = """
            UPDATE Cliente SET run='{}', nombre='{}', apellido='{}', direccion='{}', fono='{}',
            correo='{}', monto_credito={} WHERE id_cliente={}
        """.format(c.run, c.nombre, c.apellido, c.direccion, c.fono, c.correo, c.montoCredito, int(id_cliente))
        con.ejecuta_query(sql)
        con.commit()
        input("\n\nDatos modificados satisfactoriamente")
        con.desconectar()
    except Exception as e:
        print("Error al editar cliente:", e)

def eliminar(id_cliente):
    try:
        con = Conexion(host, user, password, db)
        sql = "DELETE FROM Cliente WHERE id_cliente={}".format(id_cliente)
        con.ejecuta_query(sql)
        con.commit()
        input("\n\nCliente eliminado satisfactoriamente")
        con.desconectar()
    except Exception as e:
        print("Error al eliminar cliente:", e)

def mostrartodos():
    try:
        con = Conexion(host, user, password, db)
        sql = "SELECT * FROM Cliente"
        cursor = con.ejecuta_query(sql)
        datos = cursor.fetchall()
        con.desconectar()
        return datos
    except Exception as e:
        con.rollback()
        print("Error al mostrar todos los clientes:", e)

def consultaparticular(id_cliente):
    try:
        con = Conexion(host, user, password, db)
        sql = "SELECT * FROM Cliente WHERE id_cliente={}".format(id_cliente)
        cursor = con.ejecuta_query(sql)
        datos = cursor.fetchone()
        con.desconectar()
        return datos
    except Exception as e:
        con.rollback()
        print("Error en consulta particular:", e)

def consultaparcial(cant):
    try:
        con = Conexion(host, user, password, db)
        sql = "SELECT * FROM Cliente"
        cursor = con.ejecuta_query(sql)
        datos = cursor.fetchmany(size=cant)
        con.desconectar()
        return datos
    except Exception as e:
        con.rollback()
        print("Error en consulta parcial:", e)

def mostrartipos():
    con = None
    try:
        con = Conexion(host, user, password, db)
        sql = "SELECT id_tipo, descripcion FROM TipoUsuario"
        cursor = con.ejecuta_query(sql)
        datos = cursor.fetchall()
        con.desconectar()
        return datos
    except Exception as e:
        if con:
            con.rollback()
        print(f"Error al mostrar tipos de usuario: {e}")
        return []
