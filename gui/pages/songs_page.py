# gui/pages/songs_page.py
import os
import re
import html
import json
import tempfile
import pandas as pd
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QListWidget, QTextBrowser, QLabel,
                             QFrame, QScrollArea, QSizePolicy, QComboBox)
from PyQt5.QtCore import QUrl, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from .base_page import BasePage
from gui.widgets.buttons import ModernButton, MenuButton, ChordButton, SoundButtonLarge, ChordVariantButton, \
    PaginationButton
from gui.widgets.labels import AdaptiveChordLabel
from gui.widgets.media import ScrollChordButtonsWidget
from database.queries import SongQueries
import database.db_scripts as db
from config.styles import DarkTheme

# Импортируем систему отображения аккордов
try:
    from drawing_elements import DrawingElements

    print("✅ DrawingElements загружен")
except ImportError as e:
    print(f"❌ Ошибка загрузки DrawingElements: {e}")
    DrawingElements = None

# Импортируем данные аккордов из const
try:
    from const import CHORDS_TYPE_LIST, CHORDS_TYPE_NAME_LIST_DSR

    # Создаем общий словарь аккордов и их описаний
    CHORDS_DATA = {}
    for chords_list, desc_list in zip(CHORDS_TYPE_LIST, CHORDS_TYPE_NAME_LIST_DSR):
        for chord, description in zip(chords_list, desc_list):
            CHORDS_DATA[chord] = description

    print(f"✅ Загружено {len(CHORDS_DATA)} аккордов с описаниями")

except ImportError as e:
    print(f"⚠️ Не удалось загрузить данные аккордов из const: {e}")
    CHORDS_DATA = {}


class ChordSoundPlayer:
    """Проигрыватель звуков аккордов"""

    def __init__(self):
        self.sounds_dir = os.path.join("source", "sounds")
        self.player = QMediaPlayer()

    def play_chord_sound(self, chord_name, variant="1"):
        """Воспроизведение звука аккорда"""
        try:
            # Пробуем разные варианты имен файлов
            sound_files = [
                os.path.join(self.sounds_dir, f"{chord_name}/{chord_name}_{variant}.mp3")
            ]

            for sound_file in sound_files:
                if os.path.exists(sound_file):
                    media_content = QMediaContent(QUrl.fromLocalFile(sound_file))
                    self.player.setMedia(media_content)
                    self.player.play()
                    print(f"🔊 Воспроизведение: {os.path.basename(sound_file)}")
                    return True

            print(f"❌ Звуковой файл не найден для аккорда {chord_name}")
            return False

        except Exception as e:
            print(f"❌ Ошибка воспроизведения звука: {e}")
            return False


class ChordConfigManager:
    """Менеджер конфигураций аккордов - работает через новый ChordManager"""

    def __init__(self):
        self.chord_configs_cache = {}
        self.load_configurations()

    def load_configurations(self):
        """Загрузка конфигураций из Python модулей"""
        try:
            print("🎵 Загрузка конфигураций из Python модулей...")

            # Пытаемся загрузить из нового chord_manager
            try:
                from core.chord_manager import ChordManager
                if ChordManager.is_initialized():
                    print("✅ Данные аккордов загружены из chord_manager")

                    # Получаем все аккорды
                    all_chords = ChordManager.get_all_chords()
                    print(f"📊 Всего аккордов в системе: {len(all_chords)}")

                    # Создаем кэш конфигураций из Python данных
                    self.create_chord_configs_from_python()
                    print(f"📊 Создано конфигураций: {len(self.chord_configs_cache)}")
                    return True

            except ImportError as e:
                print(f"⚠️ Не удалось загрузить chord_manager: {e}")

            return False

        except Exception as e:
            print(f"❌ Ошибка загрузки конфигураций: {e}")
            import traceback
            traceback.print_exc()
            return False

    def create_chord_configs_from_python(self):
        """Создание кэша конфигураций аккордов из Python данных"""
        try:
            from core.chord_manager import ChordManager

            all_chords = ChordManager.get_all_chords()

            for chord_name in all_chords:
                chord_data = ChordManager.get_chord_data(chord_name)
                if chord_data:
                    # Получаем варианты аккорда
                    variants = chord_data.get('variants', [])

                    for variant in variants:
                        variant_num = variant.get('variant_number', 1)
                        variant_key = f"{chord_name}v{variant_num}" if variant_num > 1 else chord_name

                        # Используем данные из нового формата с разделением на пальцы/ноты
                        drawing_elements_fingers = variant.get('drawing_elements_fingers', {})
                        drawing_elements_notes = variant.get('drawing_elements_notes', {})

                        self.chord_configs_cache[variant_key] = {
                            'base_info': {
                                'chord': chord_name,
                                'variant': str(variant_num),
                                'caption': variant.get('description', ''),
                                'type': chord_data.get('type', '')
                            },
                            'crop_rect': variant.get('crop_rect'),
                            'drawing_elements_fingers': drawing_elements_fingers,
                            'drawing_elements_notes': drawing_elements_notes,
                            'sound_files': variant.get('sound_files', [])
                        }

            print(f"✅ Создано {len(self.chord_configs_cache)} конфигураций из Python данных")

        except Exception as e:
            print(f"❌ Ошибка создания конфигураций из Python данных: {e}")

    def get_chord_config(self, chord_name):
        """Получение конфигурации аккорда с улучшенным поиском"""
        names_to_try = [
            chord_name,
            f"{chord_name}v1", f"{chord_name}v2", f"{chord_name}v3",
            f"{chord_name}v4", f"{chord_name}v5", f"{chord_name}v6",
            chord_name.upper(),
            chord_name.upper().replace('M', 'm'),
        ]

        for name in names_to_try:
            if name in self.chord_configs_cache:
                return self.chord_configs_cache[name]
        return None

    def get_chord_variants_count(self, chord_name):
        """Получение количества вариантов для аккорда"""
        try:
            from core.chord_manager import ChordManager
            variants = ChordManager.get_chord_variants(chord_name)
            return len(variants) if variants else 1
        except Exception as e:
            print(f"❌ Ошибка получения количества вариантов: {e}")
            return 1

    def get_base_image_path(self):
        """Получение пути к базовому изображению"""
        try:
            from core.chord_manager import ChordManager
            return ChordManager.get_template_image_path()
        except ImportError as e:
            print(f"⚠️ Ошибка импорта ChordManager: {e}")

        # Запасной вариант
        return os.path.join("source", "img.png")


class SongsPage(BasePage):
    """Страница песен и аккордов"""

    def __init__(self, parent=None):
        super().__init__("songs", parent)

        # Переменные для пагинации аккордов
        self.chords_per_page = 8
        self.current_page = 0
        self.unique_chords = []

        # Остальные переменные
        self.chords_list = []
        self.current_chord_name = ""
        self.current_song_title = ""
        self.current_variant = 1

        # Настройки отображения аккордов
        self.current_display_type = "fingers"  # По умолчанию пальцы

        # Менеджер конфигураций аккордов
        self.config_manager = ChordConfigManager()
        self.sound_player = ChordSoundPlayer()

        self.player = QMediaPlayer()
        self.player.error.connect(self.handle_error)

        self.initialize_page()

    def get_chord_description(self, chord_name):
        """Получает описание аккорда из данных const"""
        names_to_try = [
            chord_name,
            chord_name.upper(),
            chord_name.upper().replace('M', 'm'),
            chord_name.upper().replace('М', 'm'),
        ]

        for name in names_to_try:
            if name in CHORDS_DATA:
                return CHORDS_DATA[name]

        return f"Гитарный аккорд {chord_name}"

    def setup_ui(self):
        """Настройка UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Главное меню сверху
        menu_widget = QFrame()
        menu_layout = QHBoxLayout(menu_widget)
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_layout.setSpacing(10)
        menu_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопки главного меню
        self.songs_btn = MenuButton("🎵 ПЕСНИ")
        self.chords_btn = MenuButton("🎸 АККОРДЫ")
        self.tuner_btn = MenuButton("🎵 ТЮНЕР")
        self.learning_btn = MenuButton("📚 ОБУЧЕНИЕ")
        self.theory_btn = MenuButton("🎼 МУЗЫКАЛЬНАЯ ТЕОРИЯ")

        menu_layout.addWidget(self.songs_btn)
        menu_layout.addWidget(self.chords_btn)
        menu_layout.addWidget(self.tuner_btn)
        menu_layout.addWidget(self.learning_btn)
        menu_layout.addWidget(self.theory_btn)

        main_layout.addWidget(menu_widget)

        # ОСНОВНОЙ КОНТЕНТ
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # ЛЕВАЯ ЧАСТЬ
        left_widget = QFrame()
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.song_title_label = QLabel("🎵 Текст песни с аккордами")
        self.song_title_label.setStyleSheet(DarkTheme.SONG_TITLE_STYLE)
        self.song_title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.song_title_label)

        self.song_text = QTextBrowser()
        self.song_text.setReadOnly(True)
        self.song_text.setOpenLinks(False)
        self.song_text.anchorClicked.connect(self.chord_clicked)
        self.song_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.song_text.setWordWrapMode(True)
        left_layout.addWidget(self.song_text, 1)

        # КОНТЕЙНЕР ДЛЯ АККОРДОВ
        self.chords_main_container = QWidget()
        self.chords_main_container.setStyleSheet("background: transparent; border: none;")
        self.chords_main_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.chords_main_container.setMinimumHeight(80)

        chords_main_layout = QVBoxLayout(self.chords_main_container)
        chords_main_layout.setContentsMargins(0, 0, 0, 0)
        chords_main_layout.setSpacing(0)

        chords_pagination_container = QWidget()
        chords_pagination_container.setStyleSheet("background: transparent; border: none;")
        chords_pagination_layout = QHBoxLayout(chords_pagination_container)
        chords_pagination_layout.setContentsMargins(0, 0, 0, 0)
        chords_pagination_layout.setSpacing(15)

        self.scroll_left_btn = PaginationButton("◀")
        self.scroll_left_btn.clicked.connect(self.previous_page)
        self.scroll_left_btn.hide()

        self.scroll_chords_widget = ScrollChordButtonsWidget()
        self.scroll_chords_widget.setMinimumWidth(650)
        self.scroll_chords_widget.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QWidget {
                background: transparent;
            }
        """)

        self.scroll_right_btn = PaginationButton("▶")
        self.scroll_right_btn.clicked.connect(self.next_page)
        self.scroll_right_btn.hide()

        chords_pagination_layout.addWidget(self.scroll_left_btn)
        chords_pagination_layout.addWidget(self.scroll_chords_widget, 1)
        chords_pagination_layout.addWidget(self.scroll_right_btn)

        chords_main_layout.addWidget(chords_pagination_container)

        chords_main_layout.addWidget(chords_pagination_container)
        self.chords_main_container.hide()
        left_layout.addWidget(self.chords_main_container)

        content_layout.addWidget(left_widget, 3)

        # ПРАВАЯ ЧАСТЬ
        right_widget = QFrame()
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        # ОБЛАСТЬ ПОИСКА
        search_frame = QFrame()
        search_layout = QVBoxLayout(search_frame)
        search_layout.setSpacing(10)
        search_layout.setContentsMargins(0, 0, 0, 0)

        search_input_container = QWidget()
        search_input_container.setStyleSheet("background: transparent; border: none;")
        search_input_layout = QHBoxLayout(search_input_container)
        search_input_layout.setSpacing(10)
        search_input_layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Введите название песни...")
        self.search_input.returnPressed.connect(self.search_songs)

        self.search_button = QPushButton("Найти")
        self.search_button.setCursor(Qt.PointingHandCursor)
        self.search_button.setFixedHeight(40)
        self.search_button.clicked.connect(self.search_songs)

        search_input_layout.addWidget(self.search_input, 3)
        search_input_layout.addWidget(self.search_button, 1)
        search_layout.addWidget(search_input_container)

        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.load_song)
        self.results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.results_list.hide()
        search_layout.addWidget(self.results_list)

        right_layout.addWidget(search_frame)

        # Область аккордов
        chords_frame = QFrame()
        chords_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chords_frame.setStyleSheet("background: transparent; border: none;")
        chords_layout_right = QVBoxLayout(chords_frame)
        chords_layout_right.setSpacing(1)

        chord_info_widget = QWidget()
        chord_info_widget.setStyleSheet("background: transparent; border: none;")
        chord_info_layout = QVBoxLayout(chord_info_widget)
        chord_info_layout.setSpacing(0)
        chord_info_layout.setContentsMargins(0, 0, 0, 0)

        self.chord_name_label = QLabel("")
        self.chord_name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
                padding: 1px;
                margin: 0px;
                background: transparent;
                border: none;
                line-height: 1.2;
            }
        """)
        self.chord_name_label.setAlignment(Qt.AlignCenter)
        chord_info_layout.addWidget(self.chord_name_label)

        self.chord_description_label = QLabel("")
        self.chord_description_label.setStyleSheet("""
            QLabel {
                color: transparent;
                font-size: 0px;
                text-align: center;
                padding: 2px;
                margin: 0px;
                background: transparent;
                border: none;
                max-height: 0px;
            }
        """)
        self.chord_description_label.setAlignment(Qt.AlignCenter)
        self.chord_description_label.setWordWrap(True)
        chord_info_layout.addWidget(self.chord_description_label)

        chords_layout_right.addWidget(chord_info_widget)

        # ИЗОБРАЖЕНИЕ АККОРДА
        self.chord_image_label = AdaptiveChordLabel()
        self.chord_image_label.clicked.connect(self.show_chord_large)
        self.chord_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chords_layout_right.addWidget(self.chord_image_label, 1)

        # ПАНЕЛЬ УПРАВЛЕНИЯ ОТОБРАЖЕНИЕМ АККОРДОВ
        control_widget = QWidget()
        control_widget.setStyleSheet("background: transparent; border: none; margin: 0px; padding: 0px;")
        control_layout = QHBoxLayout(control_widget)
        control_layout.setAlignment(Qt.AlignCenter)
        control_layout.setSpacing(5)
        control_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопка переключения ноты/пальцы
        self.display_toggle_btn = QPushButton("🎵 Ноты")
        self.display_toggle_btn.setCheckable(True)
        self.display_toggle_btn.setChecked(False)
        self.display_toggle_btn.setFixedSize(80, 24)
        self.display_toggle_btn.clicked.connect(self.toggle_display_type)

        # Кнопка звука
        self.sound_btn = QPushButton("🔊 Слушать")
        self.sound_btn.setFixedSize(70, 24)
        self.sound_btn.clicked.connect(self.play_chord_sound)

        control_layout.addWidget(self.display_toggle_btn)
        control_layout.addWidget(self.sound_btn)

        chords_layout_right.addWidget(control_widget)

        # ВАРИАНТЫ АККОРДА
        self.variants_container = QWidget()
        self.variants_container.setStyleSheet("background: transparent; border: none;")
        self.variants_layout = QHBoxLayout(self.variants_container)
        self.variants_layout.setAlignment(Qt.AlignCenter)
        self.variants_layout.setSpacing(8)

        chords_layout_right.addWidget(self.variants_container)

        right_layout.addWidget(chords_frame, 1)
        content_layout.addWidget(right_widget, 2)
        main_layout.addLayout(content_layout, 1)

    def apply_styles(self):
        """Применяет стили ко всем элементам страницы"""
        self.songs_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.chords_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.tuner_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.learning_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.theory_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)

        self.song_title_label.setStyleSheet(DarkTheme.SONG_TITLE_STYLE)

        self.search_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                padding: 12px 20px;
                color: white;
                font-size: 14px;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background: rgba(255, 255, 255, 0.15);
            }
        """)

        self.search_button.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)

        self.song_text.setStyleSheet("""
            QTextBrowser {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-size: 13px;
                line-height: 1.4;
            }
        """)

        self.results_list.setStyleSheet("""
            QListWidget {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 5px;
                color: white;
                font-size: 14px;
                outline: none;
            }
            QListWidget::item {
                background: transparent;
                border-radius: 10px;
                padding: 10px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background: rgba(52, 152, 219, 0.3);
                border: 1px solid rgba(52, 152, 219, 0.5);
            }
            QListWidget::item:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)

        # СТИЛИ ДЛЯ КНОПОК УПРАВЛЕНИЯ
        self.display_toggle_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5D6D7E, stop:1 #34495E);
                border: 1px solid #2C3E50;
                border-radius: 6px;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 2px 4px;
                min-width: 80px;
                min-height: 18px;
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27AE60, stop:1 #229954);
                border: 1px solid #1E8449;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6C7A89, stop:1 #415B76);
            }
            QPushButton:checked:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ECC71, stop:1 #27AE60);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2C3E50, stop:1 #34495E);
                padding: 3px 3px 1px 5px;
            }
            QPushButton:checked:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E8449, stop:1 #145A32);
            }
        """)

        self.sound_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498DB, stop:1 #2980B9);
                border: 1px solid #2471A3;
                border-radius: 6px;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 2px 4px;
                min-width: 70px;
                min-height: 18px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5DADE2, stop:1 #3498DB);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2471A3, stop:1 #1B4F72);
                padding: 3px 3px 1px 5px;
            }
        """)

        self.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)

    def initialize_page(self):
        """Инициализация страницы"""
        if not self.is_initialized:
            self.setup_ui()
            self.connect_signals()
            self.apply_styles()
            self.is_initialized = True

    def connect_signals(self):
        """Подключение сигналов"""
        pass

    def search_songs(self):
        """Поиск песен в базе данных"""
        try:
            query = self.search_input.text().strip()
            if not query:
                return

            results = db.select_search_text(query)

            self.results_list.clear()
            for elem in results:
                self.results_list.addItem(elem)

            self.results_list.show()
            self.search_input.clear()
            self.adjust_results_list_height()

        except Exception as e:
            print(f"Ошибка поиска: {e}")

    def adjust_results_list_height(self):
        """Динамически регулирует высоту списка результатов"""
        item_count = self.results_list.count()
        if item_count == 0:
            self.results_list.setFixedHeight(0)
            self.results_list.hide()
        else:
            item_height = 50
            max_height = min(item_count, 6) * item_height + 20
            self.results_list.setFixedHeight(max_height)
            self.results_list.show()

    def resizeEvent(self, event):
        """Обработчик изменения размера окна"""
        super().resizeEvent(event)
        if hasattr(self, 'chord_image_label') and self.chord_image_label:
            self.chord_image_label.updatePixmap()
        if hasattr(self, 'scroll_chords_widget') and self.scroll_chords_widget:
            self.scroll_chords_widget.scroll_to_center()

    def load_song(self, item):
        """Загрузка выбранной песни"""
        if not item:
            return

        self.sound_btn.hide()
        self.chord_name_label.setText("")
        self.chord_description_label.setText("")

        try:
            # Очистка предыдущих элементов
            for i in reversed(range(self.variants_layout.count())):
                widget = self.variants_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            chords_layout = self.scroll_chords_widget.chords_layout
            for i in reversed(range(chords_layout.count())):
                widget = chords_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            self.chords_main_container.hide()

            self.current_chord_name = ""
            self.current_song_title = item.text()
            self.current_variant = 1

            self.song_title_label.setText(f"🎵 {self.current_song_title}")

            song_info = db.select_chord_song_info(self.current_song_title)

            with open(f'{song_info[4]}', 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()

            chords_raw = song_info[3]
            if chords_raw:
                self.chords_list = [ch.strip() for ch in chords_raw.split(',') if ch.strip()]
            else:
                self.chords_list = []

            self.create_chord_buttons()

            if len(lines) >= 3:
                lines = lines[3:]

            # Подготавливаем текст
            raw_text = ''.join(lines)

            from utils.chord_parser import ChordParser

            if self.chords_list:
                processed_text = ChordParser.word_by_word_processing(raw_text, self.chords_list)
            else:
                lines_clean = [line for line in raw_text.split('\n') if line.strip()]
                processed_text = '<br>'.join(html.escape(line) for line in lines_clean)

            styled_text = f"""
            <div style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt; line-height: 1.4; color: #ecf0f1; white-space: pre-wrap;">
                {processed_text}
            </div>
            """
            self.song_text.setHtml(styled_text)

            if self.chords_list:
                first_chord = self.chords_list[0]
                chord_url = QUrl(first_chord)
                self.chord_clicked(chord_url)

        except Exception as e:
            print(f"Ошибка загрузки песни: {e}")
            import traceback
            traceback.print_exc()

    def create_chord_buttons(self):
        """Создает кнопки аккордов с пагинацией"""
        chords_layout = self.scroll_chords_widget.chords_layout
        for i in reversed(range(chords_layout.count())):
            widget = chords_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not self.chords_list:
            self.chords_main_container.hide()
            return

        self.unique_chords = sorted(set(self.chords_list))
        self.current_page = 0
        self.update_pagination_buttons()
        self.show_current_page()

    def show_current_page(self):
        """Показывает кнопки аккордов для текущей страницы"""
        chords_layout = self.scroll_chords_widget.chords_layout

        for i in reversed(range(chords_layout.count())):
            widget = chords_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        start_index = self.current_page * self.chords_per_page
        end_index = min(start_index + self.chords_per_page, len(self.unique_chords))

        for i in range(start_index, end_index):
            chord = self.unique_chords[i]
            btn = ChordButton(chord)
            btn.clicked.connect(lambda checked, c=chord: self.on_chord_button_clicked(c))
            chords_layout.addWidget(btn)

        self.scroll_chords_widget.scroll_to_center()
        self.chords_main_container.show()

    def update_pagination_buttons(self):
        """Обновляет состояние кнопки пагинации"""
        total_chords = len(self.unique_chords)
        total_pages = (total_chords + self.chords_per_page - 1) // self.chords_per_page

        if total_pages <= 1:
            self.scroll_left_btn.hide()
            self.scroll_right_btn.hide()
        else:
            self.scroll_left_btn.show()
            self.scroll_right_btn.show()
            self.scroll_left_btn.setEnabled(self.current_page > 0)
            self.scroll_right_btn.setEnabled(self.current_page < total_pages - 1)

    def next_page(self):
        """Переход на следующую страницу"""
        total_pages = (len(self.unique_chords) + self.chords_per_page - 1) // self.chords_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.show_current_page()
            self.update_pagination_buttons()

    def previous_page(self):
        """Переход на предыдущую страницу"""
        if self.current_page > 0:
            self.current_page -= 1
            self.show_current_page()
            self.update_pagination_buttons()

    def on_chord_button_clicked(self, chord_name):
        """Обработчик клика по кнопке аккорда"""
        chord_url = QUrl(chord_name)
        self.chord_clicked(chord_url)

    def chord_clicked(self, url):
        """Обработчик клика по аккорду в тексте песни с отладкой"""
        try:
            chord_name = url.toString()
            self.current_chord_name = chord_name
            self.current_variant = 1  # Сбрасываем на первый вариант

            print(f"\n🎯 КЛИК ПО АККОРДУ: {chord_name}")

            # ВКЛЮЧАЕМ ОТЛАДКУ
            self.debug_chord_elements(chord_name, self.current_variant)

            # Получаем описание аккорда
            chord_description = self.get_chord_description(chord_name)

            # Объединяем имя аккорда и описание в одну строку
            full_chord_info = f"{chord_name} {chord_description}"

            # Устанавливаем объединенный текст в один лейбл
            self.chord_name_label.setText(full_chord_info)
            self.chord_description_label.setText("")  # Очищаем второй лейбл

            # Показываем кнопки управления
            self.display_toggle_btn.show()
            self.sound_btn.show()

            # Очищаем предыдущие варианты
            for i in reversed(range(self.variants_layout.count())):
                widget = self.variants_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Загружаем аккорд из конфигурации
            chord_config = self.config_manager.get_chord_config(chord_name)
            if chord_config:
                print(f"✅ Загружена конфигурация для аккорда: {chord_name}")
                self.load_chord_from_config(chord_name)
            else:
                print(f"❌ Конфигурация не найдена для аккорда: {chord_name}")
                self.show_chord_not_found(chord_name)

        except Exception as e:
            print(f"❌ Ошибка загрузки аккорда: {e}")
            import traceback
            traceback.print_exc()

    def debug_chord_elements(self, chord_name, variant=1):
        """Расширенная отладка элементов аккорда"""
        print(f"\n{'=' * 80}")
        print(f"🔍 ДЕТАЛЬНАЯ ОТЛАДКА АККОРДА: {chord_name} (вариант {variant})")
        print(f"{'=' * 80}")

        try:
            from core.chord_manager import ChordManager

            # Получаем данные аккорда
            chord_data = ChordManager.get_chord_data(chord_name)
            if not chord_data:
                print(f"❌ Аккорд {chord_name} не найден в ChordManager")
                return

            print(f"📊 Основные данные аккорда:")
            print(f"   Название: {chord_data.get('name')}")
            print(f"   Заголовок: {chord_data.get('caption')}")
            print(f"   Тип: {chord_data.get('type')}")
            print(f"   Вариантов: {len(chord_data.get('variants', []))}")

            # Получаем конкретный вариант
            variant_config = ChordManager.get_chord_config(chord_name, variant)
            if not variant_config:
                print(f"❌ Вариант {variant} не найден для аккорда {chord_name}")
                return

            print(f"\n🎯 Конфигурация варианта {variant}:")
            print(f"   Номер варианта: {variant_config.get('variant_number')}")
            print(f"   Описание: {variant_config.get('description')}")
            print(f"   RAM: {variant_config.get('ram')}")
            print(f"   Barre: {variant_config.get('barre')}")

            # Элементы отрисовки для пальцев
            drawing_elements_fingers = variant_config.get('drawing_elements_fingers', {})
            print(f"\n👆 ЭЛЕМЕНТЫ ОТРИСОВКИ ДЛЯ ПАЛЬЦЕВ:")
            print(f"   Ноты: {len(drawing_elements_fingers.get('notes', []))}")
            print(f"   Баре: {len(drawing_elements_fingers.get('barres', []))}")
            print(f"   Лады: {len(drawing_elements_fingers.get('frets', []))}")
            print(f"   Открытые струны: {len(drawing_elements_fingers.get('open_notes', []))}")

            # Элементы отрисовки для нот
            drawing_elements_notes = variant_config.get('drawing_elements_notes', {})
            print(f"\n🎵 ЭЛЕМЕНТЫ ОТРИСОВКИ ДЛЯ НОТ:")
            print(f"   Ноты: {len(drawing_elements_notes.get('notes', []))}")
            print(f"   Баре: {len(drawing_elements_notes.get('barres', []))}")
            print(f"   Лады: {len(drawing_elements_notes.get('frets', []))}")
            print(f"   Открытые струны: {len(drawing_elements_notes.get('open_notes', []))}")

            # Детали по каждому типу элементов для пальцев
            print(f"\n📋 ДЕТАЛИ ДЛЯ ПАЛЬЦЕВ:")
            for element_type, elements_list in drawing_elements_fingers.items():
                print(f"\n   {element_type.upper()} ({len(elements_list)} элементов):")
                for i, element in enumerate(elements_list):
                    print(f"      {i + 1}. {json.dumps(element, indent=6, ensure_ascii=False)}")

            # Детали по каждому типу элементов для нот
            print(f"\n📋 ДЕТАЛИ ДЛЯ НОТ:")
            for element_type, elements_list in drawing_elements_notes.items():
                print(f"\n   {element_type.upper()} ({len(elements_list)} элементов):")
                for i, element in enumerate(elements_list):
                    print(f"      {i + 1}. {json.dumps(element, indent=6, ensure_ascii=False)}")

        except Exception as e:
            print(f"❌ Ошибка отладки: {e}")
            import traceback
            traceback.print_exc()

    def load_chord_from_config(self, chord_name):
        """Загрузка аккорда из конфигурации"""
        try:
            from core.chord_manager import ChordManager

            # Получаем количество вариантов динамически
            variants = ChordManager.get_chord_variants(chord_name)
            variants_count = len(variants) if variants else 1
            print(f"🎯 Для аккорда {chord_name} найдено {variants_count} вариантов")

            for variant_num in range(1, variants_count + 1):
                btn = ChordVariantButton(str(variant_num))
                btn.setProperty('variant_num', variant_num)

                # Создаем замыкание для обработчика
                def make_handler(v_num):
                    def handler():
                        self.current_variant = v_num
                        print(f"🔄 Переключение на вариант {v_num} для аккорда {chord_name}")
                        self.refresh_chord_display(chord_name)

                        # Снимаем выделение с других кнопок
                        for i in range(self.variants_layout.count()):
                            other_btn = self.variants_layout.itemAt(i).widget()
                            if other_btn and other_btn.property('variant_num') != v_num:
                                other_btn.setChecked(False)
                                other_btn.update_style()

                    return handler

                handler = make_handler(variant_num)
                btn.clicked.connect(handler)
                self.variants_layout.addWidget(btn)

            # Активируем первый вариант
            if self.variants_layout.count() > 0:
                self.activate_first_variant(chord_name)

        except Exception as e:
            print(f"❌ Ошибка загрузки аккорда из конфигурации: {e}")

    def activate_first_variant(self, chord_name):
        """Активация первого варианта"""
        try:
            # Активируем первую кнопку
            if self.variants_layout.count() > 0:
                first_btn = self.variants_layout.itemAt(0).widget()
                if first_btn:
                    first_btn.setChecked(True)
                    first_btn.update_style()

            # Показываем аккорд
            self.refresh_chord_display(chord_name)

        except Exception as e:
            print(f"❌ Ошибка активации первого варианта: {e}")

    def refresh_chord_display(self, chord_name):
        """Обновление отображения аккорда"""
        try:
            pixmap = self.generate_chord_from_config(chord_name, self.current_variant)
            if not pixmap.isNull():
                self.chord_image_label.setChordPixmap(pixmap)
                print(f"✅ Аккорд {chord_name} вариант {self.current_variant} отображен")
            else:
                print(f"❌ Не удалось сгенерировать изображение для {chord_name} вариант {self.current_variant}")
        except Exception as e:
            print(f"❌ Ошибка обновления отображения аккорда: {e}")

    def show_chord_not_found(self, chord_name):
        """Показ сообщения об отсутствии аккорда"""
        self.chord_image_label.clear()
        self.display_toggle_btn.hide()
        self.sound_btn.hide()

        # Создаем красный крестик
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.red, 4))
        painter.drawLine(10, 10, 90, 90)
        painter.drawLine(90, 10, 10, 90)
        painter.end()

        self.chord_image_label.setChordPixmap(pixmap)

    def generate_chord_from_config(self, chord_name, variant=1):
        """Генерация изображения аккорда из конфигурации с учетом типа отображения"""
        try:
            # Получаем конфигурацию для конкретного варианта
            variant_key = f"{chord_name}v{variant}" if variant > 1 else chord_name
            chord_config = self.config_manager.get_chord_config(variant_key)

            if not chord_config:
                print(f"❌ Конфигурация не найдена для: {variant_key}")
                return QPixmap()

            # Получаем элементы для текущего типа отображения
            if self.current_display_type == "fingers":
                elements_data = chord_config.get('drawing_elements_fingers', {})
                print(f"👆 Используем элементы ПАЛЬЦЕВ:")
            else:
                elements_data = chord_config.get('drawing_elements_notes', {})
                print(f"🎵 Используем элементы НОТ:")

            # Объединяем все элементы в один список для отрисовки
            all_elements = []
            for element_type, elements_list in elements_data.items():
                all_elements.extend(elements_list)
                print(f"   {element_type}: {len(elements_list)} элементов")

            if not all_elements:
                print(f"❌ Нет элементов для аккорда {variant_key} в режиме {self.current_display_type}")
                return QPixmap()

            # Применяем обводку
            elements = self.apply_outline_settings(all_elements)

            # Загружаем базовое изображение
            base_image_path = self.config_manager.get_base_image_path()
            if not base_image_path or not os.path.exists(base_image_path):
                print(f"❌ Базовое изображение не найдено: {base_image_path}")
                return QPixmap()

            original_pixmap = QPixmap(base_image_path)
            if original_pixmap.isNull():
                print(f"❌ Не удалось загрузить базовое изображение: {base_image_path}")
                return QPixmap()

            # Получаем область обрезки
            crop_rect = chord_config.get('crop_rect')
            if not crop_rect:
                print(f"❌ Нет области обрезки для аккорда {variant_key}")
                return QPixmap()

            try:
                # Проверяем тип crop_rect и преобразуем в кортеж
                if isinstance(crop_rect, dict):
                    crop_x = crop_rect.get('x', 0)
                    crop_y = crop_rect.get('y', 0)
                    crop_width = crop_rect.get('width', 0)
                    crop_height = crop_rect.get('height', 0)
                elif isinstance(crop_rect, (list, tuple)) and len(crop_rect) == 4:
                    crop_x, crop_y, crop_width, crop_height = crop_rect
                else:
                    print(f"❌ Неверный формат crop_rect: {type(crop_rect)}")
                    return QPixmap()

                # Проверяем границы
                crop_x = max(0, min(crop_x, original_pixmap.width() - 1))
                crop_y = max(0, min(crop_y, original_pixmap.height() - 1))
                crop_width = max(1, min(crop_width, original_pixmap.width() - crop_x))
                crop_height = max(1, min(crop_height, original_pixmap.height() - crop_y))

                # Создаем новое изображение размером с область обрезки с прозрачным фоном
                result_pixmap = QPixmap(crop_width, crop_height)
                result_pixmap.fill(Qt.transparent)

                painter = QPainter(result_pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setRenderHint(QPainter.SmoothPixmapTransform)

                # Копируем область из оригинального изображения
                painter.drawPixmap(0, 0, original_pixmap, crop_x, crop_y, crop_width, crop_height)

                # Рисуем элементы
                self.draw_elements_on_canvas(painter, elements, (crop_x, crop_y, crop_width, crop_height))
                painter.end()

                # Применяем масштаб
                display_width = min(400, crop_width)
                scale_factor = display_width / crop_width
                display_height = int(crop_height * scale_factor)

                scaled_pixmap = result_pixmap.scaled(
                    display_width, display_height,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )

                return scaled_pixmap

            except Exception as crop_error:
                print(f"❌ Ошибка обработки crop_rect для {chord_name} вариант {variant}: {crop_error}")
                return QPixmap()

        except Exception as e:
            print(f"❌ Ошибка генерации изображения для {chord_name} вариант {variant}: {e}")
            return QPixmap()

    def apply_outline_settings(self, elements):
        """ИСПРАВЛЕННОЕ применение настроек обводки с расширенной отладкой"""
        print(f"🎯 НАЧАЛО ОБРАБОТКИ ЭЛЕМЕНТОВ: {len(elements)} элементов")

        modified_elements = []

        for index, element in enumerate(elements):
            if not isinstance(element, dict):
                print(f"❌ Элемент {index} - не словарь: {element}")
                continue

            element_type = element.get('type', 'unknown')
            original_data = element.get('data', {})
            element_data = original_data.copy()

            print(f"\n🔍 ЭЛЕМЕНТ {index}: {element_type}")
            print(f"📋 Оригинальные данные: {json.dumps(original_data, indent=2, ensure_ascii=False)}")

            if element_type == 'barre':
                print("🎸 Обработка БАРЕ:")
                # Сохраняем оригинальный стиль или используем оранжевый по умолчанию
                original_style = element_data.get('style')
                if not original_style or original_style == 'default':
                    element_data['style'] = 'orange_gradient'
                    print(f"  🎨 Стиль: установлен 'orange_gradient' (был: {original_style})")
                else:
                    print(f"  🎨 Стиль: сохранен оригинальный '{original_style}'")

                element_data['outline_width'] = 2
                element_data['outline_color'] = [0, 0, 0]
                print(f"  📏 Обводка: ширина 2px, цвет черный")

            elif element_type == 'note':
                print("🎵 Обработка НОТЫ:")

                # СОХРАНЯЕМ оригинальные данные!
                original_style = element_data.get('style', 'default')
                original_finger = element_data.get('finger')
                original_note_name = element_data.get('note_name')
                original_display_text = element_data.get('display_text', 'finger')

                print(f"  🎨 Оригинальный стиль: {original_style}")
                print(f"  👆 Оригинальный палец: {original_finger}")
                print(f"  🎵 Оригинальное имя ноты: {original_note_name}")
                print(f"  📝 Оригинальный текст отображения: {original_display_text}")

                # Только добавляем обводку, не меняем стиль!
                element_data['outline_width'] = 2
                element_data['outline_color'] = [0, 0, 0]

                # Определяем что отображать
                if original_display_text == 'note_name' and original_note_name:
                    display_symbol = original_note_name
                    print(f"  ✅ Отображаем имя ноты: {display_symbol}")
                elif original_display_text == 'symbol' and element_data.get('symbol'):
                    display_symbol = element_data.get('symbol')
                    print(f"  ✅ Отображаем символ: {display_symbol}")
                elif original_finger:
                    display_symbol = original_finger
                    print(f"  ✅ Отображаем палец: {display_symbol}")
                else:
                    # Если ничего нет, пробуем получить из других полей
                    display_symbol = original_note_name or original_finger or '?'
                    print(f"  ⚠️  Не найдены данные, используем: {display_symbol}")

                # Убедимся что есть данные для отображения
                if not element_data.get('finger') and not element_data.get('note_name'):
                    element_data['finger'] = display_symbol
                    print(f"  🔧 Установлен finger: {display_symbol}")

                element_data['display_text'] = original_display_text
                print(f"  📝 Финальный текст отображения: {original_display_text} -> {display_symbol}")

            elif element_type == 'fret':
                print("🎻 Обработка ЛАДА:")
                original_color = element_data.get('color', [0, 0, 0])
                original_style = element_data.get('style', 'default')
                print(f"  🎨 Оригинальный цвет: {original_color}")
                print(f"  🎨 Оригинальный стиль: {original_style}")
                # Для ладов просто сохраняем оригинальные настройки
                element_data['color'] = original_color
                element_data['style'] = original_style

            elif element_type == 'open_note':
                print("🔘 Обработка ОТКРЫТОЙ СТРУНЫ:")
                original_style = element_data.get('style', 'default')
                original_symbol = element_data.get('symbol', 'O')
                print(f"  🎨 Стиль: {original_style}")
                print(f"  🔤 Символ: {original_symbol}")
                # Сохраняем оригинальные настройки

            else:
                print(f"❓ Неизвестный тип элемента: {element_type}")

            print(f"✅ Финальные данные элемента {element_type}:")
            print(f"   {json.dumps(element_data, indent=2, ensure_ascii=False)}")

            modified_elements.append({
                'type': element_type,
                'data': element_data
            })

        print(f"\n🎉 ОБРАБОТКА ЗАВЕРШЕНА: {len(modified_elements)} элементов модифицировано")
        return modified_elements

    def draw_elements_on_canvas(self, painter, elements, crop_rect):
        """Рисование элементов на canvas"""
        try:
            if not DrawingElements:
                print("❌ DrawingElements не доступен")
                return

            for element in elements:
                if element['type'] == 'fret':
                    self.draw_fret_on_canvas(painter, element['data'], crop_rect)
                elif element['type'] == 'note':
                    self.draw_note_on_canvas(painter, element['data'], crop_rect)
                elif element['type'] == 'barre':
                    self.draw_barre_on_canvas(painter, element['data'], crop_rect)
                elif element['type'] == 'open_note':
                    self.draw_open_note_on_canvas(painter, element['data'], crop_rect)

        except Exception as e:
            print(f"❌ Ошибка рисования элементов: {e}")

    def draw_fret_on_canvas(self, painter, fret_data, crop_rect):
        """Рисование лада на canvas"""
        try:
            adapted_data = self.adapt_coordinates(fret_data, crop_rect)
            DrawingElements.draw_fret(painter, adapted_data)
        except Exception as e:
            print(f"❌ Ошибка рисования лада: {e}")

    def draw_note_on_canvas(self, painter, note_data, crop_rect):
        """Рисование ноты на canvas с отладкой"""
        try:
            print(f"🎵 Данные ноты ДО адаптации: {note_data}")
            adapted_data = self.adapt_coordinates(note_data, crop_rect)
            print(f"🎵 Данные ноты ПОСЛЕ адаптации: {adapted_data}")
            DrawingElements.draw_note(painter, adapted_data)
        except Exception as e:
            print(f"❌ Ошибка рисования ноты: {e}")

    def draw_barre_on_canvas(self, painter, barre_data, crop_rect):
        """Рисование баре на canvas с правильными координатами и отладкой"""
        try:
            print(f"🎸 РИСОВАНИЕ БАРЕ:")
            print(f"   Данные баре ДО адаптации: {barre_data}")
            adapted_data = self.adapt_coordinates(barre_data, crop_rect)
            print(f"   Данные баре ПОСЛЕ адаптации: {adapted_data}")
            print(f"   Crop rect: {crop_rect}")
            # Проверяем, попадают ли координаты в область видимости
            x = adapted_data.get('x', 0)
            y = adapted_data.get('y', 0)
            width = adapted_data.get('width', 0)
            height = adapted_data.get('height', 0)
            print(f"   Позиция на canvas: x={x}, y={y}, width={width}, height={height}")
            DrawingElements.draw_barre(painter, adapted_data)

        except Exception as e:
            print(f"❌ Ошибка рисования баре: {e}")

    def draw_open_note_on_canvas(self, painter, open_note_data, crop_rect):
        """Рисование открытой ноты на canvas"""
        try:
            adapted_data = self.adapt_coordinates(open_note_data, crop_rect)
            # Для открытых нот используем специальный метод или draw_note
            DrawingElements.draw_note(painter, adapted_data)
        except Exception as e:
            print(f"❌ Ошибка рисования открытой ноты: {e}")

    def adapt_coordinates(self, element_data, crop_rect):
        """ИСПРАВЛЕННАЯ адаптация координат элементов - как в старом приложении"""
        if not crop_rect:
            return element_data.copy()

        adapted_data = element_data.copy()
        crop_x, crop_y, crop_width, crop_height = crop_rect

        original_x = element_data.get('x', 0)
        original_y = element_data.get('y', 0)

        # Простое вычитание координат обрезки для ВСЕХ элементов
        if 'x' in adapted_data:
            adapted_data['x'] = original_x - crop_x
        if 'y' in adapted_data:
            adapted_data['y'] = original_y - crop_y

        # Преобразуем в целые числа для Qt
        adapted_data['x'] = int(round(adapted_data.get('x', 0)))
        adapted_data['y'] = int(round(adapted_data.get('y', 0)))

        # ОСОБАЯ КОРРЕКЦИЯ ДЛЯ БАРЕ - ИСПРАВЛЕННАЯ ЛОГИКА
        if adapted_data.get('type') == 'barre':
            barre_width = adapted_data.get('width', 100)
            barre_height = adapted_data.get('height', 20)

            print(f"🎸 АДАПТАЦИЯ БАРЕ:")
            print(f"   Исходные координаты: ({original_x}, {original_y})")
            print(f"   После вычитания crop: ({adapted_data['x']}, {adapted_data['y']})")
            print(f"   Размеры баре: {barre_width}x{barre_height}")

            # Для баре - координаты в шаблоне указывают на ЛЕВЫЙ ВЕРХНИЙ УГОЛ
            # НЕ нужно дополнительно смещать!
            # Просто используем координаты после вычитания crop_rect

            print(f"   Финальные координаты баре: ({adapted_data['x']}, {adapted_data['y']})")

        return adapted_data

    def toggle_display_type(self):
        """Переключение между нотами и пальцами"""
        if self.display_toggle_btn.isChecked():
            self.current_display_type = "notes"
            self.display_toggle_btn.setText("👆 Пальцы")
            print("🔄 Переключение на режим НОТ")
        else:
            self.current_display_type = "fingers"
            self.display_toggle_btn.setText("🎵 Ноты")
            print("🔄 Переключение на режим ПАЛЬЦЕВ")

        self.refresh_current_chord()

    def refresh_current_chord(self):
        """Обновление отображения текущего аккорда"""
        if self.current_chord_name:
            print(f"🔄 Обновление аккорда: {self.current_chord_name}")
            self.refresh_chord_display(self.current_chord_name)

    def play_chord_sound(self):
        """Воспроизведение звука аккорда через ChordSoundPlayer"""
        if not self.current_chord_name:
            return

        try:
            from core.chord_manager import ChordSoundPlayer

            # Используем ChordSoundPlayer для воспроизведения
            success = ChordSoundPlayer.play_chord_sound(
                self.player,
                self.current_chord_name,
                self.current_variant
            )

            if not success:
                print(f"🔇 Звук для аккорда {self.current_chord_name} вариант {self.current_variant} не найден")

        except Exception as e:
            print(f"❌ Ошибка при воспроизведении звука: {e}")

    def show_chord_large(self):
        """Показ увеличенного окна с аккордом"""
        if not self.current_chord_name:
            return

        try:
            from gui.windows.chord_viewer import ChordViewerWindow

            # Создаем временное изображение для просмотра
            pixmap = self.generate_chord_from_config(self.current_chord_name, self.current_variant)
            if not pixmap.isNull():
                # Сохраняем временное изображение
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                temp_path = temp_file.name
                pixmap.save(temp_path, 'PNG')
                temp_file.close()

                # Получаем путь к звуку
                sound_path = self.get_chord_sound_path(self.current_chord_name, self.current_variant)

                viewer = ChordViewerWindow(
                    self.current_chord_name,
                    temp_path,
                    sound_path or "",
                    self
                )
                viewer.exec_()

                # Удаляем временный файл после закрытия окна
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except Exception as e:
                    print(f"⚠️ Ошибка удаления временного файла: {e}")

        except Exception as e:
            print(f"Ошибка открытия окна аккорда: {e}")
            import traceback
            traceback.print_exc()

    def get_chord_sound_path(self, chord_name, variant_index=0):
        """Получение пути к звуковому файлу аккорда"""
        try:
            sounds_dir = os.path.join("source", "sounds")
            sound_file = os.path.join(sounds_dir, f"{chord_name}/{chord_name}_{variant_index}.mp3")

            if os.path.exists(sound_file):
                return sound_file

            # Пробуем без варианта
            sound_file = os.path.join(sounds_dir, f"{chord_name}/{chord_name}.mp3")
            if os.path.exists(sound_file):
                return sound_file

            return None

        except Exception as e:
            print(f"❌ Ошибка получения пути к звуку: {e}")
            return None

    def handle_error(self, error):
        """Обработчик ошибок медиаплеера"""
        print(f"Ошибка медиаплеера: {error}")

    def on_page_show(self):
        """Вызывается при показе страницы"""
        print("Страница песен показана")

    def on_page_hide(self):
        """Вызывается при скрытии страницы"""
        print("Страница песен скрыта")

    def cleanup(self):
        """Очистка ресурсов при закрытии приложения"""
        pass