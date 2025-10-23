from dao.Conexion import Conexion

def create_schema(db_conn: Conexion) -> bool:
    """Crea las tablas básicas si no existen. Devuelve True si todo OK."""
    stmts = [
        # Roles
        """
        CREATE TABLE IF NOT EXISTS rol (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        # Tabla puente departamento_empleado
        """
        CREATE TABLE IF NOT EXISTS departamento_empleado (
            departamento_id INT NOT NULL,
            empleado_id INT NOT NULL,
            PRIMARY KEY (departamento_id, empleado_id),
            FOREIGN KEY (departamento_id) REFERENCES departamento(id) ON DELETE CASCADE,
            FOREIGN KEY (empleado_id) REFERENCES empleado(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,

        # Departamentos (manager_id added but FK will be added after empleado table exists)
        """
        CREATE TABLE IF NOT EXISTS departamento (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            manager_id INT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,

        # Empleados
        """
        CREATE TABLE IF NOT EXISTS empleado (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(200),
            direccion VARCHAR(300),
            telefono VARCHAR(50),
            correo VARCHAR(150) UNIQUE,
            fecha_inicio DATE,
            password_hash TEXT,
            salario DECIMAL(12,2) DEFAULT 0,
            rol_id INT,
            departamento_id INT,
            FOREIGN KEY (rol_id) REFERENCES rol(id) ON DELETE SET NULL,
            FOREIGN KEY (departamento_id) REFERENCES departamento(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,

        # Proyectos
        """
        CREATE TABLE IF NOT EXISTS proyecto (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(200),
            fecha_inicio DATE,
            fecha_fin DATE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,

        # Tabla puente proyecto_empleado (asignaciones de empleados a proyectos)
        """
        CREATE TABLE IF NOT EXISTS proyecto_empleado (
            proyecto_id INT NOT NULL,
            empleado_id INT NOT NULL,
            PRIMARY KEY (proyecto_id, empleado_id),
            FOREIGN KEY (proyecto_id) REFERENCES proyecto(id) ON DELETE CASCADE,
            FOREIGN KEY (empleado_id) REFERENCES empleado(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,

        # Registro de tiempo
        """
        CREATE TABLE IF NOT EXISTS registro_tiempo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            empleado_id INT,
            proyecto_id INT,
            fecha DATE,
            horas_trabajadas DECIMAL(6,2),
            descripcion TEXT,
            FOREIGN KEY (empleado_id) REFERENCES empleado(id) ON DELETE CASCADE,
            FOREIGN KEY (proyecto_id) REFERENCES proyecto(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        # Personas (usuarios de la aplicación)
        """
        CREATE TABLE IF NOT EXISTS persona (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            empleado_id INT,
            created_at DATETIME,
            FOREIGN KEY (empleado_id) REFERENCES empleado(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ]

    success = True
    for s in stmts:
        try:
            db_conn.ejecuta_dml(s)
        except Exception as e:
            # No abortamos, pero marcamos fallo
            print(f"Error al ejecutar DDL: {e}")
            success = False
    # Intentar agregar la columna salario si no existe (idempotente)
    try:
        db_conn.ejecuta_dml("ALTER TABLE empleado ADD COLUMN salario DECIMAL(12,2) DEFAULT 0")
    except Exception:
        pass
    # Intentar agregar la FK de manager en departamento apuntando a empleado (puede fallar si ya existe)
    try:
        # Asegurar que la columna manager_id exista (si la tabla fue creada sin ella)
        try:
            db_conn.ejecuta_dml("ALTER TABLE departamento ADD COLUMN manager_id INT NULL")
        except Exception:
            # Ignorar si ya existe
            pass

        # Ahora agregar la FK (si no existe)
        db_conn.ejecuta_dml("""
            ALTER TABLE departamento
            ADD CONSTRAINT fk_departamento_manager
            FOREIGN KEY (manager_id) REFERENCES empleado(id) ON DELETE SET NULL
        """)
    except Exception:
        # Si falla (p. ej. ya existe), lo ignoramos
        pass

    return success
