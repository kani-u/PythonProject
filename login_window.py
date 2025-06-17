from PyQt5.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QVBoxLayout, QLabel,
    QMessageBox, QHBoxLayout, QShortcut, QDialog
)
from PyQt5.QtGui import QPixmap, QFont, QKeySequence, QPalette, QBrush
from PyQt5.QtCore import Qt
import subprocess
import os

from user_db import verify_user
from logger import log_action


def verify_admin_password(password):
    return password == "123"


class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Access")
        self.setModal(True)
        self.result = False

        self.setStyleSheet("""
            QDialog {
                background-color: #23272F;
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
                background-color: #181A20;
                color: white;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 1.5px solid #6A9AFD;
                background-color: #23272F;
            }
            QPushButton {
                background-color: #6A9AFD;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                border: none;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #4477E3;
            }
            QPushButton:pressed {
                background-color: #314c81;
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


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.allow_close = False
        self.setup_shortcuts()
        self.init_ui()

    def setup_shortcuts(self):
        # Ctrl+Shift+Q для выхода из оболочки (админский выход)
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+Q"), self)
        shortcut.activated.connect(self.try_admin_exit)

    def try_admin_exit(self):
        # Диалог для ввода админ-пароля и возврата explorer.exe в shell
        dialog = AdminLoginDialog(self)
        if dialog.exec_() and dialog.result:
            log_action("admin", "admin_exit")
            QMessageBox.information(self, "Admin Exit", "Оболочка будет отключена. Возвращаем explorer...")

            # Команда для изменения оболочки (shell) через PowerShell с UAC
            ps_cmd = (
                'Start-Process powershell -ArgumentList '
                '"-NoProfile -ExecutionPolicy Bypass -Command '
                "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon' "
                "-Name 'Shell' -Value 'explorer.exe'" '" -Verb RunAs'
            )

            # Запускаем PowerShell с повышением прав
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                shell=True, capture_output=True, text=True
            )
            log_action("admin", "admin_shell_change", extra={
                "stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode
            })

            if result.returncode != 0:
                QMessageBox.warning(self, "Ошибка", f"Не удалось изменить оболочку:\n{result.stderr or result.stdout}")
                return

            self.allow_close = True
            self.close()

            # Перезагрузка системы для применения изменений
            subprocess.run("shutdown -r -t 0", shell=True)
        else:
            log_action("admin", "admin_exit_failed")

    def init_ui(self):
        self.setWindowTitle("Lab Shell - Login")
        self.showFullScreen()

        # ====== ФОН ======
        bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img/background.jpg")
        if os.path.exists(bg_path):
            # Показываем окно, чтобы размеры были актуальны
            super().showFullScreen()
            # Берем актуальные размеры экрана
            screen_rect = self.screen().geometry()
            bg_pixmap = QPixmap(bg_path).scaled(
                screen_rect.width(),
                screen_rect.height(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(bg_pixmap))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
            self.update()
        # ====== ФОН ======

        self.setStyleSheet("""
            QWidget {

                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 18px;
                color: #E0E0E0;
            }

            QLineEdit {
                padding: 14px;
                font-size: 17px;
                border-radius: 12px;
                border: 1.5px solid #394867;
                background-color: #212834EE;
                color: #FAFAFA;
            }
            QLineEdit:focus {
                border: 2px solid #6A9AFD;
                background-color: #283042F0;
            }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 #6A9AFD, stop:1 #1B2945);
                color: white;
                padding: 13px;
                font-size: 17px;
                font-weight: bold;
                border-radius: 12px;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:1, y1:0, x2:0, y2:1,
                           stop:0 #4477E3, stop:1 #22325C);
            }
            QPushButton:pressed {
                background-color: #314c81;
            }

            QLabel {
                font-weight: 600;
                color: #E0E0E0;
            }

            QWidget#form_wrapper {
                background: rgba(24, 28, 40, 0.85);
                border-radius: 24px;
                padding: 38px;
            }
        """)

        logo = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "welcome_photo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo.setPixmap(logo_pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo.setText("🧪🔬")
            logo.setFont(QFont("Segoe UI Emoji", 64))
        logo.setAlignment(Qt.AlignCenter)

        welcome = QLabel("Добро пожаловать!")
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setFont(QFont("Segoe UI", 30, QFont.Bold))

        subtitle = QLabel("Secure access to your digital lab")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 16))
        subtitle.setStyleSheet("color: #B0B5C7; font-weight: 400; margin-bottom: 16px;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.handle_login)

        form_layout = QVBoxLayout()
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(login_button)
        form_layout.setSpacing(22)

        form_wrapper = QWidget()
        form_wrapper.setObjectName("form_wrapper")
        form_wrapper.setLayout(form_layout)
        form_wrapper.setMaximumWidth(370)

        main_layout = QVBoxLayout()
        main_layout.addStretch(1)
        main_layout.addWidget(logo)
        main_layout.addWidget(welcome)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(10)
        main_layout.addWidget(form_wrapper)
        main_layout.addStretch(2)

        container = QWidget()
        container.setMinimumWidth(400)
        container.setMaximumWidth(500)
        container.setLayout(main_layout)

        outer_layout = QHBoxLayout()
        outer_layout.addStretch(1)
        outer_layout.addWidget(container)
        outer_layout.addStretch(1)

        self.setLayout(outer_layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        valid, user_info = verify_user(username, password)
        if valid:
            log_action(username, "login_success")
            self.allow_close = True  # После успешного входа разрешаем закрытие
            self.on_login_success(username, user_info)
            self.close()
        else:
            log_action(username, "login_failed")
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")

    def closeEvent(self, event):
        if self.allow_close:
            event.accept()
        else:
            QMessageBox.warning(self, "Внимание", "Выход из оболочки запрещён!\n(Для сброса: Ctrl+Shift+Q)")
            event.ignore()