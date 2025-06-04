import sys
from PyQt5.QtWidgets import QApplication
from login_window import LoginWindow
from app_menu import AppMenu

class LabShellApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = LoginWindow(self.on_login_success)
        self.login_window.show()

    def on_login_success(self, username, user_info):
        self.login_window.close()
        self.app_menu = AppMenu(username, user_info)
        self.app_menu.show()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    LabShellApp().run()
