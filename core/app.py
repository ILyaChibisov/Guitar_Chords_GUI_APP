from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from config.styles import DarkTheme


class GuitarApp:
    """Основной класс приложения"""

    def __init__(self):
        self.app = QApplication([])
        self.main_window = MainWindow()
        self.apply_styles()

    def apply_styles(self):
        """Применяет стили ко всему приложению"""
        # Применяем стили ко всему QApplication
        self.app.setStyleSheet(DarkTheme.MAIN_STYLESHEET)

    def show(self):
        """Показывает главное окно"""
        self.main_window.show()

    def exec_(self):
        """Запускает главный цикл приложения"""
        return self.app.exec_()