# main_window.py
from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from gui.pages.songs_page import SongsPage
from gui.pages.chords_page import ChordsPage
from config.settings import AppSettings


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_ui()

        # Менеджеры (будут установлены позже)
        self.chord_manager = None
        self.sound_player = None

    def setup_window(self):
        """Настройка окна"""
        self.setWindowTitle(AppSettings.APP_NAME)
        self.resize(*AppSettings.DEFAULT_WINDOW_SIZE)
        self.setMinimumSize(*AppSettings.MIN_WINDOW_SIZE)

    def setup_ui(self):
        """Настройка UI главного окна"""
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Создаем страницы
        self.songs_page = SongsPage()
        self.chords_page = ChordsPage()

        # Добавляем страницы в stacked widget
        self.stacked_widget.addWidget(self.songs_page)
        self.stacked_widget.addWidget(self.chords_page)

        # Устанавливаем начальную страницу
        self.stacked_widget.setCurrentWidget(self.songs_page)

    def set_chord_manager(self, chord_manager):
        """Установка менеджера аккордов для всех страниц"""
        print("🎯 Установка chord manager для страниц...")
        for page_name, page in self.pages.items():
            if hasattr(page, 'set_chord_manager'):
                page.set_chord_manager(chord_manager)
                print(f"✅ {page_name}: Chord manager установлен")
            elif hasattr(page, 'set_config_manager'):
                page.set_config_manager(chord_manager)
                print(f"✅ {page_name}: Config manager установлен")
            else:
                print(f"❌ {page_name} не имеет метода set_chord_manager или set_config_manager")

    def set_sound_player(self, sound_player):
        """Установка проигрывателя звуков для всех страниц"""
        print("🎯 Установка sound player для страниц...")
        for page_name, page in self.pages.items():
            if hasattr(page, 'set_sound_player'):
                page.set_sound_player(sound_player)
                print(f"✅ {page_name}: Sound player установлен")
            else:
                print(f"❌ {page_name} не имеет метода set_sound_player")

    def show_songs_page(self):
        """Показать страницу песен"""
        print("🎵 Переключение на страницу песен")
        self.stacked_widget.setCurrentWidget(self.songs_page)
        if hasattr(self.songs_page, 'on_page_show'):
            self.songs_page.on_page_show()

    def show_chords_page(self):
        """Показать страницу аккордов"""
        print("🎸 Переключение на страницу аккордов")
        self.stacked_widget.setCurrentWidget(self.chords_page)
        if hasattr(self.chords_page, 'on_page_show'):
            self.chords_page.on_page_show()

    def on_app_start(self):
        """Вызывается при запуске приложения"""
        print("🚀 Инициализация навигации приложения")
        self.connect_menu_signals()
        self.show_songs_page()

    def connect_menu_signals(self):
        """Подключение сигналов кнопок меню на страницах"""
        try:
            print("🔗 Подключение сигналов меню...")

            # Подключаем сигналы со страницы песен
            if hasattr(self.songs_page, 'songs_btn'):
                self.songs_page.songs_btn.clicked.connect(self.show_songs_page)
                print("✅ Кнопка ПЕСНИ подключена")
            if hasattr(self.songs_page, 'chords_btn'):
                self.songs_page.chords_btn.clicked.connect(self.show_chords_page)
                print("✅ Кнопка АККОРДЫ подключена")

            # Подключаем сигналы со страницы аккордов
            if hasattr(self.chords_page, 'songs_btn'):
                self.chords_page.songs_btn.clicked.connect(self.show_songs_page)
                print("✅ Кнопка ПЕСНИ (аккорды) подключена")
            if hasattr(self.chords_page, 'chords_btn'):
                self.chords_page.chords_btn.clicked.connect(self.show_chords_page)
                print("✅ Кнопка АККОРДЫ (аккорды) подключена")

            print("✅ Все сигналы меню успешно подключены")

        except Exception as e:
            print(f"❌ Ошибка подключения сигналов меню: {e}")

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        print("🔚 Закрытие приложения...")
        try:
            if hasattr(self.songs_page, 'cleanup'):
                self.songs_page.cleanup()
            if hasattr(self.chords_page, 'cleanup'):
                self.chords_page.cleanup()
        except Exception as e:
            print(f"⚠️ Ошибка при очистке ресурсов: {e}")

        event.accept()