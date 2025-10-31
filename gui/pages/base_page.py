# gui/pages/base_page.py
from PyQt5.QtWidgets import QWidget


class BasePage(QWidget):
    """Базовый класс для всех страниц приложения"""

    def __init__(self, page_name, parent=None):
        super().__init__(parent)
        self.page_name = page_name
        self.is_initialized = False

    def initialize_page(self):
        """Инициализация страницы - должен быть переопределен в дочерних классах"""
        if not self.is_initialized:
            self.setup_ui()
            self.is_initialized = True

    def setup_ui(self):
        """Настройка UI - должен быть переопределен в дочерних классах"""
        raise NotImplementedError("Метод setup_ui должен быть реализован в дочернем классе")

    def on_page_show(self):
        """Вызывается при показе страницы"""
        pass

    def on_page_hide(self):
        """Вызывается при скрытии страницы"""
        pass