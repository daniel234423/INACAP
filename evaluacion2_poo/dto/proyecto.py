from datetime import date 

class Proyecto :
    def __init__ (self ,id ,nombre ,fecha_inicio :date ,fecha_fin :date ):
        self .id =id 
        self .nombre =nombre 
        self .fecha_inicio =fecha_inicio 
        self .fecha_fin =fecha_fin 

    def __str__ (self ):
        return f"Proyecto: {self .nombre } (ID: {self .id })"
