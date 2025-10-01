from PyQt5.QtWidgets import QMainWindow
from gui.pages.songs_page import SongsPage
from config.settings import AppSettings


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_ui()

    def setup_window(self):
        """Настройка окна"""
        self.setWindowTitle(AppSettings.APP_NAME)
        self.resize(*AppSettings.DEFAULT_WINDOW_SIZE)
        self.setMinimumSize(*AppSettings.MIN_WINDOW_SIZE)

    def setup_ui(self):
        """Настройка UI главного окна"""
        # Создаем страницу песен
        self.songs_page = SongsPage(self)

        # Устанавливаем ее как центральный виджет
        self.setCentralWidget(self.songs_page)