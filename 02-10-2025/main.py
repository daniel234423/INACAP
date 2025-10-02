# main.py
import os
import DAO.CrudCliente
from DTO.Tipo import TipoUsuario
from DTO.Cliente import Cliente

def menuprincipal(): 
    os.system('cls')
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
    os.system('cls')
    print("---")
    print("    M E N Ú   M O S T R A R  ")
    print("---")
    print("    1. - MOSTRAR TODOS    ")
    print("    2. - MOSTRAR PARTICULAR    ")
    print("    3. - MOSTRAR PARCIAL    ")
    print("    4. - VOLVER    ")
    print("---")

def ingresardatos(): 
    os.system('cls')
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
    datos = DAO.CRUDCliente.mostrartipos()
    print("---")
    for dato in datos:
        print(" CÓDIGO : {} - {}".format(dato[0], dato[1]))
    print("---")
    
    tipo = int(input("Ingrese el código del Tipo de cliente: "))
    monto = int(input("INGRESE MONTO CRÉDITO : "))
    c = Cliente(run, nombre, apellido, direccion, fono, correo, tipo, monto, deuda=0)
    DAO.CRUDCliente.agregar(c)

def mostrar():
    while(True):
        menumostrar()
        op2 = int(input(" INGRESE OPCIÓN : "))
        if op2 == 1:
            mostrartodo()
            input("\n PRESIONE ENTER PARA CONTINUAR")
        elif op2 == 2:
            menumostrar()
        elif op2 == 3:
            menumostrar()
        if op2 == 4:
            break
        else:
            print("Opción Fuera de Rango")

def mostrartodo():
    os.system("cls")
    print("===============")
    print(" LISTA DE TODOS LOS CLIENTES ")
    print("===============")
    datos = DAO.CRUDCliente.mostrartodos()
    for dato in datos:
        print(" ID : {} - RUN : {} - NOMBRE : {} - APELLIDO : {} - DIRECCION : {} - FONO : {} - CORREO : {} - MONTO CRÉDITO : {} - DEUDA : {} - TIPO : {} ".format(
            dato[0], dato[1], dato[2], dato[3], dato[4], dato[5], dato[6], dato[7], dato[8], dato[9]))
    print("---")