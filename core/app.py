# core/app.py
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

        # Инициализация менеджеров конфигураций
        self.initialize_managers()

    def initialize_managers(self):
        """Инициализация менеджеров конфигураций и звука"""
        try:
            from gui.pages.songs_page import ChordConfigManager, ChordSoundPlayer

            # Создаем и настраиваем менеджер конфигураций
            config_manager = ChordConfigManager()
            if config_manager.load_configurations():
                self.main_window.set_config_manager(config_manager)
                print("✅ Менеджер конфигураций успешно загружен")
            else:
                print("❌ Не удалось загрузить менеджер конфигураций")

            # Создаем проигрыватель звуков
            sound_player = ChordSoundPlayer()
            self.main_window.set_sound_player(sound_player)
            print("✅ Проигрыватель звуков инициализирован")

        except Exception as e:
            print(f"❌ Ошибка инициализации менеджеров: {e}")
            import traceback
            traceback.print_exc()

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