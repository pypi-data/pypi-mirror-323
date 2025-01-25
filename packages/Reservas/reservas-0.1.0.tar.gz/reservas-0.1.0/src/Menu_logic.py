

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.Menu import Ui_NLTMainWindow  # importo la iu generado por Python
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget 
from databases.reservas_logica import connectando
from src.MostrarReserva_logi import NLTMostrarReserva
#from ConsultarReservas_logic import NLTConsultarReservas
class NLTMenu(QMainWindow):
    """
    Esta clase es la que gestionara el menu de Opciones.

    Metodos :
    NLT mostrarRerva : Este metodo , cargara la ventana mostrarReseerva
    NLTSalir : Este metodo es el encargado no solo de salir de la pantalla si no de desconectar la base de datos
    NLTConsultarReserva :Este metodo Se encarga de Eliminar o Consultar un Reserva
    """
    def __init__(self):
        """
        Este metodo se encarga de inicializar la ui y conectar los metodos .
        """
        super().__init__()
        self.ui=Ui_NLTMainWindow()  # instancia del menú
        self.ui.setupUi(self)  # llamando la interfax del menu
        self.mi_conexion=connectando()
        
        self.ui.actionMostrar_Reservas.triggered.connect(self.NLTMostrarReserva)
        self.ui.actionSalir_2.triggered.connect(self.NLTsalir)
        #self.ui.actionConsultar_Reserva.triggered.connect(self.NLTConsultarReserva)
      

        



    def NLTMostrarReserva(self):
       """
       Este metodo se encarga de Abrir la otra ventana y mostrarla
       """
       self.ui_reservas =NLTMostrarReserva() # Instanciar la interfaz de reservas
       self.ui_reservas.show()  # Most 
    def NLTsalir(self):
        """
        Metodo que se encarga de salir de la app , y desconectar la base de datos
        """
        if self.mi_conexion:
           self.mi_conexion.desconectar()
           print("Conexión a la base de datos cerrada correctamente.")
        self.close()
            
            
    #def NLTConsultarReserva(self):
       # """
       # Metodo que encarga de mostrar la ventana para consultar o eliminar la reserva
        #"""
       # self.ui_consultarReservas=NLTConsultarReservas()
       # self.ui_consultarReservas.show()
      
      
      
    



       


