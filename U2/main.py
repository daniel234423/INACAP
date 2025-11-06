import os
import DAO.CRUDCliente
from DTO.Tipo import Tipo_Usuario
from DTO.Cliente import Cliente

def menuprincipal():
    os.system('cls')
    print("===================================")
    print("          M E N Ú  P R I N C I P A L")
    print("===================================")
    print("1.- (C) INGRESAR")
    print("2.- (R) MOSTRAR")
    print("3.- (U) MODIFICAR")
    print("4.- (D) ELIMINAR")
    print("5.- (E) Salir")
    print("===================================")

def menumostrar():
    os.system('cls')
    print("===================================")
    print("          M E N Ú  M O S T R A R")
    print("===================================")
    print("1.- MOSTRAR TODO")
    print("2.- MOSTRAR UNO")
    print("3.- MOSTRAR PARCIAL")
    print("4.- VOLVER")
    print("===================================")

def ingresardatos():
    os.system('cls')
    print("===================================")
    print("       INGRESAR DATOS CLIENTE")
    print("===================================")
    run = input("INGRESE RUN : ")
    nombre = input("INGRESE NOMBRE : ")
    apellido = input("INGRESE APELLIDO : ")
    direccion = input("INGRESE DIRECCION : ")
    fono = input("INGRESE TELEFONO : ")
    correo = input("INGRESE CORREO : ")

    # recorremos los tipos
    datos = DAO.CRUDCliente.mostrartipos()
    print("-----------------------------------")
    for dato in datos:
        print(" CODIGO : {} - {}".format(dato[0], dato[1]))
    print("-----------------------------------")
    tipo = int(input("Ingrese el codigo del Tipo de Cliente: "))
    monto = int(input("INGRESE MONTO CREDITO : "))

    c = Cliente(run, nombre, apellido, direccion, fono, correo, tipo, monto, deuda=0)
    DAO.CRUDCliente.agregar(c)

def mostrar():
    while(True):
        menumostrar()
        op2 = int(input(" INGRESE OPCIÓN : "))
        if op2 == 1:
            mostrartodo()
            input("\n\n PRESIONE ENTER PARA CONTINUAR")
        elif op2 == 2:
            mostraruno()
        elif op2 == 3:
            mostrarparcial()
        if op2 == 4:
            break
        else:
            print("Opción Fuera de Rango")

def mostrartodo():
    os.system('cls')
    print("===================================")
    print("    MUESTRA DE TODOS LOS CLIENTES")
    print("===================================")
    datos = DAO.CRUDCliente.mostrartodos()
    for dato in datos:
        print(" ID : {} - RUN : {} - NOMBRE : {} - APELLIDO : {} - DIRECCION : {} - FONO : {} - CORREO : {} - MONTO CRÉDITO : {} - DEUDA : {} - TIPO : {}".format(
            dato[0], dato[1], dato[2], dato[3], dato[4], dato[5], dato[6], dato[7], dato[8], dato[9]))

def mostraruno():
    os.system('cls')
    print("===================================")
    print("     MUESTRA DE DATOS PARTICULAR")
    print("===================================")
    op = int(input("\n Ingrese valor del ID del Cliente que desea Mostrar los Datos : "))
    datos = DAO.CRUDCliente.consultaparticular(op)

    print("\n===================================")
    print("    MUESTRA DE DATOS DEL CLIENTE")
    print("===================================")
    print(" ID               : {} ".format(datos[0]))
    print(" RUN              : {} ".format(datos[1]))
    print(" NOMBRE           : {} ".format(datos[2]))
    print(" APELLIDO         : {} ".format(datos[3]))
    print(" DIRECCION        : {} ".format(datos[4]))
    print(" FONO             : {} ".format(datos[5]))
    print(" CORREO           : {} ".format(datos[6]))
    print(" MONTO CREDITO    : {} ".format(datos[7]))
    print(" DEUDA            : {} ".format(datos[8]))
    print(" TIPO             : {} ".format(datos[9]))
    input("\n\n PRESIONE ENTER PARA CONTINUAR")

def mostrarparcial():
    os.system('cls')
    print("===================================")
    print("   MUESTRA PARCIALMENTE LOS CLIENTES")
    print("===================================")
    cant = int(input("\nIngrese la Cantidad de Clientes a Mostrar : "))
    datos = DAO.CRUDCliente.consultaparcial(cant)
    for dato in datos:
        print(" ID : {} - RUN : {} - NOMBRE : {} - APELLIDO : {} - DIRECCION : {} - FONO : {} - CORREO : {} - MONTO CRÉDITO : {} - DEUDA : {} - TIPO : {}".format(
            dato[0], dato[1], dato[2], dato[3], dato[4], dato[5], dato[6], dato[7], dato[8], dato[9]))
    input("\n\n PRESIONE ENTER PARA CONTINUAR")

def modificardatos():
    os.system('cls')
    listanuevos=[]
    print("===================================")
    print("     MODULO MODIFICAR CLIENTE")
    print("===================================")
    mod = int(input("\n Ingrese valor de ID del Cliente que desea Modificar : "))
    datos = DAO.CRUDCliente.consultaparticular(mod)
    mostrartodo()
    print(" ID               : {} ".format(datos[0]))
    listanuevos.append(datos[0])
    print(" RUN              : {} ".format(datos[1]))
    listanuevos.append(datos[1])

    opm = input("DESEA MODIFICAR EL NOMBRE : {} - [SI/NO] ".format(datos[2]))
    if opm.lower() == "si":
        nombrenuevo = input("INGRESE NOMBRE : ")
        listanuevos.append(nombrenuevo)
    else:
        listanuevos.append(datos[2])

    opm = input("DESEA MODIFICAR EL APELLIDO : {} - [SI/NO] ".format(datos[3]))
    if opm.lower() == "si":
        apellidonuevo = input("INGRESE APELLIDO : ")
        listanuevos.append(apellidonuevo)
    else:
        listanuevos.append(datos[3])

    opm = input("DESEA MODIFICAR LA DIRECCION : {} - [SI/NO] ".format(datos[4]))
    if opm.lower() == "si":
        dircnueva = input("INGRESE DIRECCION : ")
        listanuevos.append(dircnueva)
    else:
        listanuevos.append(datos[4])

    opm = input("DESEA MODIFICAR EL TELEFONO : {} - [SI/NO] ".format(datos[5]))
    if opm.lower() == "si":
        fononuevo = int(input("INGRESE TELEFONO : "))
        listanuevos.append(fononuevo)
    else:
        listanuevos.append(datos[5])

    opm = input("DESEA MODIFICAR EL CORREO : {} - [SI/NO] ".format(datos[6]))
    if opm.lower() == "si":
        correonuevo = input("INGRESE EL CORREO : ")
        listanuevos.append(correonuevo)
    else:
        listanuevos.append(datos[6])

    opm = input("DESEA MODIFICAR LA DEUDA : {} - [SI/NO] ".format(datos[8]))
    if opm.lower() == "si":
        deudanueva = int(input("INGRESE DEUDA : "))
        listanuevos.append(deudanueva)
    else:
        listanuevos.append(datos[8])

    opm = input("DESEA MODIFICAR EL MONTO DE CREDITO : {} - [SI/NO] ".format(datos[7]))
    if opm.lower() == "si":
        montonuevo = int(input("INGRESE MONTO DE CREDITO : "))
        listanuevos.append(montonuevo)
    else:
        listanuevos.append(datos[7])

    opm = input("DESEA MODIFICAR EL TIPO : {} - [SI/NO] ".format(datos[9]))
    if opm.lower() == "si":
        # recorremos los tipos
        datos = DAO.CRUDCliente.mostrartipos()
        print("-----------------------------------")
        for dato in datos:
            print(" CODIGO : {} - {}".format(dato[0], dato[1]))
        print("-----------------------------------")
        tiponuevo = int(input("INGRESE EL TIPO : "))
        listanuevos.append(tiponuevo)
    else:
        listanuevos.append(datos[9])

    DAO.CRUDCliente.editar(listanuevos)

def eliminardatos():
    os.system('cls')
    print("===================================")
    print("     MODULO ELIMINAR CLIENTE")
    print("===================================")
    mostrartodo()
    elim = int(input("Ingrese valor de ID del Cliente que desea Eliminar : "))
    DAO.CRUDCliente.eliminar(elim)


while(True):
    menuprincipal()
    op = int(input(" INGRESE OPCIÓN : "))
    if op==1:
        ingresardatos()
    elif op==2:
        mostrar()
    elif op==3:
        modificardatos()
    if op==4:
        eliminardatos()
    if op==5:
        op2 = input("DESEA SALIR [SI/NO] :")
        if op2.lower() == "si":
            exit()
    else:
        print("Opción Fuera de Rango")
