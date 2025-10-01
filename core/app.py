from PyQt5.QtWidgets import QWidget
from gui.main_window import MainWindow
from config.styles import DarkTheme


class GuitarApp(QWidget):
    """Основной класс приложения"""

    def __init__(self):
        super().__init__()
        self.main_window = MainWindow()
        self.apply_styles()

    def apply_styles(self):
        """Применяет стили ко всему приложению"""
        self.setStyleSheet(DarkTheme.MAIN_STYLESHEET)

    def show(self):
        """Показывает главное окно"""
        self.main_window.show()