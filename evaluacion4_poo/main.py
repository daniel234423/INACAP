import os
import time
import getpass
import bcrypt
from datetime import datetime

from DAO.CrudDestino import CrudDestino
from DAO.CrudPaqueteTuristico import CrudPaquete
from DAO.CrudReserva import CrudReserva
from DAO.CrudRol import CrudRol
from DAO.CrudUsuario import CrudUsuario
from DAO.ApiCambioMoneda import ApiCambioMoneda
from DTO.PaqueteTurictico import PaqueteTurictico
from DTO.Destino import Destino
from DTO.Usuario import Usuario

usuario_sesion: Usuario | None = None
moneda_seleccionada = {"nombre": "CLP", "indicador": None, "simbolo": "$", "tasa": 1.0}


def _a_datetime(valor):
    """Convierte fechas de la BD (date, datetime o str) a datetime segura."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    try:
        return datetime.fromisoformat(str(valor))
    except Exception:
        try:
            return datetime.strptime(str(valor), "%Y-%m-%d")
        except Exception:
            return None

def Login():
    print("----------------------------- LOGIN -----------------------------")
    print("Bienvenido a la plataforma de gestión de viajes y reservas.")
    print("Elija una opción:")
    print("1. Iniciar sesión")
    print("2. Registrarse")
    print("3. Registrarse como Administrador (Solo para pruebas): ")
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
        CrudUsuario().Registrarse(Usuario(
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
        CrudUsuario().Registrarse(Usuario(
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
        usuario_sesion = CrudUsuario().Mostrar(username)
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
        time.sleep(2)
        os.system('cls')
    else:
        print("Credenciales incorrectas. Intente nuevamente.")
        time.sleep(2)

def actualizar_destino():
    try:
        destinos = CrudDestino().Mostrar()
        print("----- Lista de Destinos -----")
        for destino in destinos:
            print(f"ID: {destino._id_destino}, Nombre: {destino._nombre}, Descripción: {destino._descripcion}, Actividades: {destino._actividades}, Costo: {destino._costo}")
        id_destino = int(input("Ingrese el ID del destino que desea actualizar: "))
        destino_seleccionado = next((d for d in destinos if d._id_destino == id_destino), None)
        if not destino_seleccionado:
            print("Destino no encontrado. Por favor, intente de nuevo.")
            return
        nuevo_nombre = input(f"Ingrese el nuevo nombre (actual: {destino_seleccionado._nombre}) si no quiere cambiarlo presione Enter: ") or destino_seleccionado._nombre
        nueva_descripcion = input(f"Ingrese la nueva descripción (actual: {destino_seleccionado._descripcion}) si no quiere cambiarla presione Enter: ") or destino_seleccionado._descripcion
        nuevas_actividades = input(f"Ingrese las nuevas actividades (actual: {destino_seleccionado._actividades}) si no quiere cambiarlas presione Enter: ") or destino_seleccionado._actividades
        nuevo_costo_input = input(f"Ingrese el nuevo costo (actual: {destino_seleccionado._costo}) si no quiere cambiarlo presione Enter: ")
        nuevo_costo = float(nuevo_costo_input) if nuevo_costo_input else destino_seleccionado._costo
        destino_actualizado = Destino(
            id_destino=id_destino,
            nombre=nuevo_nombre,
            descripcion=nueva_descripcion,
            actividades=nuevas_actividades,
            costo=nuevo_costo
        )
        exito = CrudDestino().Modificar(destino_actualizado, usuario_sesion.rol._id_rol)
        if exito:
            print("Destino actualizado con éxito.")
        else:
            print("No se pudo actualizar el destino. Por favor, intente de nuevo.")
    except Exception as e:
        print(f"Ocurrió un error al actualizar el destino: {e}. Por favor, intente de nuevo.")

def eliminar_destino():
    try:
        destinos = CrudDestino().Mostrar()
        print("----- Lista de Destinos -----")
        for destino in destinos:
            print(f"ID: {destino._id_destino}, Nombre: {destino._nombre}, Descripción: {destino._descripcion}, Actividades: {destino._actividades}, Costo: {destino._costo}")
        id_destino = int(input("Ingrese el ID del destino que desea eliminar: "))
        confirmacion = input("¿Está seguro que desea eliminar este destino? (s/n): ")
        if confirmacion.lower() != 's':
            print("Eliminación cancelada.")
            return
        exito = CrudDestino().Eliminar(id_destino, usuario_sesion.rol._id_rol)
        if exito:
            print("Destino eliminado con éxito.")
        else:
            print("No se pudo eliminar el destino. Por favor, intente de nuevo.")
    except Exception as e:
        print(f"Ocurrió un error al eliminar el destino: {e}. Por favor, intente de nuevo.")

def ver_destinos():
    try:
        time.sleep(1)
        os.system('cls')
        destinos = CrudDestino().Mostrar()
        print("================ DESTINOS ================")
        if destinos == []:
            print("No hay destinos para mostrar.")
            input("Presione Enter para volver al menú anterior...")
            os.system('cls')
            return
        print(f"{'ID':<4} {'Nombre':<22} {'Costo (CLP)':>12}")
        print("-" * 48)
        for destino in destinos:
            costo_txt = f"$ {destino._costo:,.0f}" if destino._costo is not None else "Sin costo"
            print(f"{destino._id_destino:<4} {destino._nombre:<22} {costo_txt:>12}")
            print(f"    Actividades: {destino._actividades}")
            print(f"    Descripción: {destino._descripcion}")
            print("-" * 48)
        input("Presione Enter para volver al menú anterior...")
        os.system('cls')
    except Exception as e:
        print(f"Ocurrió un error al obtener los destinos: {e}. Por favor, intente de nuevo.")

def GestionarDestinos():
    time.sleep(1)
    os.system('cls')
    print("----- Gestión de Destinos -----")
    print("1.- Crear Nuevo Destino\n2.- Ver destinos\n3.- Editar destino existente\n4.- Eliminar destino\n5.- Volver al menú anterior")
    try:
        opcion = int(input("Seleccione una opción: "))
        if opcion == 1:
            nombre = input("Ingrese el nombre del destino: ")
            descripcion = input("Ingrese la descripción del destino: ")
            actividades = input("Ingrese las actividades del destino (Separadas por comas): ")
            costo = float(input("Ingrese el costo del destino: "))
            CrudDestino().Agregar(Destino(
                id_destino=None,
                nombre=nombre,
                descripcion=descripcion,
                actividades=actividades,
                costo=costo
            ), usuario_sesion.rol._id_rol)
            print("Destino creado con éxito.")
        elif opcion == 2:
            ver_destinos()
        elif opcion == 3:
            actualizar_destino()
        elif opcion == 4:
            eliminar_destino()
        elif opcion == 5:
            print("Volviendo al menú anterior...")
            time.sleep(2)
            os.system('cls')
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
    except Exception as e:
        print(f"Ocurrió un error: {e}. Por favor, intente de nuevo.")



def parse_fecha(fecha_str: str) -> str:
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(fecha_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD o DD-MM-YYYY.")

def Agregar():
    try:
        nombre = input("Ingrese el nombre del paquete turístico: ")
        fecha_inicio_raw = input("Ingrese la fecha de inicio (YYYY-MM-DD o DD-MM-YYYY): ")
        fecha_fin_raw = input("Ingrese la fecha de fin (YYYY-MM-DD o DD-MM-YYYY): ")


        fecha_inicio = parse_fecha(fecha_inicio_raw)
        fecha_fin = parse_fecha(fecha_fin_raw)
        
        destinos = CrudDestino().Mostrar()
        print("----- Lista de Destinos -----")
        for destino in destinos:
            print(f"ID: {destino._id_destino}, Nombre: {destino._nombre}, Descripción: {destino._descripcion}, Actividades: {destino._actividades}, Costo: {destino._costo}")
        
        cantidad_destinos = int(input("¿Cuántos destinos desea agregar al paquete?: "))
        destinos_seleccionados = []
        
        for i in range(cantidad_destinos):
            id_destino = int(input(f"Ingrese el ID del destino {i+1}: "))
            destino_seleccionado = next((d for d in destinos if d._id_destino == id_destino), None)
            if destino_seleccionado:
                destinos_seleccionados.append(destino_seleccionado)
            else:
                print(f"Destino con ID {id_destino} no encontrado.")
        
        paquete_turistico = PaqueteTurictico(
            id_paquete=None,
            nombre=nombre,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            destinos=destinos_seleccionados
        )
        id_paquete = CrudPaquete().Agregar(paquete_turistico)
        if id_paquete:
            print(f"Paquete turístico creado con éxito. ID del paquete: {id_paquete}")
            time.sleep(3)
            os.system('cls')
        else:
            print("No se pudo crear el paquete turístico. Por favor, intente de nuevo.")
            time.sleep(3)
            os.system('cls')
    except Exception as e:
        print(f"Ocurrió un error al crear el paquete turístico: {e}. Por favor, intente de nuevo.")

def editar_paquete():
    try:
        paquetes = CrudPaquete().Mostrar()
        print("----- Lista de Paquetes Turísticos -----")
        for paquete in paquetes:
            print(f"ID: {paquete.id_paquete}, Nombre: {paquete.nombre}, Fecha Inicio: {paquete.fecha_inicio}, Fecha Fin: {paquete.fecha_fin}, Precio: {paquete.precio}")
        
        id_paquete = int(input("Ingrese el ID del paquete turístico que desea editar: "))
        paquete_seleccionado = next((p for p in paquetes if p.id_paquete == id_paquete), None)
        if not paquete_seleccionado:
            print("Paquete turístico no encontrado. Por favor, intente de nuevo.")
            return
        
        nuevo_nombre = input(f"Ingrese el nuevo nombre (actual: {paquete_seleccionado.nombre}) si no quiere cambiarlo presione Enter: ") or paquete_seleccionado.nombre
        nueva_fecha_inicio_raw = input(f"Ingrese la nueva fecha de inicio (actual: {paquete_seleccionado.fecha_inicio}) si no quiere cambiarla presione Enter: ")
        nueva_fecha_fin_raw = input(f"Ingrese la nueva fecha de fin (actual: {paquete_seleccionado.fecha_fin}) si no quiere cambiarla presione Enter: ")
        
        nueva_fecha_inicio = parse_fecha(nueva_fecha_inicio_raw) if nueva_fecha_inicio_raw else paquete_seleccionado.fecha_inicio
        nueva_fecha_fin = parse_fecha(nueva_fecha_fin_raw) if nueva_fecha_fin_raw else paquete_seleccionado.fecha_fin
        
        destinos = CrudDestino().Mostrar()
        print("----- Lista de Destinos -----")
        for destino in destinos:
            print(f"ID: {destino._id_destino}, Nombre: {destino._nombre}, Descripción: {destino._descripcion}, Actividades: {destino._actividades}, Costo: {destino._costo}")
        
        cantidad_destinos = int(input("¿Cuántos destinos desea agregar al paquete? (Ingrese 0 para no cambiar): "))
        destinos_seleccionados = None
        
        if cantidad_destinos > 0:
            destinos_seleccionados = []
            for i in range(cantidad_destinos):
                id_destino = int(input(f"Ingrese el ID del destino {i+1}: "))
                destino_seleccionado = next((d for d in destinos if d._id_destino == id_destino), None)
                if destino_seleccionado:
                    destinos_seleccionados.append(destino_seleccionado)
                else:
                    print(f"Destino con ID {id_destino} no encontrado.")
        paquete_actualizado = PaqueteTurictico(
            id_paquete=id_paquete,
            nombre=nuevo_nombre,
            fecha_inicio=nueva_fecha_inicio,
            fecha_fin=nueva_fecha_fin,
            destinos=destinos_seleccionados
        )
        exito = CrudPaquete().Modificar(paquete_actualizado)
        if exito:
            print("Paquete turístico actualizado con éxito.")
            time.sleep(3)
            os.system('cls')
        else:
            print("No se pudo actualizar el paquete turístico. Por favor, intente de nuevo.")
            time.sleep(3)
            os.system('cls')
    except Exception as e:
        print(f"Ocurrió un error al editar el paquete turístico: {e}. Por favor, intente de nuevo.")


def eliminar_paquete():
    try:
        paquetes = CrudPaquete().Mostrar()
        print("----- Lista de Paquetes Turísticos -----")
        for paquete in paquetes:
            print(f"ID: {paquete.id_paquete}, Nombre: {paquete.nombre}, Fecha Inicio: {paquete.fecha_inicio}, Fecha Fin: {paquete.fecha_fin}, Precio: {paquete.precio}")
        
        id_paquete = int(input("Ingrese el ID del paquete turístico que desea eliminar: "))
        confirmacion = input("¿Está seguro que desea eliminar este paquete turístico? (s/n): ")
        if confirmacion.lower() != 's':
            print("Eliminación cancelada.")
            return
        exito = CrudPaquete().Eliminar(id_paquete)
        if exito:
            print("Paquete turístico eliminado con éxito.")
            time.sleep(3)
            os.system('cls')
        else:
            print("No se pudo eliminar el paquete turístico. Por favor, intente de nuevo.")
            time.sleep(3)
            os.system('cls')
    except Exception as e:
        print(f"Ocurrió un error al eliminar el paquete turístico: {e}. Por favor, intente de nuevo.")

def ver_paquetes():
    try:
        time.sleep(1)
        os.system('cls')
        paquetes = CrudPaquete().Mostrar()
        print("================ PAQUETES ================")
        if paquetes == []:
            print("No hay paquetes turísticos para mostrar.")
            input("Presione Enter para volver al menú anterior...")
            os.system('cls')
            return
        for paquete in paquetes:
            precio_base = paquete.precio
            if precio_base is None and paquete.destinos:
                precio_base = sum((destino._costo or 0) for destino in paquete.destinos)
            precio_txt = _precio_formateado(precio_base)
            fecha_ini_txt = paquete.fecha_inicio or "Fecha a definir"
            fecha_fin_txt = paquete.fecha_fin or "Fecha a definir"

            print(f"#{paquete.id_paquete} {paquete.nombre}")
            print(f" Fechas: {fecha_ini_txt} -> {fecha_fin_txt}")
            print(f" Valor total: {precio_txt}")
            if moneda_seleccionada.get("indicador"):
                print(f"  (Tasa {moneda_seleccionada['nombre']}: {moneda_seleccionada['tasa']:,.4f} CLP)")
            print(" Destinos incluidos:")
            if paquete.destinos:
                for destino in paquete.destinos:
                    costo_dest = _precio_formateado(destino._costo) if destino._costo is not None else "Sin costo"
                    print(f"  - {destino._nombre} | {destino._actividades} | {costo_dest}")
            else:
                print("  (Sin destinos asociados)")
            print("-" * 48)
        input("Presione Enter para volver al menú anterior...")
        os.system('cls')
    except Exception as e:
        print(f"Ocurrió un error al obtener los paquetes turísticos: {e}. Por favor, intente de nuevo.")

def gestionar_paquetes():
    try:
        opc = int(input("1.- Crear Paquete Turístico\n2.- Ver Paquetes Turísticos\n3.- Editar Paquete Turístico\n4.- Eliminar Paquete Turístico\n5.- Salir al menu principal\nSeleccione una opción: "))
        if opc == 1:
            Agregar()
        elif opc == 2:
            ver_paquetes()
        elif opc == 3:
            editar_paquete()
        elif opc == 4:
            eliminar_paquete()
        elif opc == 5:
            print("Volviendo al menú anterior...")
            time.sleep(2)
            os.system('cls')
    except Exception as e:
        print(f"Ocurrió un error: {e}. Por favor, intente de nuevo.")

def ver_reservas_admin():
    try:
        reservas = CrudReserva().Mostrar_Admin(usuario_sesion.rol._id_rol)
        print("================ RESERVAS ================")
        if reservas == []:
            print("No hay reservas para mostrar.")
            input("Presione Enter para volver al menú anterior...")
            os.system('cls')
            return
        for reserva in reservas:
            valor_raw = reserva['paquete']['valor_total']
            try:
                valor_raw = float(valor_raw) if valor_raw is not None else None
            except Exception:
                pass
            valor_txt = _precio_formateado(valor_raw)
            print(f"Reserva #{reserva['id']} | Usuario {reserva['nombre_usuario']} | Paquete {reserva['id_paquete']}")
            print(f" Fecha reserva: {reserva['fecha_reserva']}")
            print(f" Paquete: {reserva['paquete']['nombre']} | {reserva['paquete']['fecha_inicio']} -> {reserva['paquete']['fecha_fin']}")
            print(f" Valor total: {valor_txt}")
            print("-" * 48)
        input("Presione Enter para volver al menú anterior...")
        os.system('cls')
    except Exception as e:
        print(f"Ocurrió un error al obtener las reservas: {e}. Por favor, intente de nuevo.")
        

def MenuAdministrador():
    print("----- Menú Administrador -----")
    print("---------- Bienvendio a su menú, Administrador ----------")
    print("1.- Gestionar Destinos\n2.- Gestionar Paquetes Turísticos\n3.- Ver Reservas\n4.- Cerrar Sesión")
    try:
        opcion = int(input("Seleccione una opción: "))
        if opcion == 1:
            GestionarDestinos()
        elif opcion == 2:
            gestionar_paquetes()
        elif opcion == 3:
            ver_reservas_admin()
        elif opcion == 4:
            print("Cerrando sesión...")
            global usuario_sesion
            usuario_sesion = None
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
        time.sleep(2)
        os.system('cls')
    except Exception as e:
        print(f"Ocurrió un error: {e}. Por favor, intente de nuevo.")   

def _seleccionar_moneda():
    print("Monedas disponibles:")
    opciones = {
        "1": ("CLP", None, "$"),
        "2": ("UF", "uf", "UF"),
        "3": ("DOLAR", "dolar", "US$"),
        "4": ("EURO", "euro", "€"),
        "5": ("UTM", "utm", "UTM"),
    }
    for idx, (nombre, _, simbolo) in opciones.items():
        print(f" {idx}. {nombre} ({simbolo})")
    eleccion = input("Seleccione la moneda en la que desea ver los precios: ").strip()
    return opciones.get(eleccion)


def cambiar_moneda():
    global moneda_seleccionada
    opcion = _seleccionar_moneda()
    if not opcion:
        print("Opción de moneda no válida. Se mantiene la moneda actual.")
        return
    nombre, indicador, simbolo = opcion
    if indicador is None:
        moneda_seleccionada = {"nombre": nombre, "indicador": None, "simbolo": simbolo, "tasa": 1.0}
        print("Moneda cambiada a CLP.")
        return
    tasa = ApiCambioMoneda().obtener_valor(indicador)
    if tasa is None:
        print("No se pudo obtener la tasa automáticamente.")
        usar_manual = input("¿Desea ingresar una tasa manual en CLP por unidad? (s/n): ").strip().lower()
        if usar_manual != 's':
            print("Se mantiene la moneda actual.")
            return
        try:
            tasa = float(input("Ingrese la tasa en CLP: ").replace(",", "."))
        except Exception:
            print("Tasa inválida. Se mantiene la moneda actual.")
            return

    moneda_seleccionada = {"nombre": nombre, "indicador": indicador, "simbolo": simbolo, "tasa": tasa}
    print(f"Moneda cambiada a {nombre}. Tasa: {tasa:,.4f} CLP")


def _convertir_precio_clp(precio_clp: float) -> tuple[float, str]:
    tasa = moneda_seleccionada.get("tasa") if moneda_seleccionada.get("indicador") else 1.0
    simbolo = moneda_seleccionada.get("simbolo", "$")
    if not tasa:
        return precio_clp, "$"
    return precio_clp / tasa, simbolo


def _precio_formateado(precio_clp: float | None) -> str:
    if precio_clp is None:
        return "Valor a confirmar"
    valor, simbolo = _convertir_precio_clp(precio_clp)
    return f"{simbolo}{valor:,.2f}"


def MostrarPaquetes():
    try:
        paquetes = CrudPaquete().Mostrar()
        print("----- Lista de Paquetes Turísticos -----")
        if paquetes == []:
            print("No hay paquetes turísticos para mostrar.")
            input("Presione Enter para volver al menú anterior...")
            os.system('cls')
            return

        paquetes_filtrados = paquetes
        aplicar_filtros = input("¿Desea aplicar filtros por fecha y destino? (s/n): ").strip().lower()
        if aplicar_filtros == 's':
            fecha_inicio_raw = input("Ingrese la fecha de inicio mínima (YYYY-MM-DD o DD-MM-YYYY, Enter para omitir): ").strip()
            fecha_fin_raw = input("Ingrese la fecha de fin máxima (YYYY-MM-DD o DD-MM-YYYY, Enter para omitir): ").strip()
            destino_id_raw = input("Ingrese el ID de destino para filtrar (Enter para omitir): ").strip()

            fecha_inicio_filtro = parse_fecha(fecha_inicio_raw) if fecha_inicio_raw else None
            fecha_fin_filtro = parse_fecha(fecha_fin_raw) if fecha_fin_raw else None
            destino_id_filtro = int(destino_id_raw) if destino_id_raw else None

            paquetes_filtrados = []
            for paquete in paquetes:
                inicio_dt = _a_datetime(paquete.fecha_inicio)
                fin_dt = _a_datetime(paquete.fecha_fin)

                if fecha_inicio_filtro:
                    filtro_inicio_dt = _a_datetime(fecha_inicio_filtro)
                    if not inicio_dt or (filtro_inicio_dt and inicio_dt < filtro_inicio_dt):
                        continue
                if fecha_fin_filtro:
                    filtro_fin_dt = _a_datetime(fecha_fin_filtro)
                    if not fin_dt or (filtro_fin_dt and fin_dt > filtro_fin_dt):
                        continue
                if destino_id_filtro is not None:
                    tiene_destino = any(getattr(destino, "_id_destino", None) == destino_id_filtro for destino in paquete.destinos)
                    if not tiene_destino:
                        continue

                paquetes_filtrados.append(paquete)

        if paquetes_filtrados == []:
            print("No hay paquetes turísticos que coincidan con los filtros.")
            input("Presione Enter para volver al menú anterior...")
            os.system('cls')
            return

        for paquete in paquetes_filtrados:
            fecha_ini_txt = paquete.fecha_inicio or "Fecha a definir"
            fecha_fin_txt = paquete.fecha_fin or "Fecha a definir"

            precio_base = paquete.precio
            if precio_base is None and paquete.destinos:
                precio_base = sum((destino._costo or 0) for destino in paquete.destinos)

            precio_mostrado = _precio_formateado(precio_base)

            print(f"Paquete: {paquete.nombre}")
            print(f" Fechas: {fecha_ini_txt} → {fecha_fin_txt}")
            print(f" Valor total: {precio_mostrado}")
            if moneda_seleccionada.get("indicador"):
                print(f"  (Tasa {moneda_seleccionada['nombre']}: {moneda_seleccionada['tasa']:,.2f} CLP)")
            print(" Incluye destinos:")
            if paquete.destinos:
                for destino in paquete.destinos:
                    costo_base = getattr(destino, "_costo", None)
                    costo_txt = "Costo no informado"
                    if costo_base is not None:
                        costo_convertido, simbolo_dest = _convertir_precio_clp(costo_base)
                        costo_txt = f"{simbolo_dest}{costo_convertido:,.2f}"
                    print(f"  - {destino._nombre}: {destino._descripcion} | Actividades: {destino._actividades} | Desde {costo_txt}")
            else:
                print("  (Aún sin destinos asociados)")
            print("--------------------------------------------------")
        input("Presione Enter para volver al menú anterior...")
        os.system('cls')
    except Exception as e:
        print(f"Ocurrió un error al obtener los paquetes turísticos: {e}. Por favor, intente de nuevo.")

def ver_reversas():
    try:
        reservas = CrudReserva().Mostrar(usuario_sesion.id)
        print("===== Tus reservas =====")
        if reservas == []:
            print("Aún no tienes reservas. ¡Explora los paquetes y reserva tu próxima aventura!")
            input("Presiona Enter para volver al menú...")
            os.system('cls')
            return
        for reserva in reservas:
            nombre = reserva['paquete']['nombre']
            f_ini = reserva['paquete']['fecha_inicio']
            f_fin = reserva['paquete']['fecha_fin']
            valor = reserva['paquete']['valor_total']
            try:
                valor = float(valor) if valor is not None else None
            except Exception:
                pass
            valor_txt = _precio_formateado(valor)
            print(f"Reserva #{reserva['id']} · Paquete: {nombre}")
            print(f" Fechas: {f_ini} → {f_fin}")
            print(f" Valor total: {valor_txt}")
            if moneda_seleccionada.get("indicador"):
                print(f"  (Tasa {moneda_seleccionada['nombre']}: {moneda_seleccionada['tasa']:,.2f} CLP)")
            print(f" Fecha de reserva: {reserva['fecha_reserva']}")
            print("----------------------------------------------")
        input("Presiona Enter para volver al menú...")
        os.system('cls')
    except Exception as e:
        print(f"Ocurrió un error al obtener las reservas: {e}. Por favor, intente de nuevo.")

def cancelar_reserva():
    try:
        reservas = CrudReserva().Mostrar(usuario_sesion.id)
        if reservas == []:
            print("No tienes reservas para cancelar.")
            input("Presiona Enter para volver al menú...")
            os.system('cls')
            return
        print("----- Tus Reservas -----")
        for reserva in reservas:
            print(f"ID Reserva: {reserva['id']}, Paquete: {reserva['paquete']['nombre']}, Fecha Reserva: {reserva['fecha_reserva']}")
        id_reserva = int(input("Ingrese el ID de la reserva que desea cancelar: "))
        confirmacion = input("¿Está seguro que desea cancelar esta reserva? (s/n): ")
        if confirmacion.lower() != 's':
            print("Cancelación de reserva cancelada.")
            return
        reserva_obj = next((r for r in reservas if r['id'] == id_reserva), None)
        if not reserva_obj:
            print("Reserva no encontrada. Por favor, intente de nuevo.")
            return
        if reserva_obj['id_usuario'] != usuario_sesion.id:
            print("No puedes cancelar una reserva que no es tuya.")
            return
        exito = CrudReserva().Eliminar(id_reserva)
        if exito:
            print("Reserva cancelada con éxito.")
        else:
            print("No se pudo cancelar la reserva. Por favor, intente de nuevo.")
    except Exception as e:
        print(f"Ocurrió un error al cancelar la reserva: {e}. Por favor, intente de nuevo.")
    finally:
        time.sleep(3)
        os.system('cls')

def GestionarReserva():
    os.system('cls')
    print("----- Gestión de Reservas -----")
    print("1.- Hacer una Reserva \n2.- Ver mis Reservas \n3.-Cancelar Reserva \n4.- Volver al menú anterior")
    try:
        opcion = int(input("Seleccione una opción: "))
        if opcion == 1:
            HacerReserva()
        elif opcion == 2:
            ver_reversas()
        elif opcion == 3:
            cancelar_reserva()
        elif opcion == 4:
            print("Volviendo al menú anterior...")
            time.sleep(2)
            os.system('cls')
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
    except Exception as e:
        print(f"Ocurrió un error: {e}. Por favor, intente de nuevo.")

def HacerReserva():
    print("----- Hacer Reserva -----")
    try:
        paquetes = CrudPaquete().Mostrar()
        if not paquetes:
            print("No hay paquetes turísticos disponibles para reservar.")
            input("Presione Enter para volver al menú anterior...")
            os.system('cls')
            return
        print("----- Lista de Paquetes Turísticos -----")
        for paquete in paquetes:
            precio_base = paquete.precio
            if precio_base is None and paquete.destinos:
                precio_base = sum((destino._costo or 0) for destino in paquete.destinos)
            precio_txt = _precio_formateado(precio_base)
            print(f"ID: {paquete.id_paquete}, Nombre: {paquete.nombre}, Fecha Inicio: {paquete.fecha_inicio}, Fecha Fin: {paquete.fecha_fin}, Precio: {precio_txt}")
        if moneda_seleccionada.get("indicador"):
            print(f"Tasa {moneda_seleccionada['nombre']}: {moneda_seleccionada['tasa']:,.2f} CLP")
        id_paquete = int(input("Ingrese el ID del paquete turístico que desea reservar: "))
        paquete_seleccionado = None
        for p in paquetes:
            if p.id_paquete == id_paquete:
                paquete_seleccionado = p
                break
        if not paquete_seleccionado:
            print("Paquete turístico no encontrado. Por favor, intente de nuevo.")
            return
        exito = CrudReserva().Agregar(usuario_sesion.id, paquete_seleccionado.id_paquete)
        if exito:
            print("Reserva realizada con éxito.")
        else:
            print("No se pudo realizar la reserva. Por favor, intente de nuevo.")
    except Exception as e:
        print(f"Ocurrió un error al hacer la reserva: {e}. Por favor, intente de nuevo.")
    finally:
        time.sleep(3)
        os.system('cls')

def MenuCliente():
    global usuario_sesion
    print("----- Menú Cliente -----")
    print("---------- Bienvendio a su menú, Cliente ----------")
    print("1.- Cambiar Moneda\n2.- Mostrar paquetes turisticos\n3.- Gestionar Reserva \n4.- Ver mis datos \n5.- Cerrar Sesión")
    try:
        opcion = int(input("Seleccione una opción: "))
        if opcion == 1:
            cambiar_moneda()
        elif opcion == 2:
            MostrarPaquetes()
        elif opcion == 3:
            GestionarReserva()
        elif opcion == 4:
            print("----- Tus Datos -----")
            print(f"Nombre: {usuario_sesion.nombre} {usuario_sesion.apellido}")
            print(f"Email: {usuario_sesion.email}")
            print(f"RUN: {usuario_sesion.run}")
            print(f"Teléfono: {usuario_sesion.fono}")
            print(f"Nombre de usuario: {usuario_sesion.username}")
            print(f"Rol: {usuario_sesion.rol._nombre}")
            input("Presiona Enter para volver al menú...")
        elif opcion == 5:
            print("Cerrando sesión...")
            usuario_sesion = None
        else:
            print("Opción no válida. Por favor, intente de nuevo.")
    except Exception as e:
        print(f"Ocurrió un error: {e}. Por favor, intente de nuevo.")

while True:
    try:
        if usuario_sesion:
            if usuario_sesion.rol._id_rol == 1:
                MenuAdministrador()
            elif usuario_sesion.rol._id_rol == 2:
                MenuCliente()
        else:
            Login()
        time.sleep(2)
        os.system('cls')
    except Exception as e:
        print(f"Ocurrió un error: {e}. Por favor, intente de nuevo.")