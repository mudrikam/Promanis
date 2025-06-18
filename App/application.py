import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
import qtawesome as qta
from .main_window import PromanisMainWindow


class PromanisApp:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.app = None
        self.window = None
    
    def initialize_app(self):
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(qta.icon('fa5s.magic'))
        
        try:
            self.window = PromanisMainWindow(self.base_dir)
            return True
        except FileNotFoundError as e:
            QMessageBox.critical(None, "Error", str(e))
            return False
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Terjadi kesalahan: {str(e)}")
            return False
    
    def run(self):
        if self.initialize_app():
            self.window.show()
            return self.app.exec()
        else:
            return 1
