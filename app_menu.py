from PyQt5.QtWidgets import (
    QWidget, QPushButton, QToolButton, QVBoxLayout, QLabel, QMessageBox, QShortcut, QDialog, QLineEdit, QHBoxLayout, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QKeySequence, QPalette, QBrush
import subprocess
import os
from logger import log_action

def verify_admin_password(password):
    return password == "123"

class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Access")
        self.setModal(True)
        self.setFixedSize(400, 250)
        self.result = False

        self.setStyleSheet("""
            QDialog {
                background-color: #23272F;
                color: #E0E0E0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                border-radius: 12px;
            }
            QLabel {
                font-weight: 600;
                margin-bottom: 10px;
                font-size: 16px;
            }
            QLineEdit {
                padding: 12px;
                border-radius: 8px;
                border: 1.5px solid #3A3F4A;
                background-color: #181A20;
                color: white;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 1.5px solid #6A9AFD;
                background-color: #23272F;
                outline: none;
            }
            QPushButton {
                background-color: #6A9AFD;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                border: none;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #4477E3;
            }
            QPushButton:pressed {
                background-color: #314c81;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        label = QLabel("Enter admin password:")
        layout.addWidget(label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Admin Password")
        layout.addWidget(self.password_input)

        btn = QPushButton("Submit")
        btn.clicked.connect(self.check_password)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        # Анимация появления окна
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def check_password(self):
        if verify_admin_password(self.password_input.text()):
            self.result = True
            self.accept()
        else:
            QMessageBox.warning(self, "Access Denied", "Incorrect password!")
            self.result = False
            self.password_input.clear()
            self.password_input.setFocus()

class AppMenu(QWidget):
    def __init__(self, username, user_info, allowed_apps):
        super().__init__()
        self.username = username
        self.user_info = user_info
        self.is_admin = user_info.get("is_admin", False)
        self.allowed_apps = allowed_apps
        self.init_ui()
        self.setup_shortcuts()

    def launch_app(self, app_path):
        app_name = next((app['name'] for app in self.allowed_apps if app['path'] == app_path), None)
        if not app_name:
            QMessageBox.warning(self, "Ошибка", "Запуск этой программы запрещён.")
            log_action(self.username, "launch_app_denied", extra={"app": app_path})
            return
        try:
            subprocess.Popen([app_path], shell=True)
            log_action(self.username, "launch_app", extra={"app": app_name})
        except Exception as e:
            log_action(self.username, "launch_app_failed", extra={"app": app_name, "error": str(e)})
            QMessageBox.warning(self, "Error", f"Failed to launch {app_name}:\n{e}")

    def setup_shortcuts(self):
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+Q"), self)
        shortcut.activated.connect(self.try_admin_exit)

    def try_admin_exit(self):
        dialog = AdminLoginDialog(self)
        if dialog.exec_() and dialog.result:
            log_action(self.username, "admin_exit")
            QMessageBox.information(self, "Admin Exit", "Оболочка будет отключена. Возвращаем explorer...")

            ps_cmd = (
                'Start-Process powershell -ArgumentList '
                '"-NoProfile -ExecutionPolicy Bypass -Command '
                "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon' "
                "-Name 'Shell' -Value 'explorer.exe'" '" -Verb RunAs'
            )
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                shell=True, capture_output=True, text=True
            )
            log_action(self.username, "admin_shell_change", extra={
                "stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode
            })

            if result.returncode != 0:
                QMessageBox.warning(self, "Ошибка", f"Не удалось изменить оболочку:\n{result.stderr or result.stdout}")
                return

            self.is_admin = True
            self.close()

            subprocess.run("shutdown -r -t 0", shell=True)
        else:
            log_action(self.username, "admin_exit_failed")

    def closeEvent(self, event):
        if not self.is_admin:
            QMessageBox.warning(self, "Отклонено", "Выйти из оболочки может только администратор (Ctrl+Shift+Q).")
            event.ignore()
        else:
            event.accept()

    from PyQt5.QtWidgets import QToolButton

    def init_ui(self):
        self.setWindowTitle(f"Welcome, {self.username}")
        self.showFullScreen()

        # ====== ФОН ======
        bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img/background1.jpg")
        if os.path.exists(bg_path):
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
        # =================

        # ====== СТИЛЬ ======
        self.setStyleSheet("""
            QWidget {
                color: #E0E0E0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QToolButton {
                background: transparent;
                border: none;
                padding: 12px 8px 0px 8px;
                margin: 18px;
                font-size: 16px;
                font-weight: normal;
                min-width: 88px;
                max-width: 112px;
            }
            QToolButton:pressed {
                background: rgba(50, 100, 200, 0.14);
                border-radius: 12px;
            }
            QToolButton:hover {
                background: rgba(100, 160, 255, 0.18);
                border-radius: 12px;
            }
            QLabel#hint_label {
                color: #A0A0A0;
                font-style: italic;
                margin-top: 30px;
                font-size: 14px;
            }
            QLabel#greeting_label {
                font-size: 30px;
                font-weight: bold;
            }
        """)
        # ==================

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        # Приветствие
        greeting = QLabel(f"Привет, {self.username}!")
        greeting.setObjectName("greeting_label")
        greeting.setFont(QFont("Segoe UI", 32, QFont.Bold))
        greeting.setAlignment(Qt.AlignCenter)
        layout.addWidget(greeting)

        # Кнопки приложений
        app_layout = QGridLayout()
        app_layout.setSpacing(32)
        app_layout.setAlignment(Qt.AlignCenter)

        base_dir = os.path.dirname(os.path.abspath(__file__))

        for i, app in enumerate(self.allowed_apps):
            btn = QToolButton()
            btn.setText(app['name'])
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            icon_path = app.get('icon')
            if icon_path:
                # Поддержка относительных и абсолютных путей
                if not os.path.isabs(icon_path):
                    icon_path = os.path.join(base_dir, icon_path)
                if os.path.exists(icon_path):
                    btn.setIcon(QIcon(icon_path))
                    btn.setIconSize(QSize(64, 64))  # как на винде
            btn.setAutoRaise(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(app['name'])
            btn.clicked.connect(lambda checked, p=app['path']: self.launch_app(p))
            row = i // 6  # по 6 иконок в ряд, можно поменять
            col = i % 6
            app_layout.addWidget(btn, row, col, alignment=Qt.AlignCenter)

        layout.addLayout(app_layout)

        # Подсказка для выхода
        hint_label = QLabel("Press Ctrl+Shift+Q for admin exit")
        hint_label.setObjectName("hint_label")
        hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint_label)

        self.setLayout(layout)

