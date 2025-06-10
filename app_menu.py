from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox, QShortcut, QDialog, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QFont
import subprocess

from logger import log_action

def verify_admin_password(password):

    return password == "admin123"

class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Access")
        self.setModal(True)
        self.result = False

        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: #E0E0E0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QLabel {
                font-weight: 600;
                margin-bottom: 10px;
            }
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                border: 1.5px solid #333333;
                background-color: #121212;
                color: white;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 1.5px solid #4CAF50;
                background-color: #222222;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                border: none;
                margin-top: 15px;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:pressed {
                background-color: #3E8E41;
            }
        """)

        layout = QVBoxLayout()

        label = QLabel("Enter admin password:")
        layout.addWidget(label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        btn = QPushButton("Submit")
        btn.clicked.connect(self.check_password)
        layout.addWidget(btn)

        self.setLayout(layout)

    def check_password(self):
        if verify_admin_password(self.password_input.text()):
            self.result = True
            self.accept()
        else:
            QMessageBox.warning(self, "Access Denied", "Incorrect password!")
            self.result = False
            self.password_input.clear()
            self.password_input.setFocus()

import os
from PyQt5.QtGui import QIcon
class AppMenu(QWidget):
    def __init__(self, username, user_info):
        super().__init__()
        self.username = username
        self.user_info = user_info
        self.is_admin = user_info.get("is_admin", False)
        self.init_ui()
        self.setup_shortcuts()

    def launch_app(self, app_name):
        allowed = self.user_info.get("allowed_apps", [])
        if app_name not in allowed:
            QMessageBox.warning(self, "Ошибка", "Запуск этой программы запрещён.")
            log_action(self.username, "launch_app_denied", extra={"app": app_name})
            return
        try:
            subprocess.Popen([app_name], shell=True)
        except Exception as e:
            log_action(self.username, "launch_app_failed", extra={"app": app_name, "error": str(e)})
            QMessageBox.warning(self, "Error", f"Failed to launch {app_name}:\n{e}")

    def confirm_logout(self):
        reply = QMessageBox.question(
            self, "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            log_action(self.username, "logout")
            self.close()

    def setup_shortcuts(self):
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+Q"), self)
        shortcut.activated.connect(self.try_admin_exit)

    def try_admin_exit(self):
        dialog = AdminLoginDialog(self)
        if dialog.exec_() and dialog.result:
            log_action(self.username, "admin_exit")
            QMessageBox.information(self, "Admin Exit", "Admin exit confirmed.")
            self.is_admin = True
            self.close()
        else:
            log_action(self.username, "admin_exit_failed")

    def closeEvent(self, event):
        # Запрет закрытия оболочки для не-админа
        if not self.is_admin:
            QMessageBox.warning(self, "Отклонено", "Выйти из оболочки может только администратор (Ctrl+Shift+Q).")
            event.ignore()
        else:
            event.accept()

    def init_ui(self):
        self.setWindowTitle(f"Welcome, {self.username}")
        self.showFullScreen()

        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #E0E0E0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QLabel {
                font-weight: 600;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                min-width: 200px;
                max-width: 200px;
                margin: 8px auto;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:pressed {
                background-color: #3E8E41;
            }
            QLabel#hint_label {
                color: #888888;
                font-style: italic;
                margin-top: 20px;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        greeting = QLabel(f"Hello, {self.username}!")
        greeting.setFont(QFont("Segoe UI", 28, QFont.Bold))
        greeting.setAlignment(Qt.AlignCenter)
        layout.addWidget(greeting)

        for app in self.user_info.get("allowed_apps", []):
            btn = QPushButton(app['name'])
            if 'icon' in app and os.path.exists(app['icon']):
                btn.setIcon(QIcon(app['icon']))
            btn.clicked.connect(lambda checked, p=app['path']: self.launch_app(p))
            layout.addWidget(btn)

        hint_label = QLabel("Press Ctrl+Shift+Q for admin exit")
        hint_label.setObjectName("hint_label")
        hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint_label)

        self.setLayout(layout)