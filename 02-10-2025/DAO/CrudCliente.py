from DAO.Conexion import Conexion

host = 'localhost'
user = 'daniel'
password = '234423'
db = 'empresa'

def agregar(c):
    try:
        con = Conexion(host, user, password, db)
        sql = (
            "INSERT INTO cliente SET run='{}', nombre='{}', apellido='{}', direccion='{}', "
            "fono='{}', correo='{}', montoCredito='{}', tipo='{}'"
        ).format(
            c.run, c.nombre, c.apellido, c.direccion,
            c.fono, c.correo, c.montoCredito, c.tipo
        )
        con.ejecuta_query(sql)
        con.commit()
        print("\n\n¡Datos ingresados satisfactoriamente!")
        con.desconectar()
    except Exception as e:
        print("Error al agregar cliente:", e)
def editar(c):
    try:
        con = Conexion(host, user, password, db)
        sql="UPDATE CLIENTE SET run='{}',nombre='{}',apellido='{}',direccion='{}',fono={},correo='{}',"\
        "montoCredito={},deuda={},TIPO_id={} WHERE id={} ".format(c[1],c[2],c[3],c[4],c[5],c[6],c[7],c[8],c[9],c[10])
        con.ejecuta_query(sql)
        con.commit()
        input("\n\n Datos Modificados Satisfactorcamente")
        con.desconectar()
    except Exception as e:
        print(e)

def eliminar(id):
    try:
        con = Conexion(host, user, password, db)
        sql = "DELETE FROM CLIENTE WHERE id={}".format(id)
        con.ejecuta_query(sql)
        con.commit()
        input("\n\n Cliente Eliminado Satisfactorcamente ")
        con.desconectar()
    except Exception as e:
        print(e)
def mostrartodos():
    try:
        con = Conexion(host, user, password, db)
        sql = "select * from CLIENTE "
        cursor=con.ejecuta_query(sql)
        datos=cursor.fetchall()
        con.desconectar()
        return datos
    except Exception as e:
        con.rollback()
        print(e)

def consultaparticular(id):
    try:
        con = Conexion(host, user, password, db)
        sql = "select * from CLIENTE where id=[]".format(id)
        cursor=con.ejecuta_query(sql)
        datos=cursor.fetchone()
        con.desconectar()
        return datos
    except Exception as e:
        con.rollback()
        print(e)

def consultapartial(cant):
    try:
        con = Conexion(host, user, password, db)
        sql = "select * from CLIENTE "
        cursor = con.ejecuta_query(sql)
        datos = cursor.fetchmany(size=cant)
        con.desconectar()
        return datos
    except Exception as e:
        con.rollback()
        print(e)

# ---
def mostrartipos():
    con = None
    try:
        con = Conexion(host, user, password, db)
        sql = "SELECT id, nombre FROM TIPO"
        cursor = con.ejecuta_query(sql)
        datos = cursor.fetchall()
        con.desconectar()
        return datos
    except Exception as e:
        if con:
            con.rollback()
        print(f"Error: {e}")
        return []  # Devuelve una lista vacía en lugar de None