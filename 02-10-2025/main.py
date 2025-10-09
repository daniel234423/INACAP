# main.py
import os
import DAO.CrudCliente
from DTO.Tipo import TipoUsuario
from DTO.Cliente import Cliente

def menuprincipal(): 
    print("---")
    print("    M E N Ú   P R I N C I P A L  ")
    print("---")
    print("    1. - (C) INGRESAR    ")
    print("    2. - (R) MOSTRAR    ")
    print("    3. - (U) MODIFICAR    ")
    print("    4. - (D) ELIMINAR    ")
    print("    5. - (S) Salir    ")
    print("---")

def menumostrar(): 
    print("---")
    print("    M E N Ú   M O S T R A R  ")
    print("---")
    print("    1. - MOSTRAR TODOS    ")
    print("    2. - MOSTRAR PARTICULAR    ")
    print("    3. - MOSTRAR PARCIAL    ")
    print("    4. - VOLVER    ")
    print("---")

def ingresardatos(): 
    print("---")
    print("    INGRESAR DATOS CLIENTE    ")
    print("---")
    run = input("INGRESE RUN : ")
    nombre = input("INGRESE NOMBRE : ")
    apellido = input("INGRESE APELLIDO : ")
    direccion = input("INGRESE DIRECCIÓN : ")
    fono = input("INGRESE TELÉFONO : ")
    correo = input("INGRESE CORREO : ")
    
    # recorremos los tipos
    datos = DAO.CrudCliente.mostrartipos()
    print("---")
    for dato in datos:
        print(" CÓDIGO : {} - {}".format(dato[0], dato[1]))
    print("---")
    
    tipo = int(input("Ingrese el código del Tipo de cliente: "))
    monto = int(input("INGRESE MONTO CRÉDITO : "))
    c = Cliente(run, nombre, apellido, direccion, fono, correo, tipo, montocredito=monto)
    print(c.montoCredito)
    DAO.CrudCliente.agregar(c)
def mostrar():
    while(True):
        menumostrar()
        op2 = int(input(" INGRESE OPCIÓN : "))
        if op2 == 1:
            mostrartodo()
            input("\n PRESIONE ENTER PARA CONTINUAR")
        elif op2 == 2:
            mostraruno()
        elif op2 == 3:
            mostrarparcial()
        if op2 == 4:
            break
        else:
            print("Opción Fuera de Rango")

def mostrartodo():
    print("===============")
    print(" LISTA DE TODOS LOS CLIENTES ")
    print("===============")
    datos = DAO.CrudCliente.mostrartodos()
    for dato in datos:
        print(" ID : {} - RUN : {} - NOMBRE : {} - APELLIDO : {} - DIRECCION : {} - FONO : {} - CORREO : {} - MONTO CRÉDITO : {} - DEUDA : {} - TIPO : {} ".format(
            dato[0], dato[1], dato[2], dato[3], dato[4], dato[5], dato[6], dato[7], dato[8], dato[9]))
    print("---")

def mostraruno():
    print("=========================")
    print(" MUESTRA DE DATOS PARTICULAR ")
    print("=========================")
    op = int(input("\n Ingrese valor del ID del Cliente que desea Mostrar los Datos : "))
    datos = DAO.CrudCliente.consultaparticular(op)
    print("\n======================================")
    print(" MUESTRA DE DATOS DEL CLIENTE ")
    print("=========================")
    print(" ID : {}".format(datos[0]))
    print(" RUN : {}".format(datos[1]))
    print(" NOMBRE : {}".format(datos[2]))
    print(" APELLIDO : {}".format(datos[3]))
    print(" DIRECCION : {}".format(datos[4]))
    print(" FONO : {}".format(datos[5]))
    print(" CORREO : {}".format(datos[6]))
    print(" TIPO : {}".format(datos[9]))
    print(" MONTO CREDITO : {}".format(datos[7]))
    print(" DEUDA : {}".format(datos[8]))
    print("=========================")
    input("\n\n PRESIONE ENTER PARA CONTINUAR")
def mostrarparcial():  
    print("---")  
    print(" MUESTRA PARCIALMENTE LOS CLIENTES ")  
    print("---")  
    cant = int(input("\nIngrese la cantidad de clientes a Mostrar : "))  
    datos = DAO.CrudCliente.consultaparcial(cant)  
    for dato in datos:  
        print(" ID : {} - RUN : {} - NOMBRE : {} - APELLIDO : {} - DIRECCION : {} - FONO : {} - CORREO : {} - MONTO CRÉDITO : {} - DEUDA : {} - TIPO : {} ".format(  
            dato[0], dato[1], dato[2], dato[3], dato[4], dato[5], dato[6], dato[7], dato[8], dato[9]))  
        print("---")  
    input("\n\n PRESIONE ENTER PARA CONTINUAR")
def modificacion():
    listanuevos = []
    print("---")
    print(" MODIFICACIÓN DE CLIENTE ")
    print("---")
    mostrartodo()
    try:
        mod = int(input("Ingrese valor de ID del cliente que desea modificar : "))
        datos = DAO.CrudCliente.consultaparticular(mod)
        if not datos:
            print("Cliente no encontrado.")
            return

        print(" ID : {}".format(datos[0]))
        listanuevos.append(datos[0])
        print(" RUN : {}".format(datos[1]))
        listanuevos.append(datos[1])

        # Solicitar nuevos datos
        nombre = input(f"Nuevo Nombre ({datos[2]}): ") or datos[2]
        apellido = input(f"Nuevo Apellido ({datos[3]}): ") or datos[3]
        direccion = input(f"Nueva Dirección ({datos[4]}): ") or datos[4]
        fono = input(f"Nuevo Teléfono ({datos[5]}): ") or datos[5]
        correo = input(f"Nuevo Correo ({datos[6]}): ") or datos[6]
        monto = input(f"Nuevo Monto Crédito ({datos[7]}): ") or datos[7]

        # Actualizar cliente
        cliente_modificado = Cliente(
            datos[1], nombre, apellido, direccion, fono, correo, datos[9], int(monto),
        )
        DAO.CrudCliente.editar(cliente_modificado, mod)
        print("Cliente modificado exitosamente.")
    except ValueError:
        print("Entrada inválida. Por favor, ingrese un número.")
    except Exception as e:
        print(f"Error al modificar cliente: {e}")

while True:
    menuprincipal()
    try:
        op = int(input(" INGRESE OPCIÓN : "))
        if op == 1:
            ingresardatos()
        elif op == 2:
            mostrar()
        elif op == 3:
            modificacion()
        elif op == 4:
            os.system("cls")
            print("===============")
            print(" ELIMINAR CLIENTE ")
            print("===============")
            mostrartodo()
            try:
                eli = int(input("Ingrese valor del ID del cliente que desea eliminar : "))
                DAO.CrudCliente.eliminar(eli)
                print("Cliente eliminado exitosamente.")
            except ValueError:
                print("Entrada inválida. Por favor, ingrese un número.")
        elif op == 5:
            print("Gracias por usar el sistema")
            break
        else:
            print("Opción Fuera de Rango")
    except ValueError:
        print("Entrada inválida. Por favor, ingrese un número.")