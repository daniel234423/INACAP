-- Schema and seed SQL for evaluacion2 (MySQL/MariaDB)
-- Created as a safe, idempotent script: uses IF NOT EXISTS and ON DUPLICATE KEY UPDATE for seeds.
CREATE DATABASE IF NOT EXISTS evaluacion2 CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
use evaluacion2;


-- Roles
CREATE TABLE IF NOT EXISTS rol (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Personas (datos personales)
CREATE TABLE IF NOT EXISTS persona (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(200),
  direccion VARCHAR(300),
  telefono VARCHAR(50),
  correo VARCHAR(150) UNIQUE,
  fecha_inicio DATE,
  salario DECIMAL(12,2) DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Departamentos (Creada antes que Empleado para evitar error 150. Manager_id FK se agrega después)
CREATE TABLE IF NOT EXISTS departamento (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL UNIQUE,
  manager_id INT NULL
  -- NOTA: La FOREIGN KEY a 'empleado(manager_id)' se agrega al final
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Empleados (PK = FK a persona.id)
-- Empleados: ahora cada empleado tiene su propio id autoincremental
CREATE TABLE IF NOT EXISTS empleado (
  id INT AUTO_INCREMENT PRIMARY KEY,
  persona_id INT NOT NULL UNIQUE,
  password_hash TEXT,
  rol_id INT,
  departamento_id INT,
  FOREIGN KEY (persona_id) REFERENCES persona(id) ON DELETE CASCADE,
  FOREIGN KEY (rol_id) REFERENCES rol(id) ON DELETE SET NULL,
  -- La FK a 'departamento' ya funciona porque 'departamento' existe
  FOREIGN KEY (departamento_id) REFERENCES departamento(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- AGREGAR la clave foránea faltante a DEPARTAMENTO (Resuelve la dependencia circular)
ALTER TABLE departamento
ADD CONSTRAINT fk_departamento_manager
FOREIGN KEY (manager_id) REFERENCES empleado(id) ON DELETE SET NULL;



-- Proyectos
CREATE TABLE IF NOT EXISTS proyecto (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(200),
  fecha_inicio DATE,
  fecha_fin DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla puente proyecto_empleado
CREATE TABLE IF NOT EXISTS proyecto_empleado (
  proyecto_id INT NOT NULL,
  empleado_id INT NOT NULL,
  PRIMARY KEY (proyecto_id, empleado_id),
  FOREIGN KEY (proyecto_id) REFERENCES proyecto(id) ON DELETE CASCADE,
  FOREIGN KEY (empleado_id) REFERENCES empleado(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Registro de tiempo
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

SET FOREIGN_KEY_CHECKS=1;

-- Seed data (idempotent)
-- Roles
INSERT INTO rol (nombre) VALUES
('Gerente'),
('EMPLEADO'),
('ADMINISTRADOR DE RH'),

ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

-- Departments (consultancy defaults)
INSERT INTO departamento (nombre) VALUES
('Desarollo sostenible'),
('Investigacion y Desarrollo'),
('Ventas'),
('Recursos Humanos'),
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

-- End of file