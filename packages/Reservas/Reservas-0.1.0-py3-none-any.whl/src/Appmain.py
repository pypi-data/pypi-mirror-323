import sys
from PyQt6.QtWidgets import QApplication
from src.Menu_logic import NLTMenu

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = NLTMenu()
    ventana.show()
    sys.exit(app.exec())
