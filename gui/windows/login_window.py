from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from gui.widgets.buttons import ModernButton


class LoginWindow(QDialog):
    """Окно авторизации"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация - GuitarChords Pro")
        self.setFixedSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        title_label = QLabel("🎸 GuitarChords Pro")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title_label)

        # Поля ввода
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("👤 Имя пользователя")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("🔒 Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)

        # Кнопка входа
        self.login_btn = ModernButton("Войти")
        self.login_btn.clicked.connect(self.authenticate)
        layout.addWidget(self.login_btn)

        layout.addStretch()

    def authenticate(self):
        """Аутентификация пользователя"""
        username = self.username_input.text()
        password = self.password_input.text()

        # TODO: Реализовать проверку учетных данных
        if username and password:
            self.accept()