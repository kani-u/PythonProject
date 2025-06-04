from PyQt5.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QVBoxLayout, QLabel,
    QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from user_db import verify_user


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Lab Shell - Login")
        self.showFullScreen()

        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 18px;
                color: #E0E0E0;
            }

            QLineEdit {
                padding: 12px;
                font-size: 16px;
                border-radius: 10px;
                border: 1.5px solid #333333;
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1.5px solid #4CAF50;
                background-color: #252525;
            }

            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                border: none;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:pressed {
                background-color: #3E8E41;
            }

            QLabel {
                font-weight: 600;
                color: #E0E0E0;
            }

            QWidget#form_wrapper {
                background-color: rgba(40, 40, 40, 0.85);
                border-radius: 20px;
                padding: 30px;
            }
        """)

        logo = QLabel()
        logo_pixmap = QPixmap("welcome_photo.png")
        logo.setPixmap(logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)

        welcome = QLabel("Welcome to Lab Shell")
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setFont(QFont("Segoe UI", 24, QFont.Bold))

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)

        form_layout = QVBoxLayout()
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(login_button)
        form_layout.setSpacing(20)

        form_wrapper = QWidget()
        form_wrapper.setObjectName("form_wrapper")
        form_wrapper.setLayout(form_layout)

        main_layout = QVBoxLayout()
        main_layout.addStretch(1)
        main_layout.addWidget(logo)
        main_layout.addSpacing(10)
        main_layout.addWidget(welcome)
        main_layout.addSpacing(20)
        main_layout.addWidget(form_wrapper)
        main_layout.addStretch(2)

        container = QWidget()
        container.setMinimumWidth(400)
        container.setMaximumWidth(600)
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
            self.on_login_success(username, user_info)
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")
