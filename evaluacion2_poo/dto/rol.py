class Rol :
    def __init__ (self ,id ,nombre ):
        self .id =id 
        self .nombre =nombre 

    def __str__ (self ):
        return f"Rol: {self .nombre } (ID: {self .id })"
