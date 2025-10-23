import sys 
import os 
import time 

from typing import Optional 
import datetime 

from dto .departamento import Departamento 
from dto .empleado import Empleado 
from dto .proyecto import Proyecto 
from dto .registro_tiempo import RegistroTiempo 
from dto .rol import Rol 

from dao .departamento_crud import DepartamentoCRUD 
from dao .empleado_crud import EmpleadoCRUD 
from dao .proyecto_crud import ProyectoCRUD 
from dao .rol_crud import RolCRUD 
from dao .registro_tiempo_crud import RegistroTiempoCRUD 
from dao .persona_crud import PersonaCRUD 

class Main :
    def __init__ (self ):
        try :
            self .empleado_dao =EmpleadoCRUD ()
            self .depto_dao =DepartamentoCRUD ()
            self .proyecto_dao =ProyectoCRUD ()
            self .rol_dao =RolCRUD ()
            self .registro_tiempo_dao =RegistroTiempoCRUD ()
        except Exception as e :
            print ("ERROR: No se pudo establecer conexión con la base de datos. Detalle:",e )
            print ("La aplicación requiere acceso a la base de datos para funcionar. Saliendo...")
            raise SystemExit (1 )

        self .usuario_logueado :Optional [Empleado ]=None 

        print ("--- Bienvenido al Sistema de Gestión de EcoTech Solutions ---")
        self ._setup_initial_data ()

    def _setup_initial_data (self ):

        try :
            from dao .migrator import create_schema 
            migr_conn =self .depto_dao .db if hasattr (self .depto_dao ,'db')else None 
            if migr_conn :
                created =create_schema (migr_conn )
                if created :
                    print ("Esquema comprobado/creado.")
                else :
                    print ("Se intentó crear el esquema, pero hubo errores. Revisa los mensajes.")
        except Exception as e :
            print (f"Advertencia: no se pudo ejecutar migraciones automáticas: {e }")

        roles_por_defecto =["Gerente","Desarrollador","RH"]
        print ("Verificando roles del sistema...")
        try :
            for nombre_rol in roles_por_defecto :
                rol_existente =self .rol_dao .buscar_por_nombre (nombre_rol )
                if not rol_existente :
                    nuevo_rol =Rol (id =None ,nombre =nombre_rol )
                    self .rol_dao .crear (nuevo_rol )
                    print (f"Rol '{nombre_rol }' creado.")
            print ("Roles configurados.")
        except Exception as e :
            print (f"Error al configurar roles: {e }")

        departamentos_iniciales =[
        "Desarrollo Backend",
        "Desarrollo Frontend",
        "QA / Testing",
        "Consultoría y Arquitectura",
        ]
        try :
            actuales =self .depto_dao .listar ()
            actuales_nombres =[d .nombre for d in actuales ]if actuales else []
            faltantes =[n for n in departamentos_iniciales if n not in actuales_nombres ]
            if faltantes :
                print (f"Faltan {len (faltantes )} departamentos. Creando departamentos y managers por defecto...")
                for nombre in faltantes :
                    depto =Departamento (id =None ,nombre =nombre )
                    depto_id =self .depto_dao .crear (depto )
                    if not depto_id :
                        print (f"No se pudo crear departamento '{nombre }' (tal vez ya existe).")
                        continue 
                    rol_gerente =self .rol_dao .buscar_por_nombre ('Gerente')
                    if not rol_gerente :
                        print ("Rol 'Gerente' no encontrado.")
                        continue 
                    import datetime as _dt 
                    fecha_inicio =_dt .date .today ()
                    manager_name =f"Mgr {nombre .split ()[0 ]}"
                    manager_email =f"{manager_name .replace (' ','').lower ()}@local"
                    existente_emp =None 
                    try :
                        empleados_actuales =self .empleado_dao .listar ()
                        for ee in empleados_actuales :
                            if getattr (ee ,'correo',None )==manager_email :
                                existente_emp =ee 
                                break 
                    except Exception :
                        existente_emp =None 

                    if existente_emp :
                        if getattr (existente_emp ,'rol',None )and getattr (existente_emp .rol ,'nombre','')=='Gerente':
                            m_id =existente_emp .id 
                        else :
                            print (f"Empleado con correo {manager_email } existe pero no es Gerente; no se reasignará como manager automático.")
                            m_id =None 
                    else :
                        manager =Empleado (id =None ,nombre =manager_name ,direccion ='N/A',telefono ='000',correo =manager_email ,fecha_inicio =fecha_inicio ,password_hash ='admin',rol =rol_gerente ,departamento_id =depto_id ,salario =0.0 )
                        m_id =self .empleado_dao .crear (manager )

                    if m_id :
                        depto_obj =self .depto_dao .buscar_por_id (depto_id )
                        if depto_obj :
                            depto_obj .manager_id =m_id 
                            self .depto_dao .editar (depto_obj )

                print ("Semilla de departamentos completada.")
        except Exception as e :
            print (f"Error al semillar departamentos: {e }")
        try :
            self .persona_dao =PersonaCRUD ()
            personas =self .persona_dao .listar ()
            if not personas :
                print ("No hay usuarios (personas) configurados. Puede crear un usuario ahora o hacerlo más tarde desde el menú.")
                crear =input ("¿Crear usuario ahora? (s/n): ").strip ()
                if crear .lower ()=='s':
                    res =self .crear_empleado_para_cuenta_interactivo ()
                    if not res :
                        print ("No se pudo crear el usuario. Continuando sin usuario.")
                    else :
                        empleado ,pwd =res 
                        self .usuario_logueado =empleado 

                        default_username =getattr (empleado ,'nombre','user').replace (' ','').lower ()
                        username =default_username 

                        from dto .persona import Persona 
                        password =pwd 
                        persona =Persona (id =None ,empleado_id =empleado .id ,nombre =empleado .nombre ,direccion =empleado .direccion ,telefono =empleado .telefono ,correo =empleado .correo ,fecha_inicio =empleado .fecha_inicio ,salario =getattr (empleado ,'salario',0 ))
                        pid =self .persona_dao .crear (persona )
                        if pid :
                            print (f"Cuenta creada. Inicie sesión usando correo '{empleado .correo }' y la contraseña que ingresó.")
                        else :
                            print ("Error creando registro personal (persona).")
                else :
                    print ("Continuando sin usuarios. El menú inicial seguirá disponible, pero algunas funciones requerirán empleados.")
            else :
                while True :
                    try :
                        if os .name =='nt':
                            os .system ('cls')
                        else :
                            os .system ('clear')
                    except Exception :
                        pass 
                    time .sleep (0.2 )
                    print ("\n--- Inicio ---")
                    print ("1) Iniciar sesión")
                    print ("2) Crear cuenta (asociada a un Empleado existente o nueva)")
                    print ("3) Salir")
                    choice =input ("Seleccione una opción (1/2/3): ").strip ()
                    if choice =='1':
                        for _ in range (3 ):
                            correo =input ("Correo: ").strip ()
                            password =input ("Contraseña: ").strip ()
                            empleado =self .empleado_dao .autenticar (correo ,password )
                            if empleado :
                                if empleado.rol and empleado.rol.nombre == 'RH':
                                    self .usuario_logueado =empleado 
                                    print (f"Bienvenido {empleado .nombre } (correo: {correo })")
                                    break
                                else:
                                    print("Acceso denegado. Solo el personal de Recursos Humanos puede ingresar.")
                                    self.usuario_logueado = None
                            else :
                                print ("Credenciales incorrectas.")
                        else :
                            print ("Fallaron los intentos de login.")
                        if self .usuario_logueado :
                            break 
                    elif choice =='2':
                        print ("Crear cuenta de usuario: se creará un nuevo empleado y se asociará la cuenta a él.")
                        empleado =self .crear_empleado_para_cuenta_interactivo ()
                        if not empleado :
                            print ("No se creó empleado. Operación cancelada.")
                            continue 

                        if isinstance (empleado ,tuple ):
                            empleado_obj ,pwd =empleado 
                            empleado =empleado_obj 
                        else :
                            pwd =getattr (empleado ,'password_hash',None )


                        print (f"Empleado creado. Puede iniciar sesión con su correo y contraseña.")
                    elif choice =='3':
                        print ("Saliendo...")
                        raise SystemExit (0 )
                    else :
                        print ("Opción inválida.")
        except Exception as e :
            print (f"Error en flujo de personas/login: {e }")
            raise 

    def parse_date_input (self ,prompt :str ,allow_empty :bool =False ,default =None ):
        """Lee una fecha desde input aceptando múltiples formatos y opcionalmente permite vacío.
        Formatos válidos: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY, YYYY/MM/DD
        """
        fmts =["%Y-%m-%d","%d-%m-%Y","%d/%m/%Y","%Y/%m/%d"]
        while True :
            try :
                s =input (prompt ).strip ()
            except Exception :
                s =""
            if allow_empty and s =="":
                return default 
            for f in fmts :
                try :
                    return datetime .datetime .strptime (s ,f ).date ()
                except Exception :
                    pass 
            print ("Fecha inválida. Ejemplos válidos: 2025-10-23, 23-10-2025, 23/10/2025, 2025/10/23")

    def crear_admin_interactivo (self )->bool :
        try :
            deptos =self .depto_dao .listar ()
            if not deptos :
                print ("No hay departamentos. Se creará el departamento por defecto 'Administración'.")
                depto_default =Departamento (id =None ,nombre ="Administración")
                depto_id =self .depto_dao .crear (depto_default )
                if not depto_id :
                    print ("Error: no se pudo crear departamento por defecto.")
                    return False 
            else :
                print ("Departamentos disponibles:")
                for d in deptos :
                    print (f"  ID: {d .id } - {d .nombre }")
                choice =input ("Ingrese el ID del departamento para el admin o presione Enter para crear 'Administración' por defecto: ")
                if choice .strip ()=='':
                    existing =None 
                    for d in deptos :
                        if d .nombre .lower ()in ('administración','administracion'):
                            existing =d 
                            break 
                    if existing :
                        depto_id =existing .id 
                    else :
                        depto_default =Departamento (id =None ,nombre ="Administración")
                        depto_id =self .depto_dao .crear (depto_default )
                else :
                    try :
                        depto_id =int (choice )
                        if not self .depto_dao .buscar_por_id (depto_id ):
                            print ("Departamento no encontrado. Se creará 'Administración'.")
                            depto_default =Departamento (id =None ,nombre ="Administración")
                            depto_id =self .depto_dao .crear (depto_default )
                    except ValueError :
                        print ("Entrada inválida. Se creará 'Administración'.")
                        depto_default =Departamento (id =None ,nombre ="Administración")
                        depto_id =self .depto_dao .crear (depto_default )

            rol_admin =self .rol_dao .buscar_por_nombre ("RH")
            if not rol_admin :
                print ("Error: rol 'RH' no existe.")
                return False 

            nombre =input ("Nombre del administrador (RH) [Admin]: ")or "Admin"
            correo =input ("Correo del administrador (RH) [admin@local]: ")or "admin@local"
            telefono =input ("Teléfono [000000000]: ")or "000000000"
            direccion =input ("Dirección [N/A]: ")or "N/A"
            import datetime as _dt 
            fecha_inicio =_dt .date .today ()
            password =input ("Contraseña para el administrador (RH) [admin]: ")or "admin"
            while True :
                salario_str =input ("Salario del administrador (RH) (ej: 120000.00) [0]: ")or "0"
                try :
                    salario =float (salario_str )
                    break 
                except ValueError :
                    print ("Entrada inválida para salario. Ingrese un número (por ejemplo 50000 o 50000.00).")

            nuevo =Empleado (
            id =None ,
            nombre =nombre ,
            direccion =direccion ,
            telefono =telefono ,
            correo =correo ,
            fecha_inicio =fecha_inicio ,
            password_hash =password ,
            rol =rol_admin ,
            departamento_id =depto_id ,
            salario =salario 
            )

            creado_id =self .empleado_dao .crear (nuevo )
            if not creado_id :
                print ("Error al crear el administrador (RH) en la base de datos.")
                return False 

            creado =self .empleado_dao .buscar_por_id (creado_id )
            if creado :
                self .usuario_logueado =creado 
                return True 
            return False 
        except Exception as e :
            print (f"Error en creación interactiva de admin: {e }")
            return False 

    def crear_empleado_para_cuenta_interactivo (self )->Optional [tuple ]:

        try :
            deptos =self .depto_dao .listar ()
            if not deptos :
                print ("No hay departamentos configurados. Cree primero un departamento.")
                return None 
            print ("Departamentos disponibles:")
            for d in deptos :
                print (f"ID: {d .id } - {d .nombre }")
            try :
                depto_id =int (input ("Ingrese el ID del departamento al que se asociará el nuevo empleado: "))
            except ValueError :
                print ("ID inválido.")
                return None 
            if not self .depto_dao .buscar_por_id (depto_id ):
                print ("Departamento no encontrado.")
                return None 

            nombre =input ("Nombre del empleado: ")or "Empleado"
            correo =input ("Correo del empleado: ")or f"{nombre .replace (' ','').lower ()}@local"
            telefono =input ("Teléfono: ")or "000"
            direccion =input ("Dirección: ")or "N/A"
            import datetime as _dt 
            fecha_inicio =_dt .date .today ()
            password =input ("Contraseña para el empleado: ")or "changeme"

            while True :
                salario_str =input ("Salario del empleado (ej: 50000.00): ")or "0"
                try :
                    salario =float (salario_str )
                    break 
                except ValueError :
                    print ("Entrada inválida para salario. Intente de nuevo.")


            rol_obj = self.rol_dao.buscar_por_nombre("RH")
            if not rol_obj:
                print("El rol 'RH' no está configurado en el sistema. No se puede crear el empleado.")
                return None

            nuevo =Empleado (id =None ,nombre =nombre ,direccion =direccion ,telefono =telefono ,correo =correo ,fecha_inicio =fecha_inicio ,password_hash =password ,rol =rol_obj ,departamento_id =depto_id ,salario =salario )
            creado_id =self .empleado_dao .crear (nuevo )
            if not creado_id :
                print ("Error al crear empleado para la cuenta.")
                return None 
            creado = self .empleado_dao .buscar_por_id (creado_id )

            return (creado ,password )
        except Exception as e :
            print (f"Error al crear empleado para cuenta: {e }")
            return None

    def seleccionar_usuario (self )->bool :

        try :
            empleados =self .empleado_dao .listar ()
        except Exception as e :
            print (f"Error al obtener lista de empleados: {e }")
            return False 

        if not empleados :
            print ("No hay empleados registrados en el sistema. No se puede continuar sin un usuario.")
            return False 

        print ("\n--- Seleccione Usuario ---")
        for emp in empleados :
            rol_nombre =emp .rol .nombre if getattr (emp ,'rol',None )else 'N/A'
            print (f"ID: {emp .id }, Nombre: {emp .nombre }, Correo: {emp .correo }, Rol: {rol_nombre }")

        try :
            empleado_id =int (input ("Ingrese el ID del empleado con el que desea operar (0 para salir): "))
        except ValueError :
            print ("Entrada no válida.")
            return False 

        if empleado_id ==0 :
            return False 

        empleado =self .empleado_dao .buscar_por_id (empleado_id )
        if not empleado :
            print ("Empleado no encontrado.")
            return False 

        self .usuario_logueado =empleado 
        print (f"Usuario seleccionado: {self .usuario_logueado .nombre } | Rol: {getattr (self .usuario_logueado .rol ,'nombre','N/A')}")
        return True 

    def menu_principal (self ):

        if not self .usuario_logueado :
            print ("No ha iniciado sesión. Por favor reinicie y autentíquese. Saliendo del sistema.")
            return 

        while True :
            try :
                if os .name =='nt':
                    os .system ('cls')
                else :
                    os .system ('clear')
            except Exception :
                pass 
            time .sleep (0.2 )
            print ("\n--- Menú Principal ---")
            print (f"Usuario: {self .usuario_logueado .nombre } | Rol: {self .usuario_logueado .rol .nombre }")
            print ("1. Gestión de Empleados")
            print ("2. Gestión de Departamentos")
            print ("3. Gestión de Proyectos")
            print ("4. Registro de Tiempo")
            print ("5. Gestión de Informes")
            print ("0. Salir")

            opcion =input ("Seleccione una opción: ").strip ()

            if opcion =='1':
                self .gestion_de_empleados ()
            elif opcion =='2':
                self .gestion_de_departamentos ()
            elif opcion =='3':
                self .gestion_de_proyectos ()
            elif opcion =='4':
                self .registro_de_tiempo ()
            elif opcion =='5':
                self .gestion_de_informes ()
            elif opcion =='0':
                print ("Hasta luego.")
                break 
            else :
                print ("Opción no válida.")

    def gestion_de_empleados (self ):
        if self .usuario_logueado .rol .nombre not in ['RH','Gerente']:
            print ("Acceso denegado. Se requiere rol de Recursos Humanos (RH) o Gerente.")
            return 

        while True :
            try :
                if os .name =='nt':
                    os .system ('cls')
                else :
                    os .system ('clear')
            except Exception :
                pass 
            time .sleep (0.15 )
            print ("\n--- Gestión de Empleados ---")
            print ("1. Crear Empleado")
            print ("2. Listar Empleados")
            print ("3. Actualizar Empleado")
            print ("4. Eliminar Empleado")
            print ("0. Volver al Menú Principal")

            opcion =input ("Seleccione una opción: ").strip ()

            if opcion =='1':
                self .crear_empleado ()
            elif opcion =='2':
                self .listar_empleados ()
            elif opcion =='3':
                self .actualizar_empleado ()
            elif opcion =='4':
                self .eliminar_empleado ()
            elif opcion =='0':
                break 
            else :
                print ("Opción no válida.")

    def crear_empleado (self ):
        print ("\n--- Crear Empleado ---")
        nombre =input ("Nombre: ").strip ()
        direccion =input ("Dirección: ").strip ()
        telefono =input ("Teléfono: ").strip ()
        correo =input ("Correo electrónico: ").strip ()

        fecha_inicio =datetime .date .today ()
        password =input ("Contraseña (se almacenará como texto en DB en este modo): ").strip ()

        print ("\n--- Roles Disponibles ---")
        # Mostrar 'Gerente' solo si el usuario logueado es RH; de lo contrario, ocultarlo
        all_roles = self .rol_dao .listar () or []
        try:
            current_role = getattr(getattr(self, 'usuario_logueado', None), 'rol', None)
            current_role_name = getattr(current_role, 'nombre', '') if current_role else ''
        except Exception:
            current_role_name = ''
        if current_role_name == 'RH':
            roles = all_roles
        else:
            roles = [r for r in all_roles if getattr(r, 'nombre', '') != 'Gerente']
        if not roles:
            print("No hay roles disponibles para asignar. Operación cancelada.")
            return
        for rol in roles:
            print (f"ID: {rol .id }, Rol: {rol .nombre }")
        rol_id =int (input ("ID del Rol: ").strip ())
        rol_obj =self .rol_dao .buscar_por_id (rol_id )
        if not rol_obj :
            print ("Rol no encontrado. Operación cancelada.")
            return 

        print ("\n--- Departamentos Disponibles ---")
        departamentos =self .depto_dao .listar ()
        for depto in departamentos :
            print (f"ID: {depto .id }, Nombre: {depto .nombre }")
        departamento_id =int (input ("ID del Departamento: ").strip ())

        nuevo_empleado =Empleado (
        id =None ,nombre =nombre ,direccion =direccion ,telefono =telefono ,
        correo =correo ,fecha_inicio =fecha_inicio ,password_hash =password ,
        rol =rol_obj ,departamento_id =departamento_id 
        )
        if self .empleado_dao .crear (nuevo_empleado ):
            print ("Empleado creado exitosamente.")
        else :
            print ("Error al crear empleado.")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def listar_empleados (self ):
        print ("\n--- Listar Empleados ---")
        empleados =self .empleado_dao .listar ()
        if not empleados :
            print ("No hay empleados registrados.")
            input('\nPresione Enter para continuar...')
            return 
        for emp in empleados :
            print (f"ID: {emp .id }, Nombre: {emp .nombre }, Correo: {emp .correo }, Rol: {emp .rol .nombre }, Depto ID: {emp .departamento_id }")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def actualizar_empleado (self ):
        print ("\n--- Actualizar Empleado ---")
        self .listar_empleados ()
        empleado_id =int (input ("Ingrese el ID del empleado a actualizar: ").strip ())
        empleado_existente =self .empleado_dao .buscar_por_id (empleado_id )

        if not empleado_existente :
            print ("Empleado no encontrado.")
            return 

        print (f"Editando empleado: {empleado_existente .nombre }")
        empleado_existente .nombre =input (f"Nombre ({empleado_existente .nombre }): ").strip ()or empleado_existente .nombre 
        empleado_existente .direccion =input (f"Dirección ({empleado_existente .direccion }): ").strip ()or empleado_existente .direccion 
        empleado_existente .telefono =input (f"Teléfono ({empleado_existente .telefono }): ").strip ()or empleado_existente .telefono 
        empleado_existente .correo =input (f"Correo ({empleado_existente .correo }): ").strip ()or empleado_existente .correo 
        print(f"Fecha de Inicio (no modificable): {empleado_existente .fecha_inicio }")

        new_password =input ("Nueva Contraseña (dejar en blanco para no cambiar): ").strip ()
        if new_password :
            empleado_existente .password_hash =new_password 

        salario_str =input (f"Salario ({getattr (empleado_existente ,'salario',0 )}): ").strip ()
        if salario_str :
            try :
                empleado_existente .salario =float (salario_str )
            except ValueError :
                print ("Salario inválido, se mantiene el valor previo.")

        print ("\n--- Roles Disponibles ---")
        roles =self .rol_dao .listar ()
        for rol in roles :
            print (f"ID: {rol .id }, Rol: {rol .nombre }")
        rol_id_str =input (f"ID del Rol ({empleado_existente .rol .id }): ").strip ()
        if rol_id_str :
            try:
                rol_obj =self .rol_dao .buscar_por_id (int (rol_id_str ))
            except Exception:
                rol_obj =None
            if rol_obj :
                try:
                    if getattr(self.usuario_logueado, 'rol', None) and getattr(self.usuario_logueado.rol, 'nombre', '') == 'Gerente' and getattr(rol_obj, 'nombre', '') == 'Gerente':
                        print("No tienes permiso para asignar otro usuario como 'Gerente'. Se mantiene el rol actual.")
                    else:
                        empleado_existente .rol =rol_obj 
                except Exception:
                    print("No se pudo validar permisos de rol. Se mantiene el rol actual.")
            else :
                print ("Rol no encontrado. Se mantiene el rol actual.")

        print ("\n--- Departamentos Disponibles ---")
        departamentos =self .depto_dao .listar ()
        for depto in departamentos :
            print (f"ID: {depto .id }, Nombre: {depto .nombre }")
        departamento_id_str =input (f"ID del Departamento ({empleado_existente .departamento_id }): ").strip ()
        if departamento_id_str :
            empleado_existente .departamento_id =int (departamento_id_str )

        if self .empleado_dao .editar (empleado_existente ):
            print ("Empleado actualizado exitosamente.")
        else :
            print ("Error al actualizar empleado.")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def eliminar_empleado (self ):
        print ("\n--- Eliminar Empleado ---")
        self .listar_empleados ()
        empleado_id =int (input ("Ingrese el ID del empleado a eliminar: ").strip ())
        if self .empleado_dao .eliminar (empleado_id ):
            print ("Empleado eliminado exitosamente.")
        else :
            print ("Error al eliminar empleado.")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass


    def gestion_de_departamentos (self ):
        if self .usuario_logueado .rol .nombre not in ['RH','Gerente','Jefe de Proyecto']:
            print ("Acceso denegado.")
            try:
                input('\nPresione Enter para continuar...')
            except Exception:
                pass
            return 

        while True :
            try :
                if os .name =='nt':
                    os .system ('cls')
                else :
                    os .system ('clear')
            except Exception :
                pass 
            time .sleep (0.15 )
            print ("\n--- Gestión de Departamentos ---")
            print ("1. Crear Departamento")
            print ("2. Listar Departamentos")
            print ("3. Actualizar Departamento")
            print ("4. Eliminar Departamento")
            print ("5. Asignar Empleado a Departamento")
            print ("6. Asignar Gerente a Departamento")
            print ("0. Volver al Menú Principal")

            opcion =input ("Opción: ").strip ()

            if opcion =='1':
                self .crear_departamento ()
            elif opcion =='2':
                self .listar_departamentos ()
            elif opcion =='3':
                self .actualizar_departamento ()
            elif opcion =='4':
                self .eliminar_departamento ()
            elif opcion =='5':
                self .asignar_empleado_a_departamento ()
            elif opcion =='6':
                self .asignar_gerente_a_departamento ()
            elif opcion =='0':
                break 
            else :
                print ("Opción no válida.")
                try:
                    input('\nPresione Enter para continuar...')
                except Exception:
                    pass

    def crear_departamento (self ):
        print ("\n--- Crear Departamento ---")
        nombre =input ("Ingrese nombre del nuevo departamento: ")

        asignar =input ("¿Asignar un gerente ahora? (s/n): ").lower ()
        manager_id =None 
        if asignar =='s':
            empleados =self .empleado_dao .listar ()
            if not empleados :
                print ("No hay empleados para asignar como gerente.")
            else :
                print ("Empleados disponibles:")
                for e in empleados :
                    print (f"ID: {e .id } - {e .nombre } (Rol: {getattr (e .rol ,'nombre','N/A')})")
                try :
                    candidate_id =int (input ("Ingrese ID del empleado a asignar como gerente: "))
                    candidato =self .empleado_dao .buscar_por_id (candidate_id )
                    if not candidato :
                        print ("Empleado no encontrado. No se asignará gerente.")
                    elif not getattr (candidato .rol ,'nombre','')=='Gerente':
                        print ("El empleado seleccionado no tiene rol 'Gerente'. No se puede asignar como gerente.")
                    else :
                        manager_id =candidate_id 
                except ValueError :
                    manager_id =None 
        nuevo_depto =Departamento (id =None ,nombre =nombre ,manager_id =manager_id )
        if self .depto_dao .crear (nuevo_depto ):
            print (f"Departamento '{nombre }' creado con éxito.")
        else :
            print ("Error al crear departamento.")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def listar_departamentos (self ):
        print ("\n--- Listar Departamentos ---")
        lista_deptos =self .depto_dao .listar ()
        if not lista_deptos :
            print ("No hay departamentos registrados.")
            try:
                input('\nPresione Enter para continuar...')
            except Exception:
                pass
            return 
        for depto in lista_deptos :
            print (f"ID: {depto .id }, Nombre: {depto .nombre }")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def actualizar_departamento (self ):
        print ("\n--- Actualizar Departamento ---")
        self .listar_departamentos ()
        depto_id =int (input ("Ingrese el ID del departamento a actualizar: "))
        depto_existente =self .depto_dao .buscar_por_id (depto_id )

        if not depto_existente :
            print ("Departamento no encontrado.")
            return 

        print (f"Editando departamento: {depto_existente .nombre }")
        depto_existente .nombre =input (f"Nombre ({depto_existente .nombre }): ")or depto_existente .nombre 

        change_mgr =input ("¿Cambiar/establecer gerente? (s/n): ").lower ()
        if change_mgr =='s':
            empleados =self .empleado_dao .listar ()
            if not empleados :
                print ("No hay empleados para asignar como gerente.")
            else :
                print ("Empleados disponibles:")
                for e in empleados :
                    print (f"ID: {e .id } - {e .nombre } (Rol: {getattr (e .rol ,'nombre','N/A')})")
                try :
                    mgr_id =int (input ("Ingrese ID del empleado a asignar como gerente (0 para quitar): "))
                except ValueError :
                    mgr_id =None 
                if mgr_id ==0 :
                    depto_existente .manager_id =None 
                elif mgr_id :

                    candidato =self .empleado_dao .buscar_por_id (mgr_id )
                    if not candidato :
                        print ("Empleado no encontrado. No se cambiará el gerente.")
                    elif not getattr (candidato .rol ,'nombre','')=='Gerente':
                        print ("El empleado seleccionado no tiene rol 'Gerente'. No se puede asignar como gerente.")
                    else :

                        if getattr (depto_existente ,'manager_id',None ):
                            confirm =input (f"Este departamento ya tiene manager (ID {depto_existente .manager_id }). ¿Desea reemplazarlo? (s/n): ").lower ()
                            if confirm !='s':
                                print ("No se reemplazó el manager existente.")
                            else :
                                depto_existente .manager_id =mgr_id 
                        else :
                            depto_existente .manager_id =mgr_id 

        if self .depto_dao .editar (depto_existente ):
            print ("Departamento actualizado exitosamente.")
        else :
            print ("Error al actualizar departamento.")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def eliminar_departamento (self ):
        print ("\n--- Eliminar Departamento ---")
        self .listar_departamentos ()
        depto_id =int (input ("Ingrese el ID del departamento a eliminar: "))
        if self .depto_dao .eliminar (depto_id ):
            print ("Departamento eliminado exitosamente.")
        else :
            print ("Error al eliminar departamento.")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def asignar_gerente_a_departamento (self ):
        print ("\n--- Asignar Gerente a Departamento ---")
        # Elegir departamento
        self .listar_departamentos ()
        try :
            depto_id =int (input ("ID del Departamento: ").strip ())
        except Exception :
            print ("ID de departamento inválido.")
            try:
                input('\nPresione Enter para continuar...')
            except Exception:
                pass
            return 
        depto =self .depto_dao .buscar_por_id (depto_id )
        if not depto :
            print ("Departamento no encontrado.")
            try:
                input('\nPresione Enter para continuar...')
            except Exception:
                pass
            return 

        # Listar únicamente empleados con rol 'Gerente'
        try :
            empleados =self .empleado_dao .listar () or []
        except Exception :
            empleados =[]
        gerentes =[e for e in empleados if getattr (getattr (e ,'rol',None ),'nombre','')=='Gerente']
        if not gerentes :
            print ("No hay empleados con rol 'Gerente' disponibles.")
            try:
                input('\nPresione Enter para continuar...')
            except Exception:
                pass
            return 
        print ("Empleados con rol 'Gerente':")
        for g in gerentes :
            print (f"  ID: {g .id } - {g .nombre } (Correo: {g .correo })")
        try :
            gerente_id =int (input ("ID del Gerente a asignar: ").strip ())
        except Exception :
            print ("ID inválido.")
            try:
                input('\nPresione Enter para continuar...')
            except Exception:
                pass
            return 

        candidato =self .empleado_dao .buscar_por_id (gerente_id )
        if not candidato or getattr (getattr (candidato ,'rol',None ),'nombre','')!='Gerente':
            print ("El empleado seleccionado no tiene rol 'Gerente'.")
            try:
                input('\nPresione Enter para continuar...')
            except Exception:
                pass
            return 

        # Confirmación si ya existe gerente
        if getattr (depto ,'manager_id',None ):
            try :
                confirm =input (f"Este departamento ya tiene manager (ID {depto .manager_id }). ¿Desea reemplazarlo? (s/n): ").strip ().lower ()
            except Exception :
                confirm ='n'
            if confirm !='s':
                print ("Operación cancelada, no se reemplazó el gerente.")
                try:
                    input('\nPresione Enter para continuar...')
                except Exception:
                    pass
                return 

        depto .manager_id =gerente_id 
        if self .depto_dao .editar (depto ):
            print ("Gerente asignado exitosamente al departamento.")
        else :
            print ("Error al asignar gerente al departamento.")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def gestion_de_proyectos (self ):
        if self .usuario_logueado .rol .nombre not in ['RH','Gerente','Jefe de Proyecto']:
            print ("Acceso denegado.")
            try:
                input('\nPresione Enter para continuar...')
            except Exception:
                pass
            return 

        while True :
            try :
                if os .name =='nt':
                    os .system ('cls')
                else :
                    os .system ('clear')
            except Exception :
                pass 
            time .sleep (0.15 )
            print ("\n--- Gestión de Proyectos ---")
            print ("1. Crear Proyecto")
            print ("2. Listar Proyectos")
            print ("3. Actualizar Proyecto")
            print ("4. Eliminar Proyecto")
            print ("5. Asignar Empleado a Proyecto")
            print ("0. Volver al Menú Principal")

            opcion =input ("Opción: ")

            if opcion =='1':
                self .crear_proyecto ()
            elif opcion =='2':
                self .listar_proyectos ()
            elif opcion =='3':
                self .actualizar_proyecto ()
            elif opcion =='4':
                self .eliminar_proyecto ()
            elif opcion =='5':
                self .asignar_empleado_a_proyecto ()
            elif opcion =='0':
                break 
            else :
                print ("Opción no válida.")

    def crear_proyecto (self ):
        print ("\n--- Crear Proyecto ---")
        nombre =input ("Nombre del Proyecto: ")
        fecha_inicio =self .parse_date_input ("Fecha de Inicio (YYYY-MM-DD): ")
        fecha_fin =self .parse_date_input ("Fecha de Fin (YYYY-MM-DD): ")

        nuevo_proyecto =Proyecto (
        id =None ,nombre =nombre ,fecha_inicio =fecha_inicio ,fecha_fin =fecha_fin 
        )
        if self .proyecto_dao .crear (nuevo_proyecto ):
            print ("Proyecto creado exitosamente.")
        else :
            print ("Error al crear proyecto.")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def listar_proyectos (self ):
        print ("\n--- Listar Proyectos ---")
        proyectos =self .proyecto_dao .listar ()
        if not proyectos :
            print ("No hay proyectos registrados.")
            try:
                input('\nPresione Enter para continuar...')
            except Exception:
                pass
            return 
        for proj in proyectos :
            print (f"ID: {proj .id }, Nombre: {proj .nombre }, Inicio: {proj .fecha_inicio }, Fin: {proj .fecha_fin }")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def actualizar_proyecto (self ):
        print ("\n--- Actualizar Proyecto ---")
        self .listar_proyectos ()
        proyecto_id =int (input ("Ingrese el ID del proyecto a actualizar: "))
        proyecto_existente =self .proyecto_dao .buscar_por_id (proyecto_id )

        if not proyecto_existente :
            print ("Proyecto no encontrado.")
            return 

        print (f"Editando proyecto: {proyecto_existente .nombre }")
        proyecto_existente .nombre =input (f"Nombre ({proyecto_existente .nombre }): ")or proyecto_existente .nombre 
        fecha_inicio_str =input (f"Fecha de Inicio (YYYY-MM-DD) ({proyecto_existente .fecha_inicio }): ")
        if fecha_inicio_str :
            try :
                proyecto_existente .fecha_inicio =self .parse_date_input ("",allow_empty =False ) if False else datetime .datetime .strptime (fecha_inicio_str ,"%Y-%m-%d").date ()
            except Exception :
                try :
                    proyecto_existente .fecha_inicio =self .parse_date_input (f"(Reintente) Fecha de Inicio: ")
                except Exception :
                    print ("Fecha de inicio inválida, se mantiene el valor previo.")
        fecha_fin_str =input (f"Fecha de Fin (YYYY-MM-DD) ({proyecto_existente .fecha_fin }): ")
        if fecha_fin_str :
            try :
                proyecto_existente .fecha_fin =self .parse_date_input ("",allow_empty =False ) if False else datetime .datetime .strptime (fecha_fin_str ,"%Y-%m-%d").date ()
            except Exception :
                try :
                    proyecto_existente .fecha_fin =self .parse_date_input (f"(Reintente) Fecha de Fin: ")
                except Exception :
                    print ("Fecha de fin inválida, se mantiene el valor previo.")

        if self .proyecto_dao .editar (proyecto_existente ):
            print ("Proyecto actualizado exitosamente.")
        else :
            print ("Error al actualizar proyecto.")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def eliminar_proyecto (self ):
        print ("\n--- Eliminar Proyecto ---")
        self .listar_proyectos ()
        proyecto_id =int (input ("Ingrese el ID del proyecto a eliminar: "))
        if self .proyecto_dao .eliminar (proyecto_id ):
            print ("Proyecto eliminado exitosamente.")
        else :
            print ("Error al eliminar proyecto.")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def asignar_empleado_a_proyecto (self ):
        print ("\n--- Asignar Empleado a Proyecto ---")
        self .listar_empleados ()
        empleado_id =int (input ("ID del Empleado: "))
        self .listar_proyectos ()
        proyecto_id =int (input ("ID del Proyecto: "))



        if self .empleado_dao .asignar_empleado_a_proyecto (empleado_id ,proyecto_id ):
            print ("Asignación lógica de empleado a proyecto confirmada.")
        else :
            print ("Error en la asignación lógica de empleado a proyecto.")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def registro_de_tiempo (self ):
        if self .usuario_logueado .rol .nombre not in ['RH','Gerente','Jefe de Proyecto','Desarrollador']:
            print ("Acceso denegado.")
            try:
                input('\nPresione Enter para continuar...')
            except Exception:
                pass
            return 

        while True :
            try :
                if os .name =='nt':
                    os .system ('cls')
                else :
                    os .system ('clear')
            except Exception :
                pass 
            time .sleep (0.15 )
            print ("\n--- Registro de Tiempo ---")
            print ("1. Registrar Horas")
            print ("2. Ver Mis Registros de Tiempo")
            print ("0. Volver al Menú Principal")

            opcion =input ("Opción: ")

            if opcion =='1':
                self .registrar_horas ()
            elif opcion =='2':
                self .ver_mis_registros_tiempo ()
            elif opcion =='0':
                break 
            else :
                print ("Opción no válida.")

    def registrar_horas (self ):
        print ("\n--- Registrar Horas ---")
        self .listar_proyectos ()
        proyecto_id =int (input ("ID del Proyecto: "))
        fecha =self .parse_date_input ("Fecha (YYYY-MM-DD): ")
        horas_trabajadas =float (input ("Horas trabajadas: "))
        descripcion =input ("Descripción del trabajo: ")

        nuevo_registro =RegistroTiempo (
        id =None ,
        empleado_id =self .usuario_logueado .id ,
        proyecto_id =proyecto_id ,
        fecha =fecha ,
        horas_trabajadas =horas_trabajadas ,
        descripcion =descripcion 
        )
        if self .registro_tiempo_dao .crear (nuevo_registro ):
            print ("Registro de tiempo creado exitosamente.")
        else :
            print ("Error al crear registro de tiempo.")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def ver_mis_registros_tiempo (self ):
        print ("\n--- Mis Registros de Tiempo ---")
        registros =self .registro_tiempo_dao .listar_por_empleado (self .usuario_logueado .id )
        if not registros :
            print ("No tienes registros de tiempo.")
            try:
                input('\nPresione Enter para continuar...')
            except Exception:
                pass
            return 
        for reg in registros :
            proyecto =self .proyecto_dao .buscar_por_id (reg .proyecto_id )
            proyecto_nombre =proyecto .nombre if proyecto else "N/A"
            print (f"ID: {reg .id }, Proyecto: {proyecto_nombre }, Fecha: {reg .fecha }, Horas: {reg .horas_trabajadas }, Descripción: {reg .descripcion }")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass

    def gestion_de_informes (self ):
        if self .usuario_logueado .rol .nombre not in ['RH','Gerente','Jefe de Proyecto']:
            print ("Acceso denegado.")
            try:
                input('\nPresione Enter para continuar...')
            except Exception:
                pass
            return 

        while True :
            try :
                if os .name =='nt':
                    os .system ('cls')
                else :
                    os .system ('clear')
            except Exception :
                pass 
            time .sleep (0.15 )
            print ("\n--- Gestión de Informes ---")
            print ("1. Ver Informe de Empleado")
            print ("0. Volver al Menú Principal")

            opcion =input ("Opción: ")

            if opcion =='1':
                self .ver_horas_por_empleado ()
            elif opcion =='0':
                break 
            else :
                print ("Opción no válida.")

    def ver_horas_por_empleado (self ):
        print ("\n--- Informe por Empleado ---")
        # Mostrar lista de empleados para que el usuario pueda elegir
        print('\nEmpleados disponibles:')
        empleados = self .empleado_dao .listar ()
        for emp in empleados:
            rol_nombre = emp .rol .nombre if getattr(emp, 'rol', None) else 'N/A'
            print(f"  ID: {emp .id } - {emp .nombre } (Correo: {emp .correo }, Rol: {rol_nombre })")

        try:
            empleado_id =int (input ("\nIngrese el ID del empleado para ver el informe: ").strip ())
        except Exception:
            print("ID inválido.")
            return

        empleado =self .empleado_dao .buscar_por_id (empleado_id )
        if not empleado :
            print ("Empleado no encontrado.")
            return 

        departamento =None
        try:
            if getattr(empleado,'departamento_id',None):
                departamento =self .depto_dao .buscar_por_id (empleado .departamento_id )
        except Exception:
            departamento =None

        registros =self .registro_tiempo_dao.listar_por_empleado (empleado_id ) or []
        # Proyectos asignados en la tabla intermedia
        try:
            proyectos_asignados = self .proyecto_dao .listar_por_empleado (empleado_id ) or []
        except Exception:
            proyectos_asignados = []

        horas_por_proyecto = {}
        total_horas = 0
        # Sumar horas por proyecto desde registros de tiempo
        for reg in registros:
            pid = reg .proyecto_id
            horas_por_proyecto.setdefault(pid, 0)
            horas_por_proyecto[pid] += reg .horas_trabajadas or 0
            total_horas += reg .horas_trabajadas or 0

        # Asegurar que los proyectos asignados aparezcan aunque tengan 0 horas
        for p in proyectos_asignados:
            horas_por_proyecto.setdefault(getattr(p, 'id', None), 0)

        print(f"\nEmpleado: {empleado .nombre } (ID: {empleado .id })")
        print(f"Correo: {empleado .correo }")
        print(f"Departamento: {departamento .nombre if departamento else 'N/A'} (ID: {getattr(empleado,'departamento_id', 'N/A')})")
        print("\nProyectos y horas:")
        if not horas_por_proyecto and not proyectos_asignados:
            print("  No hay proyectos asignados ni registros de tiempo para este empleado.")
        else:
            # Mostrar todos los proyectos del dict (que incluye asignados y los con registros)
            for pid, horas in horas_por_proyecto.items():
                proyecto = self .proyecto_dao .buscar_por_id(pid) if pid else None
                nombre_proy = proyecto .nombre if proyecto else 'N/A'
                print(f"  - Proyecto: {nombre_proy} (ID: {pid}) -> Horas: {horas}")

        print(f"\nTotal de horas registradas: {total_horas}")
        try:
            input('\nPresione Enter para continuar...')
        except Exception:
            pass



if __name__ =="__main__":
    app =Main ()
    app .menu_principal ()
