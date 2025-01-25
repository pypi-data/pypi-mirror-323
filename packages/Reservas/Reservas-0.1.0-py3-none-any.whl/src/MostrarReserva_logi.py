  
#import sys
#import os

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from databases.reservas_logica import connectando
from ui.MostrarReserva import Ui_NLTMainWindow
from src.Reserva_logic import NLTReserva

class NLTMostrarReserva(QMainWindow):
    """
    Esta clase es la encargada de Mostrar las reservas, siempre y cuando el usuario seleccione un salón.
    Métodos:
    mostrarFormulario: Este método se encargará de crear y mostrar el formulario.
    NLTcargar_salones: Este método cargará los salones desde la base de datos.
    on_salon_select: Este método se encarga de actualizar la información cuando se selecciona un salón.
    cargar_reservas_en_tabla: Método que gestiona la carga de datos desde la base de datos a la tabla.
    """
    
    def __init__(self):
        """
        Inicializa la clase NLTMostrarReserva, se encarga de gestionar las reservas por el id_salon.
        """
        super().__init__()
        self.miconexion = connectando()
        self.ui = Ui_NLTMainWindow()
        self.ui.setupUi(self)

        # Cargar los salones
        self.NLTcargar_salones()

        # Conectar evento para la selección de un salón (automáticamente se actualiza la tabla)
        self.ui.listWidget.itemSelectionChanged.connect(self.on_salon_select)
        
        # Conectar evento para abrir el formulario de reserva
        self.ui.pushButton_2.clicked.connect(self.mostrarFormulario)

    def NLTcargar_salones(self):
        """
        Método que carga los salones desde la base de datos y los muestra en el listWidget.
        """
        salones = self.miconexion.MostrarReservasSalones()
        print("Salones:", salones)  # Verifica lo que contiene `salones`
        
        if salones:
            for salon in salones:
                self.ui.listWidget.addItem(salon[1])  # Suponiendo que salon[1] es el nombre del salón
        else:
            print("No hay salones disponibles")

    def on_salon_select(self):
        """
        Método que gestiona el evento cuando el usuario selecciona un salón en la lista.
        Este evento se activa automáticamente al seleccionar un salón, sin necesidad de hacer clic.
        """
        item = self.ui.listWidget.selectedItems()  # Obtener los items seleccionados en la lista
        
        if item:
            salon_nombre = item[0].text()  # Obtener el nombre del salón seleccionado
            salon_id = self.miconexion.obtener_salon_id(salon_nombre)
            self.cargar_reservas_en_tabla(salon_nombre)
            self.salon_id_seleccionado = salon_id  # Almacenar el id del salón seleccionado

    def cargar_reservas_en_tabla(self, salon_nombre):
        """
        Método que carga las reservas desde las tablas y las muestra en la tabla.
        """
        # Limpiar la tabla antes de agregar nuevos datos
        self.ui.tableWidget.setRowCount(0)
        
        # Obtener las reservas para el salón seleccionado
        reservas = self.miconexion.MostrarReservasSalones(salon_nombre)

        # Insertar las reservas en la tabla
        for idx, reserva in enumerate(reservas):
            self.ui.tableWidget.insertRow(idx)  # Insertar una nueva fila
            for col_idx, valor in enumerate(reserva):
                item = QTableWidgetItem(str(valor))
                self.ui.tableWidget.setItem(idx, col_idx, item)

    def mostrarFormulario(self):
        """
        Método encargado de abrir el formulario de reserva si el id del salón está asignado.
        """
        if hasattr(self, 'salon_id_seleccionado'):
            self.reserva = NLTReserva()
            self.mi_ventana = NLTReserva(salon_id=self.salon_id_seleccionado)
            self.mi_ventana.exec()
        else:
            print("No se ha seleccionado un salón para realizar la reserva.")
