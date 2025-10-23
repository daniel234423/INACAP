import sys
import os
import time

from typing import Optional
import datetime
 
from dto.departamento import Departamento
from dto.empleado import Empleado
from dto.proyecto import Proyecto
from dto.registro_tiempo import RegistroTiempo
from dto.rol import Rol
 
from dao.departamento_crud import DepartamentoCRUD
from dao.empleado_crud import EmpleadoCRUD
from dao.proyecto_crud import ProyectoCRUD
from dao.rol_crud import RolCRUD
from dao.registro_tiempo_crud import RegistroTiempoCRUD
from dao.persona_crud import PersonaCRUD

class Main:
    def __init__(self):
        try:
            self.empleado_dao = EmpleadoCRUD()
            self.depto_dao = DepartamentoCRUD()
            self.proyecto_dao = ProyectoCRUD()
            self.rol_dao = RolCRUD()
            self.registro_tiempo_dao = RegistroTiempoCRUD()
        except Exception as e:
            print("ERROR: No se pudo establecer conexión con la base de datos. Detalle:", e)
            print("La aplicación requiere acceso a la base de datos para funcionar. Saliendo...")
            raise SystemExit(1)
        
        self.usuario_logueado: Optional[Empleado] = None
        
        print("--- Bienvenido al Sistema de Gestión de EcoTech Solutions ---")
        self._setup_initial_data()

    def _setup_initial_data(self):
        """Verifica y crea roles por defecto si no existen. También si la BD está vacía, crea
        departamentos y managers por defecto para una consultora de software.
        """
        try:
            from dao.migrator import create_schema
            migr_conn = self.depto_dao.db if hasattr(self.depto_dao, 'db') else None
            if migr_conn:
                created = create_schema(migr_conn)
                if created:
                    print("Esquema comprobado/creado.")
                else:
                    print("Se intentó crear el esquema, pero hubo errores. Revisa los mensajes.")
        except Exception as e:
            print(f"Advertencia: no se pudo ejecutar migraciones automáticas: {e}")

        roles_por_defecto = ["Administrador", "Gerente", "Jefe de Proyecto", "Desarrollador"]
        print("Verificando roles del sistema...")
        try:
            for nombre_rol in roles_por_defecto:
                rol_existente = self.rol_dao.buscar_por_nombre(nombre_rol)
                if not rol_existente:
                    nuevo_rol = Rol(id=None, nombre=nombre_rol)
                    self.rol_dao.crear(nuevo_rol)
                    print(f"Rol '{nombre_rol}' creado.")
            print("Roles configurados.")
        except Exception as e:
            print(f"Error al configurar roles: {e}")

        departamentos_iniciales = [
            "Desarrollo Backend",
            "Desarrollo Frontend",
            "QA / Testing",
            "Consultoría y Arquitectura",
        ]
        try:
            actuales = self.depto_dao.listar()
            actuales_nombres = [d.nombre for d in actuales] if actuales else []
            faltantes = [n for n in departamentos_iniciales if n not in actuales_nombres]
            if faltantes:
                print(f"Faltan {len(faltantes)} departamentos. Creando departamentos y managers por defecto...")
                for nombre in faltantes:
                    depto = Departamento(id=None, nombre=nombre)
                    depto_id = self.depto_dao.crear(depto)
                    if not depto_id:
                        print(f"No se pudo crear departamento '{nombre}' (tal vez ya existe).")
                        continue
                    rol_gerente = self.rol_dao.buscar_por_nombre('Gerente')
                    if not rol_gerente:
                        print("Rol 'Gerente' no encontrado.")
                        continue
                    import datetime as _dt
                    fecha_inicio = _dt.date.today()
                    manager_name = f"Mgr {nombre.split()[0]}"
                    manager_email = f"{manager_name.replace(' ','').lower()}@local"
                    existente_emp = None
                    try:
                        empleados_actuales = self.empleado_dao.listar()
                        for ee in empleados_actuales:
                            if getattr(ee, 'correo', None) == manager_email:
                                existente_emp = ee
                                break
                    except Exception:
                        existente_emp = None

                    if existente_emp:
                        if getattr(existente_emp, 'rol', None) and getattr(existente_emp.rol, 'nombre', '') == 'Gerente':
                            m_id = existente_emp.id
                        else:
                            print(f"Empleado con correo {manager_email} existe pero no es Gerente; no se reasignará como manager automático.")
                            m_id = None
                    else:
                        manager = Empleado(id=None, nombre=manager_name, direccion='N/A', telefono='000', correo=manager_email, fecha_inicio=fecha_inicio, password_hash='admin', rol=rol_gerente, departamento_id=depto_id, salario=0.0)
                        m_id = self.empleado_dao.crear(manager)

                    if m_id:
                        depto_obj = self.depto_dao.buscar_por_id(depto_id)
                        if depto_obj:
                            depto_obj.manager_id = m_id
                            self.depto_dao.editar(depto_obj)
                        from dto.persona import Persona
                        persona_dao = PersonaCRUD()
                        username = f"{manager_name.replace(' ','').lower()}"
                        if not persona_dao.buscar_por_username(username):
                            persona = Persona(id=None, username=username, password_hash='admin', empleado_id=m_id)
                            persona_dao.crear(persona)
                print("Semilla de departamentos completada.")
        except Exception as e:
            print(f"Error al semillar departamentos: {e}")

        try:
            empleados = self.empleado_dao.listar()
            if not empleados:
                print("No se encontraron empleados en la base de datos.")
                print("Opciones:")
                print("  1) Crear usuario administrador ahora")
                print("  2) Salir")
                print("  3) Continuar sin crear usuario (no recomendado)")
                opcion = input("Seleccione una opción (1/2/3): ").strip()
                if opcion == '1':
                    created = self.crear_admin_interactivo()
                    if created:
                        print("Administrador creado correctamente.")
                    else:
                        print("No se creó el administrador.")
                elif opcion == '2':
                    print("Saliendo...")
                    raise SystemExit(0)
                else:
                    print("Continuando sin crear usuarios. Algunas funciones fallarán si no hay empleados.")
        except Exception as e:
            print(f"Error al comprobar/solicitar datos iniciales: {e}")

        try:
            self.persona_dao = PersonaCRUD()
            personas = self.persona_dao.listar()
            if not personas:
                print("No hay usuarios (personas) configurados. Debe crear un usuario para iniciar sesión.")
                crear = input("¿Crear usuario ahora? (s/n): ").strip()
                if crear.lower() == 's':
                    res = self.crear_empleado_para_cuenta_interactivo()
                    if not res:
                        print("No se pudo crear el usuario. Saliendo.")
                        raise SystemExit(1)
                    empleado, pwd = res
                    self.usuario_logueado = empleado
                    username = input("Nombre de usuario para login [admin]: ").strip() or 'admin'
                    password = pwd
                    from dto.persona import Persona
                    persona = Persona(id=None, username=username, password_hash=password, empleado_id=empleado.id)
                    pid = self.persona_dao.crear(persona)
                    if pid:
                        print(f"Usuario '{username}' creado. Use ese nombre para iniciar sesión.")
                    else:
                        print("Error creando usuario (persona).")
                else:
                    print("No hay usuarios para iniciar sesión. Saliendo.")
                    raise SystemExit(1)
            else:
                while True:
                    try:
                        if os.name == 'nt':
                            os.system('cls')
                        else:
                            os.system('clear')
                    except Exception:
                        pass
                    time.sleep(0.2)
                    print("\n--- Inicio ---")
                    print("1) Iniciar sesión")
                    print("2) Crear cuenta (asociada a un Empleado existente o nueva)")
                    print("3) Salir")
                    choice = input("Seleccione una opción (1/2/3): ").strip()
                    if choice == '1':
                        for _ in range(3):
                            username = input("Usuario: ").strip()
                            password = input("Contraseña: ").strip()
                            persona = self.persona_dao.autenticar(username, password)
                            if persona:
                                empleado = self.empleado_dao.buscar_por_id(persona.empleado_id)
                                if not empleado:
                                    print("Empleado asociado no encontrado. Contacte al administrador.")
                                    raise SystemExit(1)
                                self.usuario_logueado = empleado
                                print(f"Bienvenido {empleado.nombre} (usuario: {username})")
                                break
                            else:
                                print("Credenciales incorrectas.")
                        else:
                            print("Fallaron los intentos de login.")
                        if self.usuario_logueado:
                            break
                    elif choice == '2':
                        print("Crear cuenta de usuario: se creará un nuevo empleado y se asociará la cuenta a él.")
                        empleado = self.crear_empleado_para_cuenta_interactivo()
                        if not empleado:
                            print("No se creó empleado. Operación cancelada.")
                            continue

                        if isinstance(empleado, tuple):
                            empleado_obj, pwd = empleado
                            empleado = empleado_obj
                        else:
                            pwd = getattr(empleado, 'password_hash', None)

                        username = input("Nombre de usuario (login): ").strip()
                        from dto.persona import Persona
                        exists = self.persona_dao.buscar_por_username(username)
                        if exists:
                            print("El nombre de usuario ya existe. Elija otro.")
                            continue
                        password = pwd or input("Contraseña: ")
                        persona = Persona(id=None, username=username, password_hash=password, empleado_id=empleado.id)
                        pid = self.persona_dao.crear(persona)
                        if pid:
                            auth = self.persona_dao.autenticar(username, password)
                            if auth:
                                print(f"Cuenta creada con éxito y verificada (username: {username}). Puede iniciar sesión.")
                            else:
                                print(f"Cuenta creada pero la verificación falló. Revise la contraseña o elimine/cree la cuenta nuevamente.")
                                stored = self.persona_dao.buscar_por_username(username)
                                if stored:
                                    print(f"Usuario en BD: id={stored.id}, username={stored.username}, empleado_id={stored.empleado_id}")
                        else:
                            print("Error creando la cuenta.")
                    elif choice == '3':
                        print("Saliendo...")
                        raise SystemExit(0)
                    else:
                        print("Opción inválida.")
        except Exception as e:
            print(f"Error en flujo de personas/login: {e}")
            raise

    def crear_admin_interactivo(self) -> bool:
        """Crea un usuario administrador mediante prompts en terminal.

        Retorna True si se creó correctamente.
        """
        try:
            deptos = self.depto_dao.listar()
            if not deptos:
                print("No hay departamentos. Se creará el departamento por defecto 'Administración'.")
                depto_default = Departamento(id=None, nombre="Administración")
                depto_id = self.depto_dao.crear(depto_default)
                if not depto_id:
                    print("Error: no se pudo crear departamento por defecto.")
                    return False
            else:
                print("Departamentos disponibles:")
                for d in deptos:
                    print(f"  ID: {d.id} - {d.nombre}")
                choice = input("Ingrese ID del departamento para el admin o presione Enter para crear 'Administración' por defecto: ")
                if choice.strip() == '':
                    existing = None
                    for d in deptos:
                        if d.nombre.lower() in ('administración', 'administracion'):
                            existing = d
                            break
                    if existing:
                        depto_id = existing.id
                    else:
                        depto_default = Departamento(id=None, nombre="Administración")
                        depto_id = self.depto_dao.crear(depto_default)
                else:
                    try:
                        depto_id = int(choice)
                        if not self.depto_dao.buscar_por_id(depto_id):
                            print("Departamento no encontrado. Se creará 'Administración'.")
                            depto_default = Departamento(id=None, nombre="Administración")
                            depto_id = self.depto_dao.crear(depto_default)
                    except ValueError:
                        print("Entrada inválida. Se creará 'Administración'.")
                        depto_default = Departamento(id=None, nombre="Administración")
                        depto_id = self.depto_dao.crear(depto_default)

            rol_admin = self.rol_dao.buscar_por_nombre("Administrador")
            if not rol_admin:
                print("Error: rol 'Administrador' no existe.")
                return False

            nombre = input("Nombre del administrador [Admin]: ") or "Admin"
            correo = input("Correo del administrador [admin@local]: ") or "admin@local"
            telefono = input("Teléfono [000000000]: ") or "000000000"
            direccion = input("Dirección [N/A]: ") or "N/A"
            import datetime as _dt
            fecha_inicio = _dt.date.today()
            password = input("Contraseña para el administrador [admin]: ") or "admin"
            while True:
                salario_str = input("Salario del administrador (ej: 120000.00) [0]: ") or "0"
                try:
                    salario = float(salario_str)
                    break
                except ValueError:
                    print("Entrada inválida para salario. Ingrese un número (por ejemplo 50000 o 50000.00).")

            nuevo = Empleado(
                id=None,
                nombre=nombre,
                direccion=direccion,
                telefono=telefono,
                correo=correo,
                fecha_inicio=fecha_inicio,
                password_hash=password,
                rol=rol_admin,
                departamento_id=depto_id,
                salario=salario
            )

            creado_id = self.empleado_dao.crear(nuevo)
            if not creado_id:
                print("Error al crear el administrador en la base de datos.")
                return False

            creado = self.empleado_dao.buscar_por_id(creado_id)
            if creado:
                self.usuario_logueado = creado
                return True
            return False
        except Exception as e:
            print(f"Error en creación interactiva de admin: {e}")
            return False

    def crear_empleado_para_cuenta_interactivo(self) -> Optional[tuple]:
        """Crea un empleado interactivo para asociarlo a una nueva cuenta de persona.

        Muestra departamentos con ID y nombre, pide selección por ID y crea el empleado con rol
        'Desarrollador' por defecto (puede cambiarse después).
        Retorna el objeto Empleado creado o None si falló.
        """
        try:
            deptos = self.depto_dao.listar()
            if not deptos:
                print("No hay departamentos configurados. Cree primero un departamento.")
                return None
            print("Departamentos disponibles:")
            for d in deptos:
                print(f"ID: {d.id} - {d.nombre}")
            try:
                depto_id = int(input("Ingrese el ID del departamento al que se asociará el nuevo empleado: "))
            except ValueError:
                print("ID inválido.")
                return None
            if not self.depto_dao.buscar_por_id(depto_id):
                print("Departamento no encontrado.")
                return None

            nombre = input("Nombre del empleado: ") or "Empleado"
            correo = input("Correo del empleado: ") or f"{nombre.replace(' ','').lower()}@local"
            telefono = input("Teléfono: ") or "000"
            direccion = input("Dirección: ") or "N/A"
            import datetime as _dt
            fecha_inicio = _dt.date.today()
            password = input("Contraseña para el empleado: ") or "changeme"
            # validar salario
            while True:
                salario_str = input("Salario del empleado (ej: 50000.00): ") or "0"
                try:
                    salario = float(salario_str)
                    break
                except ValueError:
                    print("Entrada inválida para salario. Intente de nuevo.")

            # Para cuentas de usuario nuevas, el empleado debe ser Gerente según la regla solicitada
            rol_gerente = self.rol_dao.buscar_por_nombre('Gerente')
            if not rol_gerente:
                print("Rol 'Gerente' no encontrado. Usando primer rol disponible.")
                roles = self.rol_dao.listar()
                rol_obj = roles[0] if roles else None
            else:
                rol_obj = rol_gerente

            nuevo = Empleado(id=None, nombre=nombre, direccion=direccion, telefono=telefono, correo=correo, fecha_inicio=fecha_inicio, password_hash=password, rol=rol_obj, departamento_id=depto_id, salario=salario)
            creado_id = self.empleado_dao.crear(nuevo)
            if not creado_id:
                print("Error al crear empleado para la cuenta.")
                return None
            creado = self.empleado_dao.buscar_por_id(creado_id)
            # Si el empleado creado es Gerente, asignarlo como manager del departamento seleccionado
            try:
                if creado and getattr(creado.rol, 'nombre', '') == 'Gerente':
                    depto_obj = self.depto_dao.buscar_por_id(depto_id)
                    if depto_obj:
                        if not getattr(depto_obj, 'manager_id', None):
                            depto_obj.manager_id = creado.id
                            self.depto_dao.editar(depto_obj)
                            print(f"Empleado {creado.nombre} asignado como manager del departamento {depto_obj.nombre}.")
                        else:
                            # Preguntar si desea reemplazar
                            resp = input(f"El departamento ya tiene un manager (ID {depto_obj.manager_id}). ¿Reemplazarlo por {creado.nombre}? (s/n): ").lower()
                            if resp == 's':
                                depto_obj.manager_id = creado.id
                                self.depto_dao.editar(depto_obj)
                                print(f"Manager reemplazado: ahora {creado.nombre} es manager de {depto_obj.nombre}.")
            except Exception as e:
                print(f"Advertencia: no se pudo asignar manager automáticamente: {e}")

            return (creado, password)
        except Exception as e:
            print(f"Error al crear empleado para cuenta: {e}")
            return None

    def seleccionar_usuario(self) -> bool:
        """Selecciona el usuario con el que se trabajará sin pedir contraseña.

        Lista los empleados existentes y pide al usuario que elija un ID. Si no hay empleados,
        devuelve False para indicar que no se puede continuar.
        """
        try:
            empleados = self.empleado_dao.listar()
        except Exception as e:
            print(f"Error al obtener lista de empleados: {e}")
            return False

        if not empleados:
            print("No hay empleados registrados en el sistema. No se puede continuar sin un usuario.")
            return False

        print("\n--- Seleccione Usuario ---")
        for emp in empleados:
            rol_nombre = emp.rol.nombre if getattr(emp, 'rol', None) else 'N/A'
            print(f"ID: {emp.id}, Nombre: {emp.nombre}, Correo: {emp.correo}, Rol: {rol_nombre}")

        try:
            empleado_id = int(input("Ingrese el ID del empleado con el que desea operar (0 para salir): "))
        except ValueError:
            print("Entrada no válida.")
            return False

        if empleado_id == 0:
            return False

        empleado = self.empleado_dao.buscar_por_id(empleado_id)
        if not empleado:
            print("Empleado no encontrado.")
            return False

        self.usuario_logueado = empleado
        print(f"Usuario seleccionado: {self.usuario_logueado.nombre} | Rol: {getattr(self.usuario_logueado.rol, 'nombre', 'N/A')}")
        return True

    def menu_principal(self):
        """Muestra el menú principal y gestiona las opciones."""
        if not self.usuario_logueado:
            print("No ha iniciado sesión. Por favor reinicie y autentíquese. Saliendo del sistema.")
            return

        while True:
            try:
                if os.name == 'nt':
                    os.system('cls')
                else:
                    os.system('clear')
            except Exception:
                pass
            time.sleep(0.2)
            print("\n--- Menú Principal ---")
            print(f"Usuario: {self.usuario_logueado.nombre} | Rol: {self.usuario_logueado.rol.nombre}")
            print("1. Gestión de Empleados")
            print("2. Gestión de Departamentos")
            print("3. Gestión de Proyectos")
            print("4. Registro de Tiempo")
            print("5. Gestión de Informes")
            print("0. Salir")
            
            opcion = input("Seleccione una opción: ").strip()
            
            if opcion == '1':
                self.gestion_de_empleados()
            elif opcion == '2':
                self.gestion_de_departamentos()
            elif opcion == '3':
                self.gestion_de_proyectos()
            elif opcion == '4':
                self.registro_de_tiempo()
            elif opcion == '5':
                self.gestion_de_informes()
            elif opcion == '0':
                print("Hasta luego.")
                break
            else:
                print("Opción no válida.")

    def gestion_de_empleados(self):
        if self.usuario_logueado.rol.nombre not in ['Administrador', 'Gerente']:
            print("Acceso denegado. Se requiere rol de Administrador o Gerente.")
            return

        while True:
            try:
                if os.name == 'nt':
                    os.system('cls')
                else:
                    os.system('clear')
            except Exception:
                pass
            time.sleep(0.15)
            print("\n--- Gestión de Empleados ---")
            print("1. Crear Empleado")
            print("2. Listar Empleados")
            print("3. Actualizar Empleado")
            print("4. Eliminar Empleado")
            print("5. Asignar Empleado a Departamento")
            print("0. Volver al Menú Principal")

            opcion = input("Seleccione una opción: ").strip()

            if opcion == '1':
                self.crear_empleado()
            elif opcion == '2':
                self.listar_empleados()
            elif opcion == '3':
                self.actualizar_empleado()
            elif opcion == '4':
                self.eliminar_empleado()
            elif opcion == '5':
                self.asignar_empleado_a_departamento()
            elif opcion == '0':
                break
            else:
                print("Opción no válida.")
    
    def crear_empleado(self):
        print("\n--- Crear Empleado ---")
        nombre = input("Nombre: ").strip()
        direccion = input("Dirección: ").strip()
        telefono = input("Teléfono: ").strip()
        correo = input("Correo electrónico: ").strip()
        fecha_inicio_str = input("Fecha de Inicio (YYYY-MM-DD): ").strip()
        fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
        password = input("Contraseña (se almacenará como texto en DB en este modo): ").strip()

        print("\n--- Roles Disponibles ---")
        roles = self.rol_dao.listar()
        for rol in roles:
            print(f"ID: {rol.id}, Rol: {rol.nombre}")
        rol_id = int(input("ID del Rol: ").strip())
        rol_obj = self.rol_dao.buscar_por_id(rol_id)
        if not rol_obj:
            print("Rol no encontrado. Operación cancelada.")
            return

        print("\n--- Departamentos Disponibles ---")
        departamentos = self.depto_dao.listar()
        for depto in departamentos:
            print(f"ID: {depto.id}, Nombre: {depto.nombre}")
        departamento_id = int(input("ID del Departamento: ").strip())

        nuevo_empleado = Empleado(
            id=None, nombre=nombre, direccion=direccion, telefono=telefono,
            correo=correo, fecha_inicio=fecha_inicio, password_hash=password,
            rol=rol_obj, departamento_id=departamento_id
        )
        if self.empleado_dao.crear(nuevo_empleado):
            print("Empleado creado exitosamente.")
        else:
            print("Error al crear empleado.")

    def listar_empleados(self):
        print("\n--- Listar Empleados ---")
        empleados = self.empleado_dao.listar()
        if not empleados:
            print("No hay empleados registrados.")
            return
        for emp in empleados:
            print(f"ID: {emp.id}, Nombre: {emp.nombre}, Correo: {emp.correo}, Rol: {emp.rol.nombre}, Depto ID: {emp.departamento_id}")

    def actualizar_empleado(self):
        print("\n--- Actualizar Empleado ---")
        self.listar_empleados()
        empleado_id = int(input("Ingrese el ID del empleado a actualizar: ").strip())
        empleado_existente = self.empleado_dao.buscar_por_id(empleado_id)

        if not empleado_existente:
            print("Empleado no encontrado.")
            return

        print(f"Editando empleado: {empleado_existente.nombre}")
        empleado_existente.nombre = input(f"Nombre ({empleado_existente.nombre}): ").strip() or empleado_existente.nombre
        empleado_existente.direccion = input(f"Dirección ({empleado_existente.direccion}): ").strip() or empleado_existente.direccion
        empleado_existente.telefono = input(f"Teléfono ({empleado_existente.telefono}): ").strip() or empleado_existente.telefono
        empleado_existente.correo = input(f"Correo ({empleado_existente.correo}): ").strip() or empleado_existente.correo
        fecha_inicio_str = input(f"Fecha de Inicio (YYYY-MM-DD) ({empleado_existente.fecha_inicio}): ").strip()
        if fecha_inicio_str:
            empleado_existente.fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
        
        new_password = input("Nueva Contraseña (dejar en blanco para no cambiar): ").strip()
        if new_password:
            empleado_existente.password_hash = new_password # DAO will hash it (si procede)

        salario_str = input(f"Salario ({getattr(empleado_existente,'salario',0)}): ").strip()
        if salario_str:
            try:
                empleado_existente.salario = float(salario_str)
            except ValueError:
                print("Salario inválido, se mantiene el valor previo.")

        print("\n--- Roles Disponibles ---")
        roles = self.rol_dao.listar()
        for rol in roles:
            print(f"ID: {rol.id}, Rol: {rol.nombre}")
        rol_id_str = input(f"ID del Rol ({empleado_existente.rol.id}): ").strip()
        if rol_id_str:
            rol_obj = self.rol_dao.buscar_por_id(int(rol_id_str))
            if rol_obj:
                empleado_existente.rol = rol_obj
            else:
                print("Rol no encontrado. Se mantiene el rol actual.")

        print("\n--- Departamentos Disponibles ---")
        departamentos = self.depto_dao.listar()
        for depto in departamentos:
            print(f"ID: {depto.id}, Nombre: {depto.nombre}")
        departamento_id_str = input(f"ID del Departamento ({empleado_existente.departamento_id}): ").strip()
        if departamento_id_str:
            empleado_existente.departamento_id = int(departamento_id_str)

        if self.empleado_dao.editar(empleado_existente):
            print("Empleado actualizado exitosamente.")
        else:
            print("Error al actualizar empleado.")

    def eliminar_empleado(self):
        print("\n--- Eliminar Empleado ---")
        self.listar_empleados()
        empleado_id = int(input("Ingrese el ID del empleado a eliminar: ").strip())
        if self.empleado_dao.eliminar(empleado_id):
            print("Empleado eliminado exitosamente.")
        else:
            print("Error al eliminar empleado.")

    def asignar_empleado_a_departamento(self):
        print("\n--- Asignar Empleado a Departamento ---")
        self.listar_empleados()
        empleado_id = int(input("ID del Empleado a asignar: ").strip())
        self.listar_departamentos()
        departamento_id = int(input("ID del Departamento: ").strip())

        if self.empleado_dao.asignar_a_departamento(empleado_id, departamento_id):
            print("Empleado asignado a departamento exitosamente.")
        else:
            print("Error al asignar empleado a departamento.")

    def gestion_de_departamentos(self):
        if self.usuario_logueado.rol.nombre not in ['Administrador', 'Gerente', 'Jefe de Proyecto']:
            print("Acceso denegado.")
            return

        while True:
            try:
                if os.name == 'nt':
                    os.system('cls')
                else:
                    os.system('clear')
            except Exception:
                pass
            time.sleep(0.15)
            print("\n--- Gestión de Departamentos ---")
            print("1. Crear Departamento")
            print("2. Listar Departamentos")
            print("3. Actualizar Departamento")
            print("4. Eliminar Departamento")
            print("5. Asignar Empleado a Departamento")
            print("0. Volver al Menú Principal")

            opcion = input("Opción: ").strip()

            if opcion == '1':
                self.crear_departamento()
            elif opcion == '2':
                self.listar_departamentos()
            elif opcion == '3':
                self.actualizar_departamento()
            elif opcion == '4':
                self.eliminar_departamento()
            elif opcion == '5':
                self.asignar_empleado_a_departamento()
            elif opcion == '0':
                break
            else:
                print("Opción no válida.")

    def crear_departamento(self):
        print("\n--- Crear Departamento ---")
        nombre = input("Ingrese nombre del nuevo departamento: ")
        # Preguntar si asignar un gerente ahora
        asignar = input("¿Asignar un gerente ahora? (s/n): ").lower()
        manager_id = None
        if asignar == 's':
            empleados = self.empleado_dao.listar()
            if not empleados:
                print("No hay empleados para asignar como gerente.")
            else:
                print("Empleados disponibles:")
                for e in empleados:
                    print(f"ID: {e.id} - {e.nombre} (Rol: {getattr(e.rol,'nombre','N/A')})")
                try:
                    candidate_id = int(input("Ingrese ID del empleado a asignar como gerente: "))
                    candidato = self.empleado_dao.buscar_por_id(candidate_id)
                    if not candidato:
                        print("Empleado no encontrado. No se asignará gerente.")
                    elif not getattr(candidato.rol, 'nombre', '') == 'Gerente':
                        print("El empleado seleccionado no tiene rol 'Gerente'. No se puede asignar como gerente.")
                    else:
                        manager_id = candidate_id
                except ValueError:
                    manager_id = None
        nuevo_depto = Departamento(id=None, nombre=nombre, manager_id=manager_id)
        if self.depto_dao.crear(nuevo_depto):
            print(f"Departamento '{nombre}' creado con éxito.")
        else:
            print("Error al crear departamento.")

    def listar_departamentos(self):
        print("\n--- Listar Departamentos ---")
        lista_deptos = self.depto_dao.listar()
        if not lista_deptos:
            print("No hay departamentos registrados.")
            return
        for depto in lista_deptos:
            print(f"ID: {depto.id}, Nombre: {depto.nombre}")

    def actualizar_departamento(self):
        print("\n--- Actualizar Departamento ---")
        self.listar_departamentos()
        depto_id = int(input("Ingrese el ID del departamento a actualizar: "))
        depto_existente = self.depto_dao.buscar_por_id(depto_id)

        if not depto_existente:
            print("Departamento no encontrado.")
            return

        print(f"Editando departamento: {depto_existente.nombre}")
        depto_existente.nombre = input(f"Nombre ({depto_existente.nombre}): ") or depto_existente.nombre
        # Permitir cambiar/establecer manager
        change_mgr = input("¿Cambiar/establecer gerente? (s/n): ").lower()
        if change_mgr == 's':
            empleados = self.empleado_dao.listar()
            if not empleados:
                print("No hay empleados para asignar como gerente.")
            else:
                print("Empleados disponibles:")
                for e in empleados:
                    print(f"ID: {e.id} - {e.nombre} (Rol: {getattr(e.rol,'nombre','N/A')})")
                try:
                    mgr_id = int(input("Ingrese ID del empleado a asignar como gerente (0 para quitar): "))
                except ValueError:
                    mgr_id = None
                if mgr_id == 0:
                    depto_existente.manager_id = None
                elif mgr_id:
                    # Verificar que el candidato sea Gerente
                    candidato = self.empleado_dao.buscar_por_id(mgr_id)
                    if not candidato:
                        print("Empleado no encontrado. No se cambiará el gerente.")
                    elif not getattr(candidato.rol, 'nombre', '') == 'Gerente':
                        print("El empleado seleccionado no tiene rol 'Gerente'. No se puede asignar como gerente.")
                    else:
                        # Si ya existe manager, pedir confirmación
                        if getattr(depto_existente, 'manager_id', None):
                            confirm = input(f"Este departamento ya tiene manager (ID {depto_existente.manager_id}). ¿Desea reemplazarlo? (s/n): ").lower()
                            if confirm != 's':
                                print("No se reemplazó el manager existente.")
                            else:
                                depto_existente.manager_id = mgr_id
                        else:
                            depto_existente.manager_id = mgr_id
        
        if self.depto_dao.editar(depto_existente):
            print("Departamento actualizado exitosamente.")
        else:
            print("Error al actualizar departamento.")

    def eliminar_departamento(self):
        print("\n--- Eliminar Departamento ---")
        self.listar_departamentos()
        depto_id = int(input("Ingrese el ID del departamento a eliminar: "))
        if self.depto_dao.eliminar(depto_id):
            print("Departamento eliminado exitosamente.")
        else:
            print("Error al eliminar departamento.")

    def gestion_de_proyectos(self):
        if self.usuario_logueado.rol.nombre not in ['Administrador', 'Gerente', 'Jefe de Proyecto']:
            print("Acceso denegado.")
            return

        while True:
            try:
                if os.name == 'nt':
                    os.system('cls')
                else:
                    os.system('clear')
            except Exception:
                pass
            time.sleep(0.15)
            print("\n--- Gestión de Proyectos ---")
            print("1. Crear Proyecto")
            print("2. Listar Proyectos")
            print("3. Actualizar Proyecto")
            print("4. Eliminar Proyecto")
            print("5. Asignar Empleado a Proyecto")
            print("0. Volver al Menú Principal")

            opcion = input("Opción: ")

            if opcion == '1':
                self.crear_proyecto()
            elif opcion == '2':
                self.listar_proyectos()
            elif opcion == '3':
                self.actualizar_proyecto()
            elif opcion == '4':
                self.eliminar_proyecto()
            elif opcion == '5':
                self.asignar_empleado_a_proyecto()
            elif opcion == '0':
                break
            else:
                print("Opción no válida.")

    def crear_proyecto(self):
        print("\n--- Crear Proyecto ---")
        nombre = input("Nombre del Proyecto: ")
        fecha_inicio_str = input("Fecha de Inicio (YYYY-MM-DD): ")
        fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
        fecha_fin_str = input("Fecha de Fin (YYYY-MM-DD): ")
        fecha_fin = datetime.datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()

        nuevo_proyecto = Proyecto(
            id=None, nombre=nombre, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
        )
        if self.proyecto_dao.crear(nuevo_proyecto):
            print("Proyecto creado exitosamente.")
        else:
            print("Error al crear proyecto.")

    def listar_proyectos(self):
        print("\n--- Listar Proyectos ---")
        proyectos = self.proyecto_dao.listar()
        if not proyectos:
            print("No hay proyectos registrados.")
            return
        for proj in proyectos:
            print(f"ID: {proj.id}, Nombre: {proj.nombre}, Inicio: {proj.fecha_inicio}, Fin: {proj.fecha_fin}")

    def actualizar_proyecto(self):
        print("\n--- Actualizar Proyecto ---")
        self.listar_proyectos()
        proyecto_id = int(input("Ingrese el ID del proyecto a actualizar: "))
        proyecto_existente = self.proyecto_dao.buscar_por_id(proyecto_id)

        if not proyecto_existente:
            print("Proyecto no encontrado.")
            return

        print(f"Editando proyecto: {proyecto_existente.nombre}")
        proyecto_existente.nombre = input(f"Nombre ({proyecto_existente.nombre}): ") or proyecto_existente.nombre
        fecha_inicio_str = input(f"Fecha de Inicio (YYYY-MM-DD) ({proyecto_existente.fecha_inicio}): ")
        if fecha_inicio_str:
            proyecto_existente.fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
        fecha_fin_str = input(f"Fecha de Fin (YYYY-MM-DD) ({proyecto_existente.fecha_fin}): ")
        if fecha_fin_str:
            proyecto_existente.fecha_fin = datetime.datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()

        if self.proyecto_dao.editar(proyecto_existente):
            print("Proyecto actualizado exitosamente.")
        else:
            print("Error al actualizar proyecto.")

    def eliminar_proyecto(self):
        print("\n--- Eliminar Proyecto ---")
        self.listar_proyectos()
        proyecto_id = int(input("Ingrese el ID del proyecto a eliminar: "))
        if self.proyecto_dao.eliminar(proyecto_id):
            print("Proyecto eliminado exitosamente.")
        else:
            print("Error al eliminar proyecto.")

    def asignar_empleado_a_proyecto(self):
        print("\n--- Asignar Empleado a Proyecto ---")
        self.listar_empleados()
        empleado_id = int(input("ID del Empleado: "))
        self.listar_proyectos()
        proyecto_id = int(input("ID del Proyecto: "))

        # This method in EmpleadoCRUD only confirms existence, not a direct assignment to a pivot table.
        # If a dedicated pivot table for employee-project assignments is needed, it should be implemented.
        if self.empleado_dao.asignar_empleado_a_proyecto(empleado_id, proyecto_id):
            print("Asignación lógica de empleado a proyecto confirmada.")
        else:
            print("Error en la asignación lógica de empleado a proyecto.")

    def registro_de_tiempo(self):
        if self.usuario_logueado.rol.nombre not in ['Administrador', 'Gerente', 'Jefe de Proyecto', 'Desarrollador']:
            print("Acceso denegado.")
            return

        while True:
            try:
                if os.name == 'nt':
                    os.system('cls')
                else:
                    os.system('clear')
            except Exception:
                pass
            time.sleep(0.15)
            print("\n--- Registro de Tiempo ---")
            print("1. Registrar Horas")
            print("2. Ver Mis Registros de Tiempo")
            print("0. Volver al Menú Principal")

            opcion = input("Opción: ")

            if opcion == '1':
                self.registrar_horas()
            elif opcion == '2':
                self.ver_mis_registros_tiempo()
            elif opcion == '0':
                break
            else:
                print("Opción no válida.")

    def registrar_horas(self):
        print("\n--- Registrar Horas ---")
        self.listar_proyectos()
        proyecto_id = int(input("ID del Proyecto: "))
        fecha_str = input("Fecha (YYYY-MM-DD): ")
        fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
        horas_trabajadas = float(input("Horas trabajadas: "))
        descripcion = input("Descripción del trabajo: ")

        nuevo_registro = RegistroTiempo(
            id=None,
            empleado_id=self.usuario_logueado.id, # Usa el ID del usuario logueado
            proyecto_id=proyecto_id,
            fecha=fecha,
            horas_trabajadas=horas_trabajadas,
            descripcion=descripcion
        )
        if self.registro_tiempo_dao.crear(nuevo_registro):
            print("Registro de tiempo creado exitosamente.")
        else:
            print("Error al crear registro de tiempo.")

    def ver_mis_registros_tiempo(self):
        print("\n--- Mis Registros de Tiempo ---")
        registros = self.registro_tiempo_dao.listar_por_empleado(self.usuario_logueado.id)
        if not registros:
            print("No tienes registros de tiempo.")
            return
        for reg in registros:
            proyecto = self.proyecto_dao.buscar_por_id(reg.proyecto_id)
            proyecto_nombre = proyecto.nombre if proyecto else "N/A"
            print(f"ID: {reg.id}, Proyecto: {proyecto_nombre}, Fecha: {reg.fecha}, Horas: {reg.horas_trabajadas}, Descripción: {reg.descripcion}")

    def gestion_de_informes(self):
        if self.usuario_logueado.rol.nombre not in ['Administrador', 'Gerente', 'Jefe de Proyecto']:
            print("Acceso denegado.")
            return

        while True:
            try:
                if os.name == 'nt':
                    os.system('cls')
                else:
                    os.system('clear')
            except Exception:
                pass
            time.sleep(0.15)
            print("\n--- Gestión de Informes ---")
            print("1. Ver Horas por Empleado")
            print("0. Volver al Menú Principal")

            opcion = input("Opción: ")

            if opcion == '1':
                self.ver_horas_por_empleado()
            elif opcion == '0':
                break
            else:
                print("Opción no válida.")

    def ver_horas_por_empleado(self):
        print("\n--- Horas Registradas por Empleado ---")
        self.listar_empleados()
        empleado_id = int(input("Ingrese el ID del empleado para ver sus registros: "))
        
        empleado = self.empleado_dao.buscar_por_id(empleado_id)
        if not empleado:
            print("Empleado no encontrado.")
            return

        registros = self.registro_tiempo_dao.listar_por_empleado(empleado_id)
        if not registros:
            print(f"El empleado {empleado.nombre} no tiene registros de tiempo.")
            return

        total_horas = 0
        print(f"\nRegistros de tiempo para {empleado.nombre}:")
        for reg in registros:
            proyecto = self.proyecto_dao.buscar_por_id(reg.proyecto_id)
            proyecto_nombre = proyecto.nombre if proyecto else "N/A"
            print(f"  - Proyecto: {proyecto_nombre}, Fecha: {reg.fecha}, Horas: {reg.horas_trabajadas}, Descripción: {reg.descripcion}")
            total_horas += reg.horas_trabajadas
        print(f"Total de horas registradas para {empleado.nombre}: {total_horas}")


# Punto de entrada de la aplicación
if __name__ == "__main__":
    app = Main()
    app.menu_principal()
