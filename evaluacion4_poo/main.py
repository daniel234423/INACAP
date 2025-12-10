import os
import time
import getpass
import bcrypt

from DAO.CrudDestino import CrudDestino
from DAO.CrudRol import CrudRol
from DAO.CrudUsuario import CrudUsuario
from DTO.Destino import Destino
from DTO.Usuario import Usuario

usuario_sesion = None

def Login():
    print("----------------------------- LOGIN -----------------------------")
    print("Bienvenido a la plataforma de gestión de viajes y reservas.")
    print("Elija una opción:")
    print("1. Iniciar sesión")
    print("2. Registrarse")
    print("3.- Registrarse como Administrador (Solo para pruebas): ")
    print("4. Salir")
    try:
        opcion = int(input("Ingrese el número de la opción deseada: "))
        if opcion == 1:
            iniciar_sesion()
        elif opcion == 2:
            registrar_usuario()
        elif opcion == 3:
            registrar_administrador()
        elif opcion == 4:
            print("Gracias por usar la plataforma. ¡Hasta luego!")
            exit()
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
    except Exception as e:
        print(f"Ocurrió un error: {e}. Por favor, intente de nuevo.")


def registrar_administrador():
    print("Bienvenido al registro de administrador ")
    try:
        print("Para ingresar a el registro de administrador, por favor ingrese la contraseña maestra.")
        master_password = getpass.getpass("Contraseña maestra: ")
        if master_password != "admin123":
            print("Contraseña maestra incorrecta. Acceso denegado.")
            return
        nombre = input("Ingrese su nombre: ")
        apellido = input("Ingrese su apellido: ")
        email = input("Ingrese su email: ")
        run = input("Ingrese su RUN: ")
        fono = input("Ingrese su teléfono: ")
        username = input("Ingrese su nombre de usuario: ")
        password = getpass.getpass("Ingrese su contraseña: ")
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        print("Registrando administrador...")
        CrudUsuario().AgregarUsuario(Usuario(
            id=None,
            nombre=nombre,
            apellido=apellido,
            email=email,
            run=run,
            fono=fono,
            username=username,
            hash_password=password_hash,
            rol=CrudRol().obtener_rol("Administrador")
        ))
        print("Registro de administrador completado con éxito.")
    except Exception as e:
        print(f"Error durante el registro de administrador: {e}")

def registrar_usuario():
    try:
        print("Bienvenido a su registro de usuario")
        nombre = input("Ingrese su nombre: ")
        apellido = input("Ingrese su apellido: ")
        email = input("Ingrese su email: ")
        run = input("Ingrese su RUN: ")
        fono = input("Ingrese su teléfono: ")
        username = input("Ingrese su nombre de usuario: ")
        password = getpass.getpass("Ingrese su contraseña: ")
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        print("Registrando usuario...")
        print(CrudRol().obtener_rol("Cliente"))
        CrudUsuario().AgregarUsuario(Usuario(
            id=None,
            nombre=nombre,
            apellido=apellido,
            email=email,
            run=run,
            fono=fono,
            username=username,
            hash_password=password_hash,
            rol=CrudRol().obtener_rol("Cliente")
        ))
        print("Registro completado con éxito.")
        global usuario_sesion
        usuario_sesion = CrudUsuario().ObtenerUsuarioPorUsername(username)
        time.sleep(3)
        os.system('cls')
    except Exception as e:
        print(f"Error durante el registro: {e}")

def iniciar_sesion():
    print("Iniciar sesión en la plataforma")
    username = input("Ingrese su nombre de usuario: ")
    password = getpass.getpass("Ingrese su contraseña: ")
    usuario = CrudUsuario().IniciarSesion(username, password)
    if usuario:
        print(f"Inicio de sesión exitoso. Bienvenido, {usuario.nombre}!")
        global usuario_sesion
        usuario_sesion = usuario
        time.sleep(3)
        os.system('cls')
    else:
        print("Credenciales incorrectas. Intente nuevamente.")
        time.sleep(2)


def GestionarDestinos():
    print("----- Gestión de Destinos -----")
    print("1.- Crear Nuevo Destino\n2.- Volver al Menú Anterior")
    try:
        opcion = int(input("Seleccione una opción: "))
        if opcion == 1:
            nombre = input("Ingrese el nombre del destino: ")
            descripcion = input("Ingrese la descripción del destino: ")
            actividades = input("Ingrese las actividades del destino (Separadas por comas): ")
            costo = float(input("Ingrese el costo del destino: "))
            CrudDestino().crear_destino(Destino(
                id_destino=None,
                nombre=nombre,
                descripcion=descripcion,
                actividades=actividades,
                costo=costo
            ), usuario_sesion.rol._id_rol)
            print("Destino creado con éxito.")
        elif opcion == 2:
            print("Volviendo al menú anterior...")
            time.sleep(2)
            os.system('cls')
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
    except Exception as e:
        print(f"Ocurrió un error: {e}. Por favor, intente de nuevo.")

def MenuAdministrador():
    print("----- Menú Administrador -----")
    print("---------- Bienvendio a su menú, Administrador ----------")
    print("1.- Gestionar Destinos\n2.- Gestionar Paquetes Turísticos\n3.- Ver Reservas\n4.- Cerrar Sesión")
    try:
        opcion = int(input("Seleccione una opción: "))
        if opcion == 1:
            GestionarDestinos()
        elif opcion == 2:
            print("Funcionalidad de Gestión de Paquetes Turísticos en desarrollo...")
        elif opcion == 3:
            print("Funcionalidad de Ver Reservas en desarrollo...")
        elif opcion == 4:
            print("Cerrando sesión...")
            global usuario_sesion
            usuario_sesion = None
            time.sleep(2)
            os.system('cls')
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
    except Exception as e:
        print(f"Ocurrió un error: {e}. Por favor, intente de nuevo.")   

while True:
    try:
        if usuario_sesion:
            if usuario_sesion.rol._id_rol == 1:
                MenuAdministrador()
        else:
            Login()
        time.sleep(3)
        os.system('cls')
    except Exception as e:
        print(f"Ocurrió un error: {e}. Por favor, intente de nuevo.")