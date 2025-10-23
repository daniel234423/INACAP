from dto .persona import Persona 
from dto .rol import Rol 


class Empleado (Persona ):

    def __init__ (self ,id =None ,persona_id =None ,nombre =None ,direccion =None ,telefono =None ,correo =None ,fecha_inicio =None ,password_hash =None ,rol :Rol =None ,departamento_id =None ,salario :float =0.0 ,persona :Persona =None ,created_at =None ):

        # persona puede venir embebida o referenciada por persona_id
        if persona :
            super ().__init__ (id =persona .id or id ,empleado_id =persona .empleado_id ,nombre =persona .nombre ,direccion =persona .direccion ,telefono =persona .telefono ,correo =persona .correo ,fecha_inicio =persona .fecha_inicio ,salario =persona .salario ,created_at =persona .created_at )
            self .persona_id = persona .id or persona_id
            self .id = id
        else :
            super ().__init__ (id =id ,empleado_id =id ,nombre =nombre ,direccion =direccion ,telefono =telefono ,correo =correo ,fecha_inicio =fecha_inicio ,salario =salario ,created_at =created_at )
            self .persona_id = persona_id

        self .password_hash =password_hash 
        self .rol =rol 
        self .departamento_id =departamento_id 

    def __str__ (self ):
        display_name =self .nombre or self .correo or f"Empleado {self .id }"
        rol_name =getattr (self .rol ,'nombre','N/A')if self .rol else 'N/A'
        return f"Empleado: {display_name } (ID: {self .id }, Rol: {rol_name }, Salario: {getattr (self ,'salario',0 )})"
