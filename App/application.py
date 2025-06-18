import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
import qtawesome as qta
from .main_window import PromanisMainWindow


class PromanisApp:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.app = None
        self.window = None

    def set_windows_app_user_model_id(self, app_id):
        # Set Windows AppUserModelID for correct taskbar icon grouping
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass

    def initialize_app(self):
        self.set_windows_app_user_model_id("mudrikam.promanis.wand")
        self.app = QApplication(sys.argv)
        # Set wand.ico as the main application icon (taskbar & window)
        icon_path = os.path.join(self.base_dir, "App", "wand.ico")
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))
        else:
            self.app.setWindowIcon(qta.icon('fa5s.magic'))
        try:
            self.window = PromanisMainWindow(self.base_dir)
            # Set window icon explicitly for main window
            if os.path.exists(icon_path):
                self.window.setWindowIcon(QIcon(icon_path))
            else:
                self.window.setWindowIcon(qta.icon('fa5s.magic'))
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
