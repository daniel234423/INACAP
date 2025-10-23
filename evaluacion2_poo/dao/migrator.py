from dao .Conexion import Conexion 


def create_schema (db_conn :Conexion )->bool :

    success =True 

    try :

        db_conn .ejecuta_dml (
        "INSERT INTO rol (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)",
        ('Gerente',)
        )
        db_conn .ejecuta_dml (
        "INSERT INTO rol (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)",
        ('Desarrollador',)
        )
        db_conn .ejecuta_dml (
        "INSERT INTO rol (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)",
        ('RH',)
        )


        db_conn .ejecuta_dml (
        "INSERT INTO departamento (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)",
        ('Desarrollo Backend',)
        )
        db_conn .ejecuta_dml (
        "INSERT INTO departamento (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)",
        ('Desarrollo Frontend',)
        )
        db_conn .ejecuta_dml (
        "INSERT INTO departamento (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)",
        ('QA / Testing',)
        )
        db_conn .ejecuta_dml (
        "INSERT INTO departamento (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)",
        ('Consultoría y Arquitectura',)
        )

    except Exception as e :
        print (f"Error al ejecutar seed en migrator: {e }")
        success =False 

    return success 
