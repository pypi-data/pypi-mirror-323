
import re
"""
Modulo  Que se encarga de Validar los datos , que el Usuario introduce
por el Formulario ..
 
"""
def validarTelefono(telefono):
    """
    Metodo para validar Telefono a nivel nacional e Internacional 
    Args : el Telefono 
    Returns : True o False .
    >>> validarTelefono("65628928")
    True

    >>> validarTelefono("065895789")
    False
    
    """
    patron=r"^\+?[1-9]\d{1,14}$"  
    if re.fullmatch(patron,str(telefono)):
      return True
    else :
       return False
    

def validarNombre(nombre): 
   """
    Metodo que Recibe por parametros un nombre , puede contener acentos ,mayusculas y minusculas
    Args : Recibe un nombre
    Return :  True o False si correcto el nombre

    >>> validarNombre("Navil")
    True
    >>> validarNombre("1Navil")
    False

   """
   patron=r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$" 
   if re.fullmatch(patron,nombre) :
      return True
   else:
      return False

"""
Para validar la entrada de numeros enteros que no me acepte nada mas...
"""   
def validarNumerosEnteros(numero):
   """
   Metodo para Validar que sea un numero lo que se introduce
   Args : numero 
   Return : True o False

   >>> validarNumerosEnteros(5)
   True
   >>> validarNumerosEnteros("N")
   False
   """
   patron =r"^\d+$"
   if re.match(patron, str(numero)):    # recibe un entero y lo convieto en cadena para poder hacer la Expersion Regualar
      return True
   else:

      return False
def validarFecha(fecha):
   """
   Metodo para validar la fecha 
   Args :  Recibe la fecha
   Return True o False
   >>> validarFecha("10/07/1989")
   True
   >>> validarFecha("111/07/1989")
   False
   """
   patron= r"^\d{2}/\d{2}/\d{4}$"
   if re.fullmatch(patron , fecha):
      return True
   else :
      return False
   
if __name__ == "__main__":
    import doctest
    doctest.testmod()

   


   


