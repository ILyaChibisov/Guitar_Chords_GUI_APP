from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from gui.main_window import MainWindow
from config.styles import DarkTheme


class GuitarApp:
    """Основной класс приложения"""

    def __init__(self):
        self.app = QApplication([])
        self.main_window = MainWindow()

        # Настройка приложения
        self.app.setApplicationName("GuitarChords Pro")
        self.app.setApplicationVersion("1.0.0")

        # Настройка шрифта по умолчанию
        default_font = QFont("Segoe UI", 10)
        self.app.setFont(default_font)

        self.apply_styles()

    def apply_styles(self):
        """Применяет стили ко всему приложению"""
        # Применяем стили ко всему QApplication
        self.app.setStyleSheet(DarkTheme.MAIN_STYLESHEET)

    def show(self):
        """Показывает главное окно"""
        self.main_window.show()
        # Инициализируем навигацию после показа окна
        self.main_window.on_app_start()

    def exec_(self):
        """Запускает главный цикл приложения"""
        return self.app.exec_()