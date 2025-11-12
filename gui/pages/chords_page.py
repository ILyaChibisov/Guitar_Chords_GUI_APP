import os
import tempfile
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFrame, QScrollArea, QGridLayout, QSizePolicy, QLineEdit, QListWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen

from .base_page import BasePage
from gui.widgets.buttons import MenuButton, ChordButton, ChordVariantButton
from gui.widgets.labels import AdaptiveChordLabel
from config.styles import DarkTheme

# Импортируем данные аккордов из нового файла
try:
    from type_chords import CHORDS_TYPE_BY_NOTE, CHORDS_BY_NOTE, CHORDS_TYPE_BY_STYLE, CHORDS_BY_STYLE, \
        CHORDS_DESCRIPTIONS

    print("✅ ChordsPage: Данные аккордов загружены из type_chords.py")
except ImportError as e:
    print(f"⚠️ ChordsPage: Не удалось загрузить данные аккордов: {e}")
    # Заглушки на случай ошибки
    CHORDS_TYPE_BY_NOTE = ['A', 'A#|Bb', 'B|H', 'C', 'C#|Db', 'D', 'D#|Eb', 'E', 'F', 'F#|Gb', 'G', 'G#|Ab']
    CHORDS_BY_NOTE = {'A': ['A', 'Am']}
    CHORDS_TYPE_BY_STYLE = ['Major', 'Minor']
    CHORDS_BY_STYLE = {'Major': ['A', 'B', 'C'], 'Minor': ['Am', 'Bm', 'Cm']}
    CHORDS_DESCRIPTIONS = {'A': 'Ля мажор', 'Am': 'Ля минор'}

# Импортируем систему отображения аккордов
try:
    from drawing_elements import DrawingElements

    print("✅ ChordsPage: DrawingElements загружен")
except ImportError as e:
    print(f"❌ ChordsPage: Ошибка загрузки DrawingElements: {e}")
    DrawingElements = None


class ChordsPage(BasePage):
    """Страница аккордов с выбором по типам и нотам"""

    def __init__(self, parent=None):
        super().__init__("chords", parent)

        # Переменные для навигации
        self.current_view = "style"  # "style" или "note"
        self.selected_type = None
        self.selected_note = None
        self.current_chord_name = ""
        self.current_variant = 1

        # Настройки отображения аккордов
        self.current_display_type = "fingers"

        # Менеджер конфигураций (будет передан из main)
        self.config_manager = None
        self.sound_player = None

        # Для поиска аккордов
        self.all_chords = self.get_all_chords()

        self.initialize_page()

    def get_all_chords(self):
        """Получает список всех доступных аккордов"""
        all_chords = []
        for chords in CHORDS_BY_STYLE.values():
            all_chords.extend(chords)
        for chords in CHORDS_BY_NOTE.values():
            all_chords.extend(chords)
        return sorted(set(all_chords))

    def set_config_manager(self, config_manager):
        """Установка менеджера конфигураций"""
        self.config_manager = config_manager
        print("✅ ChordsPage: Config manager установлен")

    def set_chord_manager(self, chord_manager):
        """Альтернативное имя для совместимости"""
        self.config_manager = chord_manager
        print("✅ ChordsPage: Chord manager установлен")

    def set_sound_player(self, sound_player):
        """Установка проигрывателя звуков"""
        self.sound_player = sound_player
        print("✅ ChordsPage: Sound player установлен")

    def setup_ui(self):
        """Настройка UI страницы аккордов"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Главное меню сверху
        menu_widget = QFrame()
        menu_layout = QHBoxLayout(menu_widget)
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_layout.setSpacing(8)
        menu_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопки главного меню
        self.songs_btn = MenuButton("🎵 ПЕСНИ")
        self.chords_btn = MenuButton("🎸 АККОРДЫ")
        self.tuner_btn = MenuButton("🎵 ТЮНЕР")
        self.learning_btn = MenuButton("📚 ОБУЧЕНИЕ")
        self.theory_btn = MenuButton("🎼 ТЕОРИЯ")

        menu_layout.addWidget(self.songs_btn)
        menu_layout.addWidget(self.chords_btn)
        menu_layout.addWidget(self.tuner_btn)
        menu_layout.addWidget(self.learning_btn)
        menu_layout.addWidget(self.theory_btn)

        main_layout.addWidget(menu_widget)

        # ОСНОВНОЙ КОНТЕНТ
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # ЛЕВАЯ ЧАСТЬ - ОТОБРАЖЕНИЕ АККОРДА (ОСНОВНОЕ)
        left_widget = QFrame()
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # НАЗВАНИЕ АККОРДА НАД КАРТИНКОЙ
        self.chord_name_label = QLabel("Аккорд A (Ля мажор)")
        self.chord_name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                text-align: center;
                padding: 8px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }
        """)
        self.chord_name_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.chord_name_label)

        # ИЗОБРАЖЕНИЕ АККОРДА (КРУПНОЕ И КАЧЕСТВЕННОЕ)
        self.chord_image_label = AdaptiveChordLabel()
        self.chord_image_label.clicked.connect(self.show_chord_large)
        self.chord_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chord_image_label.setMinimumHeight(400)
        self.chord_image_label.setStyleSheet("""
            AdaptiveChordLabel {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
        """)
        left_layout.addWidget(self.chord_image_label, 1)

        # ПАНЕЛЬ УПРАВЛЕНИЯ АККОРДОМ
        chord_control_widget = QWidget()
        chord_control_widget.setStyleSheet("background: transparent; border: none;")
        chord_control_layout = QVBoxLayout(chord_control_widget)
        chord_control_layout.setSpacing(8)
        chord_control_layout.setContentsMargins(0, 0, 0, 0)

        # КНОПКИ УПРАВЛЕНИЯ
        control_buttons_widget = QWidget()
        control_buttons_widget.setStyleSheet("background: transparent; border: none;")
        control_buttons_layout = QHBoxLayout(control_buttons_widget)
        control_buttons_layout.setAlignment(Qt.AlignCenter)
        control_buttons_layout.setSpacing(10)

        # Кнопка переключения ноты/пальцы
        self.display_toggle_btn = QPushButton("🎵 Ноты")
        self.display_toggle_btn.setCheckable(True)
        self.display_toggle_btn.setChecked(False)
        self.display_toggle_btn.setFixedSize(100, 35)
        self.display_toggle_btn.hide()

        # Кнопка звука
        self.sound_btn = QPushButton("🔊 Слушать")
        self.sound_btn.setFixedSize(100, 35)
        self.sound_btn.hide()

        control_buttons_layout.addWidget(self.display_toggle_btn)
        control_buttons_layout.addWidget(self.sound_btn)

        chord_control_layout.addWidget(control_buttons_widget)

        # ВАРИАНТЫ АККОРДА
        self.variants_container = QWidget()
        self.variants_container.setStyleSheet("background: transparent; border: none;")
        self.variants_layout = QHBoxLayout(self.variants_container)
        self.variants_layout.setAlignment(Qt.AlignCenter)
        self.variants_layout.setSpacing(8)
        self.variants_container.hide()

        chord_control_layout.addWidget(self.variants_container)
        left_layout.addWidget(chord_control_widget)

        content_layout.addWidget(left_widget, 2)  # Левая часть занимает 2/3

        # ПРАВАЯ ЧАСТЬ - ВЫБОР АККОРДОВ
        right_widget = QFrame()
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_widget.setMaximumWidth(400)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # ПОИСК АККОРДОВ (АНАЛОГИЧНО SONGS_PAGE)
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
        self.search_input.setPlaceholderText("🔍 Введите название аккорда...")
        self.search_input.returnPressed.connect(self.search_chords)

        self.search_button = QPushButton("Найти")
        self.search_button.setCursor(Qt.PointingHandCursor)
        self.search_button.setFixedHeight(40)
        self.search_button.clicked.connect(self.search_chords)

        search_input_layout.addWidget(self.search_input, 3)
        search_input_layout.addWidget(self.search_button, 1)
        search_layout.addWidget(search_input_container)

        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.load_chord_from_search)
        self.results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.results_list.hide()
        search_layout.addWidget(self.results_list)

        right_layout.addWidget(search_frame)

        # ПЕРЕКЛЮЧАТЕЛЬ РЕЖИМА ВЫБОРА
        mode_selector_widget = QWidget()
        mode_selector_widget.setStyleSheet("background: transparent; border: none;")
        mode_selector_layout = QHBoxLayout(mode_selector_widget)
        mode_selector_layout.setAlignment(Qt.AlignCenter)
        mode_selector_layout.setSpacing(8)

        self.style_mode_btn = QPushButton("📊 По типу")
        self.style_mode_btn.setCheckable(True)
        self.style_mode_btn.setChecked(True)
        self.style_mode_btn.setFixedSize(120, 35)

        self.note_mode_btn = QPushButton("🎵 По тональности")
        self.note_mode_btn.setCheckable(True)
        self.note_mode_btn.setFixedSize(140, 35)

        mode_selector_layout.addWidget(self.style_mode_btn)
        mode_selector_layout.addWidget(self.note_mode_btn)

        right_layout.addWidget(mode_selector_widget)

        # ОБЛАСТЬ ВЫБОРА ТИПОВ/ТОНАЛЬНОСТЕЙ
        self.selection_container = QScrollArea()
        self.selection_container.setWidgetResizable(True)
        self.selection_container.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.selection_container.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.selection_container.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
            QWidget {
                background: transparent;
            }
        """)

        self.selection_widget = QWidget()
        self.selection_layout = QGridLayout(self.selection_widget)
        self.selection_layout.setSpacing(8)
        self.selection_layout.setContentsMargins(10, 10, 10, 10)
        self.selection_layout.setAlignment(Qt.AlignTop)

        self.selection_container.setWidget(self.selection_widget)
        right_layout.addWidget(self.selection_container, 1)

        # КНОПКА НАЗАД
        self.back_button = QPushButton("⬅️ Назад")
        self.back_button.setFixedHeight(35)
        self.back_button.hide()
        right_layout.addWidget(self.back_button)

        content_layout.addWidget(right_widget, 1)  # Правая часть занимает 1/3
        main_layout.addLayout(content_layout, 1)

        # Инициализация данных - показываем аккорд A по умолчанию
        self.show_style_selection()
        self.load_default_chord()

    def load_default_chord(self):
        """Загружает аккорд A по умолчанию"""
        self.on_chord_selected("A")

    def apply_styles(self):
        """Применяет стили ко всем элементам страницы"""
        # Стили для кнопок главного меню
        self.songs_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.chords_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.tuner_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.learning_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.theory_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)

        # Стили для переключателя режимов
        button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5D6D7E, stop:1 #34495E);
                border: 2px solid #2C3E50;
                border-radius: 8px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498DB, stop:1 #2980B9);
                border: 2px solid #2471A3;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6C7A89, stop:1 #415B76);
            }
            QPushButton:checked:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5DADE2, stop:1 #3498DB);
            }
        """
        self.style_mode_btn.setStyleSheet(button_style)
        self.note_mode_btn.setStyleSheet(button_style)

        # Стили для кнопки назад
        self.back_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E74C3C, stop:1 #C0392B);
                border: 2px solid #922B21;
                border-radius: 8px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #EC7063, stop:1 #E74C3C);
            }
        """)

        # Стили для кнопок управления
        self.display_toggle_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5D6D7E, stop:1 #34495E);
                border: 1px solid #2C3E50;
                border-radius: 6px;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 8px;
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
                padding: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5DADE2, stop:1 #3498DB);
            }
        """)

        # Стили для поиска
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

    def initialize_page(self):
        """Инициализация страницы"""
        if not self.is_initialized:
            self.setup_ui()
            self.connect_signals()
            self.apply_styles()
            self.is_initialized = True

    def connect_signals(self):
        """Подключение сигналов"""
        self.style_mode_btn.clicked.connect(lambda: self.switch_mode("style"))
        self.note_mode_btn.clicked.connect(lambda: self.switch_mode("note"))
        self.back_button.clicked.connect(self.go_back)
        self.display_toggle_btn.clicked.connect(self.toggle_display_type)
        self.sound_btn.clicked.connect(self.play_chord_sound)

    def switch_mode(self, mode):
        """Переключение между режимами выбора"""
        if mode == "style":
            self.style_mode_btn.setChecked(True)
            self.note_mode_btn.setChecked(False)
            self.current_view = "style"
            self.show_style_selection()
        else:
            self.style_mode_btn.setChecked(False)
            self.note_mode_btn.setChecked(True)
            self.current_view = "note"
            self.show_note_selection()

        # Сбрасываем выбор при переключении режима
        self.selected_type = None
        self.selected_note = None
        self.back_button.hide()
        self.clear_chord_display()

    def show_style_selection(self):
        """Показ выбора по типам аккордов"""
        self.clear_selection_layout()

        row, col = 0, 0
        max_cols = 4  # Максимум 4 кнопки в строке

        for style in CHORDS_TYPE_BY_STYLE:
            btn = QPushButton(style)
            btn.setFixedSize(80, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498DB, stop:1 #2980B9);
                    border: 2px solid #2471A3;
                    border-radius: 8px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5DADE2, stop:1 #3498DB);
                }
            """)
            btn.clicked.connect(lambda checked, s=style: self.on_style_selected(s))

            self.selection_layout.addWidget(btn, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def show_note_selection(self):
        """Показ выбора по тональностям"""
        self.clear_selection_layout()

        row, col = 0, 0
        max_cols = 4  # Максимум 4 кнопки в строке

        for note in CHORDS_TYPE_BY_NOTE:
            btn = QPushButton(note)
            btn.setFixedSize(80, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #27AE60, stop:1 #229954);
                    border: 2px solid #1E8449;
                    border-radius: 8px;
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2ECC71, stop:1 #27AE60);
                }
            """)
            btn.clicked.connect(lambda checked, n=note: self.on_note_selected(n))

            self.selection_layout.addWidget(btn, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def search_chords(self):
        """Поиск аккордов по имени или описанию"""
        try:
            query = self.search_input.text().strip().lower()
            if not query:
                self.results_list.hide()
                return

            results = []
            for chord in self.all_chords:
                # Поиск по имени аккорда
                if query in chord.lower():
                    results.append(chord)
                # Поиск по описанию
                elif chord in CHORDS_DESCRIPTIONS:
                    description = CHORDS_DESCRIPTIONS[chord].lower()
                    if query in description:
                        results.append(chord)

            self.results_list.clear()
            for chord in results:
                self.results_list.addItem(chord)

            if results:
                self.results_list.show()
                self.adjust_results_list_height()
            else:
                self.results_list.hide()

        except Exception as e:
            print(f"Ошибка поиска аккордов: {e}")

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

    def load_chord_from_search(self, item):
        """Загрузка аккорда из результатов поиска"""
        if not item:
            return

        chord_name = item.text()
        self.on_chord_selected(chord_name)
        self.results_list.hide()
        self.search_input.clear()

    def on_style_selected(self, style):
        """Обработчик выбора типа аккорда"""
        self.selected_type = style
        self.selected_note = None
        self.show_chords_for_style(style)
        self.back_button.show()

    def on_note_selected(self, note):
        """Обработчик выбора тональности"""
        self.selected_note = note
        self.selected_type = None
        self.show_chords_for_note(note)
        self.back_button.show()

    def show_chords_for_style(self, style):
        """Показ аккордов для выбранного типа"""
        self.clear_selection_layout()

        if style not in CHORDS_BY_STYLE:
            self.show_error_message(f"Тип '{style}' не найден")
            return

        chords = CHORDS_BY_STYLE[style]

        row, col = 0, 0
        max_cols = 4  # Максимум 4 кнопки в строке

        for chord in chords:
            btn = ChordButton(chord)
            btn.setFixedSize(80, 35)
            btn.clicked.connect(lambda checked, c=chord: self.on_chord_selected(c))

            self.selection_layout.addWidget(btn, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def show_chords_for_note(self, note):
        """Показ аккордов для выбранной тональности"""
        self.clear_selection_layout()

        if note not in CHORDS_BY_NOTE:
            self.show_error_message(f"Тональность '{note}' не найдена")
            return

        chords = CHORDS_BY_NOTE[note]

        row, col = 0, 0
        max_cols = 4  # Максимум 4 кнопки в строке

        for chord in chords:
            btn = ChordButton(chord)
            btn.setFixedSize(80, 35)
            btn.clicked.connect(lambda checked, c=chord: self.on_chord_selected(c))

            self.selection_layout.addWidget(btn, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def on_chord_selected(self, chord_name):
        """Обработчик выбора аккорда"""
        self.current_chord_name = chord_name
        self.current_variant = 1

        print(f"🎯 ChordsPage: Выбран аккорд: {chord_name}")

        # Обновляем информацию об аккорде
        chord_description = self.get_chord_description(chord_name)
        self.chord_name_label.setText(f"Аккорд {chord_name} ({chord_description})")

        # Показываем элементы управления
        self.display_toggle_btn.show()
        self.sound_btn.show()

        # Загружаем и отображаем аккорд
        self.load_chord_variants(chord_name)
        self.refresh_chord_display()

    def get_chord_description(self, chord_name):
        """Получает описание аккорда"""
        return CHORDS_DESCRIPTIONS.get(chord_name, "Гитарный аккорд")

    def load_chord_variants(self, chord_name):
        """Загрузка вариантов аккорда"""
        for i in reversed(range(self.variants_layout.count())):
            widget = self.variants_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not self.config_manager:
            print("❌ ChordsPage: Config manager не установлен")
            return

        variants_count = self.config_manager.get_chord_variants_count(chord_name)
        print(f"🎯 ChordsPage: Для аккорда {chord_name} найдено {variants_count} вариантов")

        if variants_count == 0:
            variants_count = 1

        for variant_num in range(1, variants_count + 1):
            btn = ChordVariantButton(str(variant_num))
            btn.setProperty('variant_num', variant_num)

            def make_handler(v_num):
                def handler():
                    self.current_variant = v_num
                    print(f"🔄 ChordsPage: Переключение на вариант {v_num} для аккорда {chord_name}")
                    self.refresh_chord_display()
                    for i in range(self.variants_layout.count()):
                        other_btn = self.variants_layout.itemAt(i).widget()
                        if other_btn and other_btn.property('variant_num') != v_num:
                            other_btn.setChecked(False)
                            other_btn.update_style()

                return handler

            btn.clicked.connect(make_handler(variant_num))
            self.variants_layout.addWidget(btn)

        if self.variants_layout.count() > 0:
            first_btn = self.variants_layout.itemAt(0).widget()
            if first_btn:
                first_btn.setChecked(True)
                first_btn.update_style()

        self.variants_container.show()

    def refresh_chord_display(self):
        """Обновление отображения аккорда с высоким качеством"""
        if not self.current_chord_name or not self.config_manager:
            return

        try:
            # Генерируем изображение с высоким качеством
            pixmap = self.generate_chord_from_config(self.current_chord_name, self.current_variant)
            if not pixmap.isNull():
                # Принудительно обновляем отображение
                self.chord_image_label.setChordPixmap(pixmap)

                # Принудительное обновление виджета
                self.chord_image_label.update()
                self.chord_image_label.repaint()

                print(
                    f"✅ ChordsPage: Аккорд {self.current_chord_name} вариант {self.current_variant} отображен с высоким качеством")
            else:
                print(f"❌ ChordsPage: Не удалось сгенерировать изображение для {self.current_chord_name}")
                self.show_chord_not_found()
        except Exception as e:
            print(f"❌ ChordsPage: Ошибка обновления отображения аккорда: {e}")
            self.show_chord_not_found()

    def generate_chord_from_config(self, chord_name, variant=1):
        """Генерация изображения аккорда из конфигурации с высоким качеством"""
        if not self.config_manager:
            return QPixmap()

        try:
            variant_key = f"{chord_name}v{variant}" if variant > 1 else chord_name
            chord_config = self.config_manager.get_chord_config(variant_key)

            if not chord_config:
                chord_config = self.config_manager.get_chord_config(chord_name)
                if not chord_config:
                    return QPixmap()

            # Получаем элементы для текущего типа отображения
            if self.current_display_type == "fingers":
                elements = chord_config.get('elements_fingers', [])
                print(f"👆 Используем элементы пальцев: {len(elements)}")
            else:
                elements = chord_config.get('elements_notes', [])
                print(f"🎵 Используем элементы нот: {len(elements)}")

            if not elements:
                return QPixmap()

            # Применяем обводку
            elements = self.apply_outline_settings(elements)

            # Загружаем базовое изображение
            base_image_path = self.config_manager.get_base_image_path()
            if not base_image_path or not os.path.exists(base_image_path):
                return QPixmap()

            original_pixmap = QPixmap(base_image_path)
            if original_pixmap.isNull():
                return QPixmap()

            # Получаем область обрезки
            crop_rect = chord_config.get('crop_rect')
            if not crop_rect:
                return QPixmap()

            crop_x, crop_y, crop_width, crop_height = crop_rect

            # Проверяем границы
            crop_x = max(0, min(crop_x, original_pixmap.width() - 1))
            crop_y = max(0, min(crop_y, original_pixmap.height() - 1))
            crop_width = max(1, min(crop_width, original_pixmap.width() - crop_x))
            crop_height = max(1, min(crop_height, original_pixmap.height() - crop_y))

            print(f"🎯 Оригинальное изображение: {original_pixmap.width()}x{original_pixmap.height()}")
            print(f"🎯 Область обрезки: ({crop_x}, {crop_y}, {crop_width}, {crop_height})")

            # Создаем новое изображение размером с область обрезки
            result_pixmap = QPixmap(crop_width, crop_height)
            result_pixmap.fill(Qt.transparent)

            painter = QPainter(result_pixmap)

            # ВЫСОКОЕ КАЧЕСТВО РЕНДЕРИНГА
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            painter.setRenderHint(QPainter.TextAntialiasing, True)

            # Копируем область из оригинального изображения
            painter.drawPixmap(0, 0, original_pixmap, crop_x, crop_y, crop_width, crop_height)

            # Рисуем элементы
            self.draw_elements_on_canvas(painter, elements, (crop_x, crop_y, crop_width, crop_height))
            painter.end()

            # МАСШТАБИРОВАНИЕ
            display_width = int(crop_width * 0.5)  # 50% масштаб
            display_height = int(crop_height * 0.5)  # 50% масштаб

            print(f"📏 Масштаб (50%): {crop_width}x{crop_height} -> {display_width}x{display_height}")

            scaled_pixmap = result_pixmap.scaled(
                display_width,
                display_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            print(f"✅ Изображение установлено: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
            return scaled_pixmap

        except Exception as e:
            print(f"❌ ChordsPage: Ошибка генерации изображения для {chord_name} вариант {variant}: {e}")
            import traceback
            traceback.print_exc()
            return QPixmap()

    def apply_outline_settings(self, elements):
        """ИСПРАВЛЕННОЕ применение настроек обводки - идентичное songs_page"""
        modified_elements = []
        for element in elements:
            if not isinstance(element, dict):
                continue

            element_type = element.get('type')
            element_data = element.get('data', {}).copy()

            if element_type == 'barre':
                element_data['style'] = 'orange_gradient'
                element_data['outline_width'] = 2
                element_data['outline_color'] = [0, 0, 0]

            elif element_type == 'note':
                element_data['style'] = 'red_3d'
                element_data['outline_width'] = 2
                element_data['outline_color'] = [0, 0, 0]
                element_data['text_color'] = [255, 255, 255]

                if 'finger' not in element_data:
                    if 'note_name' in element_data:
                        element_data['finger'] = element_data['note_name']
                    else:
                        element_data['finger'] = '1'

                element_data['display_text'] = 'finger'

            elif element_type == 'fret':
                element_data['color'] = [0, 0, 0]
                element_data['style'] = 'default'

            modified_elements.append({
                'type': element_type,
                'data': element_data
            })

        return modified_elements

    def draw_elements_on_canvas(self, painter, elements, crop_rect):
        """ИСПРАВЛЕННОЕ рисование элементов на canvas"""
        try:
            if not DrawingElements:
                print("❌ ChordsPage: DrawingElements не доступен")
                return

            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            painter.setRenderHint(QPainter.TextAntialiasing, True)

            for element in elements:
                try:
                    element_type = element.get('type')
                    element_data = element.get('data', {})

                    if element_type == 'fret':
                        DrawingElements.draw_fret(painter, element_data)
                    elif element_type == 'note':
                        DrawingElements.draw_note(painter, element_data)
                    elif element_type == 'barre':
                        DrawingElements.draw_barre(painter, element_data)

                except Exception as e:
                    print(f"❌ ChordsPage: Ошибка рисования элемента {element_type}: {e}")

        except Exception as e:
            print(f"❌ ChordsPage: Ошибка рисования элементов: {e}")

    def adapt_coordinates(self, element_data, crop_rect):
        """ИСПРАВЛЕННАЯ адаптация координат элементов - идентичная songs_page"""
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

        # ОСОБАЯ КОРРЕКЦИЯ ТОЛЬКО ДЛЯ БАРЕ
        if adapted_data.get('type') == 'barre':
            barre_width = adapted_data.get('width', 100)
            barre_height = adapted_data.get('height', 20)

            # Для баре - координаты указывают на центр, нужно сместить в левый верхний угол
            if 'x' in adapted_data:
                adapted_data['x'] = adapted_data['x'] - (barre_width // 2)
            if 'y' in adapted_data:
                adapted_data['y'] = adapted_data['y'] - (barre_height // 2)

        return adapted_data

    def show_chord_not_found(self):
        """Показ сообщения об отсутствии аккорда"""
        self.chord_image_label.clear()
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.red, 4))
        painter.drawLine(10, 10, 90, 90)
        painter.drawLine(90, 10, 10, 90)
        painter.end()
        self.chord_image_label.setChordPixmap(pixmap)

    def toggle_display_type(self):
        """Переключение между нотами и пальцами"""
        if self.display_toggle_btn.isChecked():
            self.current_display_type = "notes"
            self.display_toggle_btn.setText("👆 Пальцы")
        else:
            self.current_display_type = "fingers"
            self.display_toggle_btn.setText("🎵 Ноты")
        self.refresh_chord_display()

    def play_chord_sound(self):
        """Воспроизведение звука аккорда"""
        if not self.current_chord_name or not self.sound_player:
            return

        try:
            success = self.sound_player.play_chord_sound(self.current_chord_name, str(self.current_variant))
            if not success:
                success = self.sound_player.play_chord_sound(self.current_chord_name)
            if not success:
                print(f"❌ ChordsPage: Не удалось найти звуковой файл для аккорда {self.current_chord_name}")
        except Exception as e:
            print(f"❌ ChordsPage: Ошибка при воспроизведении звука: {e}")

    def show_chord_large(self):
        """Показ увеличенного окна с аккордом"""
        if not self.current_chord_name:
            return

        try:
            from gui.windows.chord_viewer import ChordViewerWindow
            pixmap = self.generate_chord_from_config(self.current_chord_name, self.current_variant)
            if not pixmap.isNull():
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                temp_path = temp_file.name
                pixmap.save(temp_path, 'PNG')
                temp_file.close()
                sound_path = self.get_chord_sound_path(self.current_chord_name, self.current_variant)
                viewer = ChordViewerWindow(self.current_chord_name, temp_path, sound_path or "", self)
                viewer.exec_()
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except Exception as e:
                    print(f"⚠️ ChordsPage: Ошибка удаления временного файла: {e}")
        except Exception as e:
            print(f"❌ ChordsPage: Ошибка при открытии окна просмотра аккорда: {e}")

    def get_chord_sound_path(self, chord_name, variant):
        """Получение пути к звуковому файлу аккорда"""
        try:
            sounds_dir = os.path.join("source", "sounds")
            sound_file = os.path.join(sounds_dir, f"{chord_name}/{chord_name}_{variant}.mp3")
            if os.path.exists(sound_file):
                return sound_file
            sound_file = os.path.join(sounds_dir, f"{chord_name}/{chord_name}.mp3")
            if os.path.exists(sound_file):
                return sound_file
            sound_file = os.path.join(sounds_dir, f"{chord_name}.mp3")
            if os.path.exists(sound_file):
                return sound_file
            return None
        except Exception as e:
            print(f"❌ ChordsPage: Ошибка получения пути к звуковому файлу: {e}")
            return None

    def go_back(self):
        """Возврат к предыдущему уровню навигации"""
        if self.selected_type or self.selected_note:
            self.selected_type = None
            self.selected_note = None
            self.back_button.hide()
            self.clear_chord_display()
            if self.current_view == "style":
                self.show_style_selection()
            else:
                self.show_note_selection()

    def clear_selection_layout(self):
        """Очистка layout выбора"""
        for i in reversed(range(self.selection_layout.count())):
            widget = self.selection_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def clear_chord_display(self):
        """Очистка отображения аккорда"""
        self.chord_name_label.setText("Выберите аккорд")
        self.chord_image_label.clear()
        self.display_toggle_btn.hide()
        self.sound_btn.hide()
        self.variants_container.hide()
        for i in reversed(range(self.variants_layout.count())):
            widget = self.variants_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def show_error_message(self, message):
        """Показ сообщения об ошибке"""
        error_label = QLabel(message)
        error_label.setStyleSheet("""
            QLabel {
                color: #E74C3C;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
                padding: 20px;
                background: rgba(231, 76, 60, 0.1);
                border: 1px solid rgba(231, 76, 60, 0.3);
                border-radius: 10px;
            }
        """)
        error_label.setAlignment(Qt.AlignCenter)
        self.selection_layout.addWidget(error_label)

    def on_page_show(self):
        """Вызывается при показе страницы"""
        print("🎸 ChordsPage: Страница аккордов показана")

    def on_page_hide(self):
        """Вызывается при скрытии страницы"""
        print("🎸 ChordsPage: Страница аккордов скрыта")

    def cleanup(self):
        """Очистка ресурсов"""
        self.clear_chord_display()
        self.clear_selection_layout()