#import sys
#import os

# Aseguramos que el directorio raíz esté en el PATH
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.validacion import validarFecha,validarNombre,validarNumerosEnteros,validarTelefono
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget ,QMessageBox,QDialog
from PyQt6.QtCore import QDateTime

from databases.reservas_logica import connectando
#rom DialogoCongreso_logic import NLTCongreso
from ui.Reserva import Ui_NLTForm



class NLTReserva(QDialog):
    """
    Esta clase es la que se encarga de crear el formulario de la reserva.
    
    Métodos:
    NLTverificarReserva : Este método se encargará de verificar cuando el usuario seleccione el congreso
    NLTcreandoFormulario  : Este método creará el formulario con los datos introducidos por el usuario
    NLTvolver : Este método se encargará de volver a la ventana mostrar Reserva
    """
    def __init__(self, salon_id=None):
        print(f"Inicializando NLTReserva con salon_id={salon_id}")
        super().__init__()
        # En el constructor o al inicializar la UI:
      

        self.salon_id = salon_id  # Este es el ID del salón
        self.miconexion = connectando()  # Mi clase con la lógica de la base de datos
        self.ui = Ui_NLTForm()
        self.ui.setupUi(self)  # Llamando al IU
        # En el constructor o al inicializar la UI:
        self.ui.checkBox.setVisible(False)

        self.datos_congreso_ingresados = False  # Para controlar cuando se llenen los datos del congreso

        # Crear el evento de crear
        self.ui.pushButton_2.clicked.connect(self.NLTcreandoFormulario)
        # Conectar el evento de cambio de selección del ComboBox al método verificarReserva
        self.ui.tipo_ReservasComboBox.currentIndexChanged.connect(self.NLTverificarReserva)
        # Botón volver 
        self.ui.pushButton.clicked.connect(self.NLTvolver)

        # Configurar la fecha por defecto (fecha actual)
        fecha_actual = QDateTime.currentDateTime()
        self.ui.fecha_EventoDateTimeEdit.setDateTime(fecha_actual)
        self.ui.fecha_EventoDateTimeEdit.setMinimumDateTime(fecha_actual)

        # Diccionarios para manejar las opciones
        self.ReservasDic = {
            "Banquete": 1,
            "Jornada": 2,
            "Congreso": 3
        }
        self.CocinasDic = {
            "Bufé": 1,
            "Carta": 2,
            "Pedir cita con el chef": 3,
            "No precisa": 4
        }

        # Ocultar los campos de jornadas y habitaciones por defecto
        self.ui.jornadaLabel.setVisible(False)
        self.ui.spinBox.setVisible(False)
        #self.ui.habitacionesLabel.setVisible(False)
        #self.ui.habitacionesSpinBox.setVisible(False)

    def NLTverificarReserva(self):
        """
        Este método se encarga de mostrar los campos adicionales (jornada y habitaciones) solo cuando el tipo de evento es Congreso.
        """
        tipo_reserva = self.ui.tipo_ReservasComboBox.currentText()

        if tipo_reserva == "Congreso":
            # Mostrar los campos adicionales si se selecciona Congreso
            self.ui.jornadaLabel.setVisible(True)
            self.ui.spinBox.setVisible(True)
            self.ui.checkBox.setVisible(True)
           # self.ui.habitacionesSpinBox.setVisible(True)
        else:
            # Ocultar los campos si no se selecciona Congreso
            self.ui.jornadaLabel.setVisible(False)
            self.ui.spinBox.setVisible(False)
            self.ui.checkBox.setVisible(False)
           # self.ui.habitacionesSpinBox.setVisible(False)
            self.ui.checkBox.setChecked(False)

    def NLTcreandoFormulario(self):
        """
        Este método se encarga de guardar los datos recogidos desde la UI a la base de datos.
        """
        nombre = self.ui.nombreLineEdit.text()
        Telefono = self.ui.telefonoLineEdit.text()
        fecha = self.ui.fecha_EventoDateTimeEdit.dateTime().toString("dd/MM/yyyy")
        tipo_reserva = self.ReservasDic[self.ui.tipo_ReservasComboBox.currentText()]
        Asistencia = self.ui.numeros_PersonasLineEdit.text()
        tipo_cocina = self.CocinasDic[self.ui.tipo_CocinasComboBox.currentText()]

        if not all([nombre, Telefono, fecha, Asistencia, tipo_reserva, tipo_cocina]):
            QMessageBox.warning(self, "Datos incompletos", "Por favor, complete todos los campos.")
            return

        # Validar los datos introducidos por el usuario
        if not validarNombre(nombre):
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacío, tienes que introducir caracteres.")
            return
        if not validarTelefono(Telefono):
            QMessageBox.warning(self, "Error", "Número de teléfono incorrecto.")
            return
        if not validarNumerosEnteros(Asistencia):
            QMessageBox.warning(self, "Error", "Por favor, introduzca un número entero.")
            return
        if not validarFecha(fecha):
            QMessageBox.warning(self, "Error", "Formato de fecha inválido.")
            return

        # Diccionario de datos para insertar en el formulario
        insertFormulario = {
            "tipo_reserva_id": tipo_reserva,
            "tipo_cocina_id": tipo_cocina,
            "persona": nombre,
            "telefono": Telefono,
            "fecha": fecha,
            "ocupacion": Asistencia,
            "salon_id": self.salon_id,
            "habitaciones": 0,
            "jornada": 0
        }

        # Si es Congreso, añadir los datos adicionales (jornada y habitaciones)
        if tipo_reserva == 3:  # Congreso
            #self.NLTmostrarDialogoCongreso()
            if hasattr(self, 'jornada') and hasattr(self, 'habitaciones'):
                insertFormulario["jornada"] = self.jornada
                insertFormulario["habitaciones"] = self.habitaciones
            else:
                # Si no se proporcionan los datos de jornada y habitaciones, asignar valores predeterminados
                self.jornada = 0
                self.habitaciones = 0
                insertFormulario["jornada"] = self.jornada
                insertFormulario["habitaciones"] = self.habitaciones

        # Insertar en la base de datos
        id_reserva = self.miconexion.insertFormulario(**insertFormulario)
        QMessageBox.information(self, "Reserva Exitosa", f"Tu reserva fue creada con éxito.\nID de reserva: {id_reserva}")
        QMessageBox.information(self, "Éxito", "Reserva creada exitosamente.")

    def NLTvolver(self):
        """Método para volver a la ventana Mostrar Reserva"""
        QMessageBox.information(self, "Acción Cancelada", "Regresando a Mostrar Reserva.")
        self.reject()  # Cierra el diálogo con el estado Rejected
