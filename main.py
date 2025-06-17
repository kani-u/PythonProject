import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from login_window import LoginWindow
from app_menu import AppMenu
import json
import os

class LabShellApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = LoginWindow(self.on_login_success)
        self.login_window.show()

    def load_allowed_apps(self):
        try:
            # Абсолютный путь к allowed_apps.json рядом с этим скриптом
            base_dir = os.path.dirname(os.path.abspath(__file__))
            apps_path = os.path.join(base_dir, "allowed_apps.json")
            with open(apps_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось загрузить allowed_apps.json:\n{e}")
            return []
        
        
    def on_login_success(self, username, user_info):
        self.login_window.close()
        allowed_apps = self.load_allowed_apps()
        self.app_menu = AppMenu(username, user_info, allowed_apps)
        self.app_menu.show()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    LabShellApp().run()