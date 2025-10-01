from PyQt5.QtCore import QObject, pyqtSignal


class NavigationController(QObject):
    """Контроллер навигации между страницами"""

    page_changed = pyqtSignal(str)  # Сигнал смены страницы

    def __init__(self):
        super().__init__()
        self.current_page = "songs"
        self.pages = {}

    def register_page(self, name, page_widget):
        """Регистрирует страницу в навигаторе"""
        self.pages[name] = page_widget

    def navigate_to(self, page_name):
        """Переходит на указанную страницу"""
        if page_name in self.pages:
            # Скрываем текущую страницу
            if self.current_page in self.pages:
                self.pages[self.current_page].hide()

            # Показываем новую страницу
            self.pages[page_name].show()
            self.current_page = page_name
            self.page_changed.emit(page_name)
            return True
        return False