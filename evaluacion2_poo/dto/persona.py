from datetime import datetime 


class Persona :

    def __init__ (self ,id =None ,empleado_id =None ,nombre =None ,direccion =None ,telefono =None ,correo =None ,fecha_inicio =None ,salario :float =0.0 ,created_at =None ):
        self .id =id 

        self .empleado_id =empleado_id 

        self .nombre =nombre 
        self .direccion =direccion 
        self .telefono =telefono 
        self .correo =correo 
        self .fecha_inicio =fecha_inicio 
        self .salario =float (salario or 0.0 )
        self .created_at =created_at or datetime .utcnow ()

    def __str__ (self ):
        name =self .nombre or 'N/A'
        if getattr (self ,'empleado_id',None ):
            return f"Persona: {name } (ID: {self .id }, Empleado ID: {self .empleado_id })"
        return f"Persona: {name } (ID: {self .id })"
