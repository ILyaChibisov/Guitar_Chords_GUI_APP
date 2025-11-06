# gui/pages/chords_page.py
import os
import tempfile
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFrame, QScrollArea, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen

from .base_page import BasePage
from gui.widgets.buttons import MenuButton, ChordButton, ChordVariantButton
from gui.widgets.labels import AdaptiveChordLabel
from config.styles import DarkTheme

# Импортируем данные аккордов из const
try:
    from const import CHORDS_TYPE_LIST, CHORDS_TYPE_NAME_LIST_DSR, CHORDS_TYPE

    # Создаем словарь для быстрого доступа к аккордам по типам
    CHORDS_BY_TYPE = {}
    if (isinstance(CHORDS_TYPE_NAME_LIST_DSR, list) and
            isinstance(CHORDS_TYPE_LIST, list) and
            len(CHORDS_TYPE_NAME_LIST_DSR) == len(CHORDS_TYPE_LIST)):

        for i, (chord_type, chords_list) in enumerate(zip(CHORDS_TYPE_NAME_LIST_DSR, CHORDS_TYPE_LIST)):
            # Используем индекс как ключ, если тип - список
            if isinstance(chord_type, list):
                key = f"Type_{i}"
            else:
                key = str(chord_type)
            CHORDS_BY_TYPE[key] = chords_list

    # Создаем общий словарь аккордов и их описаний
    CHORDS_DATA = {}
    if (isinstance(CHORDS_TYPE_LIST, list) and
            isinstance(CHORDS_TYPE_NAME_LIST_DSR, list)):

        for chords_list, desc_list in zip(CHORDS_TYPE_LIST, CHORDS_TYPE_NAME_LIST_DSR):
            if isinstance(chords_list, list) and isinstance(desc_list, list):
                for chord, description in zip(chords_list, desc_list):
                    if isinstance(chord, str) and isinstance(description, str):
                        CHORDS_DATA[chord] = description

    print(f"✅ ChordsPage: Загружено {len(CHORDS_BY_TYPE)} типов аккордов")
    print(f"✅ ChordsPage: Загружено {len(CHORDS_DATA)} аккордов с описаниями")

except ImportError as e:
    print(f"⚠️ ChordsPage: Не удалось загрузить данные аккордов из const: {e}")
    CHORDS_BY_TYPE = {}
    CHORDS_DATA = {}

# Заглушка для CHORDS_TYPE если не загрузился
try:
    from const import CHORDS_TYPE

    if not isinstance(CHORDS_TYPE, list):
        CHORDS_TYPE = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
except ImportError:
    CHORDS_TYPE = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

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
        self.current_view = "type"  # "type" или "note"
        self.selected_type = None
        self.selected_note = None
        self.current_chord_name = ""
        self.current_variant = 1

        # Настройки отображения аккордов
        self.current_display_type = "fingers"

        # Менеджер конфигураций (будет передан из main)
        self.config_manager = None
        self.sound_player = None

        self.initialize_page()

    def set_config_manager(self, config_manager):
        """Установка менеджера конфигураций из главного приложения"""
        self.config_manager = config_manager
        print("✅ ChordsPage: Config manager установлен")

    def set_sound_player(self, sound_player):
        """Установка проигрывателя звуков из главного приложения"""
        self.sound_player = sound_player
        print("✅ ChordsPage: Sound player установлен")

    def setup_ui(self):
        """Настройка UI страницы аккордов"""
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

        # ЗАГОЛОВОК СТРАНИЦЫ
        self.page_title = QLabel("🎸 БИБЛИОТЕКА АККОРДОВ")
        self.page_title.setStyleSheet(DarkTheme.SONG_TITLE_STYLE)
        self.page_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.page_title)

        # ОСНОВНОЙ КОНТЕНТ
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # ЛЕВАЯ ЧАСТЬ - ВЫБОР АККОРДОВ
        left_widget = QFrame()
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # ПЕРЕКЛЮЧАТЕЛЬ РЕЖИМА ВЫБОРА
        mode_selector_widget = QWidget()
        mode_selector_widget.setStyleSheet("background: transparent; border: none;")
        mode_selector_layout = QHBoxLayout(mode_selector_widget)
        mode_selector_layout.setAlignment(Qt.AlignCenter)
        mode_selector_layout.setSpacing(10)

        self.type_mode_btn = QPushButton("📊 По типам")
        self.type_mode_btn.setCheckable(True)
        self.type_mode_btn.setChecked(True)
        self.type_mode_btn.setFixedSize(120, 35)

        self.note_mode_btn = QPushButton("🎵 По нотам")
        self.note_mode_btn.setCheckable(True)
        self.note_mode_btn.setFixedSize(120, 35)

        mode_selector_layout.addWidget(self.type_mode_btn)
        mode_selector_layout.addWidget(self.note_mode_btn)

        left_layout.addWidget(mode_selector_widget)

        # ОБЛАСТЬ ВЫБОРА ТИПОВ/НОТ
        self.selection_container = QScrollArea()
        self.selection_container.setWidgetResizable(True)
        self.selection_container.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.selection_container.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.selection_container.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
            QWidget {
                background: transparent;
            }
        """)

        self.selection_widget = QWidget()
        self.selection_layout = QGridLayout(self.selection_widget)
        self.selection_layout.setSpacing(10)
        self.selection_layout.setContentsMargins(15, 15, 15, 15)
        self.selection_layout.setAlignment(Qt.AlignTop)

        self.selection_container.setWidget(self.selection_widget)
        left_layout.addWidget(self.selection_container, 1)

        # КНОПКА НАЗАД
        self.back_button = QPushButton("⬅️ Назад")
        self.back_button.setFixedHeight(40)
        self.back_button.hide()
        left_layout.addWidget(self.back_button)

        content_layout.addWidget(left_widget, 2)

        # ПРАВАЯ ЧАСТЬ - ОТОБРАЖЕНИЕ АККОРДА
        right_widget = QFrame()
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        # ИНФОРМАЦИЯ О ВЫБРАННОМ АККОРДЕ
        chord_info_widget = QWidget()
        chord_info_widget.setStyleSheet("background: transparent; border: none;")
        chord_info_layout = QVBoxLayout(chord_info_widget)
        chord_info_layout.setSpacing(0)
        chord_info_layout.setContentsMargins(0, 0, 0, 0)

        self.chord_name_label = QLabel("Выберите аккорд")
        self.chord_name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                text-align: center;
                padding: 10px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        self.chord_name_label.setAlignment(Qt.AlignCenter)
        chord_info_layout.addWidget(self.chord_name_label)

        right_layout.addWidget(chord_info_widget)

        # ИЗОБРАЖЕНИЕ АККОРДА
        self.chord_image_label = AdaptiveChordLabel()
        self.chord_image_label.clicked.connect(self.show_chord_large)
        self.chord_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chord_image_label.setStyleSheet("""
            AdaptiveChordLabel {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
        """)
        right_layout.addWidget(self.chord_image_label, 1)

        # ПАНЕЛЬ УПРАВЛЕНИЯ ОТОБРАЖЕНИЕМ
        control_widget = QWidget()
        control_widget.setStyleSheet("background: transparent; border: none;")
        control_layout = QHBoxLayout(control_widget)
        control_layout.setAlignment(Qt.AlignCenter)
        control_layout.setSpacing(10)

        # Кнопка переключения ноты/пальцы
        self.display_toggle_btn = QPushButton("🎵 Ноты")
        self.display_toggle_btn.setCheckable(True)
        self.display_toggle_btn.setChecked(False)
        self.display_toggle_btn.setFixedSize(100, 30)
        self.display_toggle_btn.hide()

        # Кнопка звука
        self.sound_btn = QPushButton("🔊 Слушать")
        self.sound_btn.setFixedSize(100, 30)
        self.sound_btn.hide()

        control_layout.addWidget(self.display_toggle_btn)
        control_layout.addWidget(self.sound_btn)

        right_layout.addWidget(control_widget)

        # ВАРИАНТЫ АККОРДА
        self.variants_container = QWidget()
        self.variants_container.setStyleSheet("background: transparent; border: none;")
        self.variants_layout = QHBoxLayout(self.variants_container)
        self.variants_layout.setAlignment(Qt.AlignCenter)
        self.variants_layout.setSpacing(8)
        self.variants_container.hide()

        right_layout.addWidget(self.variants_container)

        content_layout.addWidget(right_widget, 1)
        main_layout.addLayout(content_layout, 1)

        # Инициализация данных
        self.show_type_selection()

    def apply_styles(self):
        """Применяет стили ко всем элементам страницы"""
        # Стили для кнопок главного меню
        self.songs_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.chords_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.tuner_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.learning_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.theory_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)

        # Стили для переключателя режимов
        self.type_mode_btn.setStyleSheet("""
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
        """)

        self.note_mode_btn.setStyleSheet(self.type_mode_btn.styleSheet())

        # Стили для кнопки назад
        self.back_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E74C3C, stop:1 #C0392B);
                border: 2px solid #922B21;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #EC7063, stop:1 #E74C3C);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #CB4335, stop:1 #A93226);
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
                padding: 2px 4px;
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
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5DADE2, stop:1 #3498DB);
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
        self.type_mode_btn.clicked.connect(lambda: self.switch_mode("type"))
        self.note_mode_btn.clicked.connect(lambda: self.switch_mode("note"))
        self.back_button.clicked.connect(self.go_back)
        self.display_toggle_btn.clicked.connect(self.toggle_display_type)
        self.sound_btn.clicked.connect(self.play_chord_sound)

    def switch_mode(self, mode):
        """Переключение между режимами выбора"""
        if mode == "type":
            self.type_mode_btn.setChecked(True)
            self.note_mode_btn.setChecked(False)
            self.current_view = "type"
            self.show_type_selection()
        else:
            self.type_mode_btn.setChecked(False)
            self.note_mode_btn.setChecked(True)
            self.current_view = "note"
            self.show_note_selection()

        # Сбрасываем выбор при переключении режима
        self.selected_type = None
        self.selected_note = None
        self.back_button.hide()
        self.clear_chord_display()

    def show_type_selection(self):
        """Показ выбора по типам аккордов"""
        self.clear_selection_layout()

        if not CHORDS_BY_TYPE:
            self.show_error_message("Данные аккордов не загружены")
            return

        row, col = 0, 0
        max_cols = 6

        for chord_type in CHORDS_BY_TYPE.keys():
            btn = QPushButton(str(chord_type))
            btn.setFixedSize(120, 50)
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
            btn.clicked.connect(lambda checked, ct=chord_type: self.on_type_selected(ct))

            self.selection_layout.addWidget(btn, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def show_note_selection(self):
        """Показ выбора по нотам"""
        self.clear_selection_layout()

        row, col = 0, 0
        max_cols = 6

        for note in CHORDS_TYPE:
            btn = QPushButton(str(note))
            btn.setFixedSize(80, 45)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #27AE60, stop:1 #229954);
                    border: 2px solid #1E8449;
                    border-radius: 8px;
                    color: white;
                    font-size: 14px;
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

    def on_type_selected(self, chord_type):
        """Обработчик выбора типа аккорда"""
        self.selected_type = chord_type
        self.selected_note = None
        self.show_chords_for_type(chord_type)
        self.back_button.show()

    def on_note_selected(self, note):
        """Обработчик выбора ноты"""
        self.selected_note = note
        self.selected_type = None
        self.show_chords_for_note(note)
        self.back_button.show()

    def show_chords_for_type(self, chord_type):
        """Показ аккордов для выбранного типа"""
        self.clear_selection_layout()

        if chord_type not in CHORDS_BY_TYPE:
            self.show_error_message(f"Тип '{chord_type}' не найден")
            return

        chords = CHORDS_BY_TYPE[chord_type]

        if not isinstance(chords, list):
            self.show_error_message(f"Некорректные данные для типа '{chord_type}'")
            return

        row, col = 0, 0
        max_cols = 6

        for chord in chords:
            if not isinstance(chord, str):
                continue

            btn = ChordButton(chord)
            btn.setFixedSize(90, 40)
            btn.clicked.connect(lambda checked, c=chord: self.on_chord_selected(c))

            self.selection_layout.addWidget(btn, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def show_chords_for_note(self, note):
        """Показ аккордов для выбранной ноты"""
        self.clear_selection_layout()

        # Ищем аккорды, начинающиеся с выбранной ноты
        chords_for_note = []
        for chords_list in CHORDS_BY_TYPE.values():
            if not isinstance(chords_list, list):
                continue

            for chord in chords_list:
                if isinstance(chord, str) and chord.startswith(str(note)):
                    chords_for_note.append(chord)

        # Убираем дубликаты
        chords_for_note = list(set(chords_for_note))
        chords_for_note.sort()

        if not chords_for_note:
            self.show_error_message(f"Аккорды для ноты '{note}' не найдены")
            return

        row, col = 0, 0
        max_cols = 6

        for chord in chords_for_note:
            btn = ChordButton(chord)
            btn.setFixedSize(90, 40)
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
        self.chord_name_label.setText(f"{chord_name} - {chord_description}")

        # Показываем элементы управления
        self.display_toggle_btn.show()
        self.sound_btn.show()

        # Загружаем и отображаем аккорд
        self.load_chord_variants(chord_name)
        self.refresh_chord_display()

    def get_chord_description(self, chord_name):
        """Получает описание аккорда"""
        if not isinstance(chord_name, str):
            return "Гитарный аккорд"

        names_to_try = [
            chord_name,
            chord_name.upper(),
            chord_name.upper().replace('M', 'm'),
            chord_name.upper().replace('М', 'm'),
        ]

        for name in names_to_try:
            if name in CHORDS_DATA:
                return CHORDS_DATA[name]

        return "Гитарный аккорд"

    def load_chord_variants(self, chord_name):
        """Загрузка вариантов аккорда"""
        # Очищаем предыдущие варианты
        for i in reversed(range(self.variants_layout.count())):
            widget = self.variants_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not self.config_manager:
            print("❌ ChordsPage: Config manager не установлен")
            return

        # Получаем количество вариантов
        variants_count = self.config_manager.get_chord_variants_count(chord_name)
        print(f"🎯 ChordsPage: Для аккорда {chord_name} найдено {variants_count} вариантов")

        if variants_count == 0:
            variants_count = 1  # Минимум один вариант

        # Создаем кнопки вариантов
        for variant_num in range(1, variants_count + 1):
            btn = ChordVariantButton(str(variant_num))
            btn.setProperty('variant_num', variant_num)

            def make_handler(v_num):
                def handler():
                    self.current_variant = v_num
                    print(f"🔄 ChordsPage: Переключение на вариант {v_num} для аккорда {chord_name}")
                    self.refresh_chord_display()
                    # Снимаем выделение с других кнопок
                    for i in range(self.variants_layout.count()):
                        other_btn = self.variants_layout.itemAt(i).widget()
                        if other_btn and other_btn.property('variant_num') != v_num:
                            other_btn.setChecked(False)
                            other_btn.update_style()

                return handler

            btn.clicked.connect(make_handler(variant_num))
            self.variants_layout.addWidget(btn)

        # Активируем первый вариант
        if self.variants_layout.count() > 0:
            first_btn = self.variants_layout.itemAt(0).widget()
            if first_btn:
                first_btn.setChecked(True)
                first_btn.update_style()

        self.variants_container.show()

    def refresh_chord_display(self):
        """Обновление отображения аккорда"""
        if not self.current_chord_name or not self.config_manager:
            return

        try:
            pixmap = self.generate_chord_from_config(self.current_chord_name, self.current_variant)
            if not pixmap.isNull():
                self.chord_image_label.setChordPixmap(pixmap)
                print(f"✅ ChordsPage: Аккорд {self.current_chord_name} вариант {self.current_variant} отображен")
            else:
                print(f"❌ ChordsPage: Не удалось сгенерировать изображение для {self.current_chord_name}")
                self.show_chord_not_found()
        except Exception as e:
            print(f"❌ ChordsPage: Ошибка обновления отображения аккорда: {e}")
            self.show_chord_not_found()

    def generate_chord_from_config(self, chord_name, variant=1):
        """Генерация изображения аккорда из конфигурации"""
        if not self.config_manager:
            return QPixmap()

        try:
            variant_key = f"{chord_name}v{variant}" if variant > 1 else chord_name
            chord_config = self.config_manager.get_chord_config(variant_key)

            if not chord_config:
                print(f"❌ ChordsPage: Конфигурация не найдена для: {variant_key}")
                # Пробуем найти базовый аккорд без варианта
                chord_config = self.config_manager.get_chord_config(chord_name)
                if not chord_config:
                    return QPixmap()

            # Получаем элементы для текущего типа отображения
            if self.current_display_type == "fingers":
                elements = chord_config.get('elements_fingers', [])
            else:
                elements = chord_config.get('elements_notes', [])

            if not elements:
                print(f"❌ ChordsPage: Нет элементов для аккорда {variant_key}")
                return QPixmap()

            # Применяем обводку
            elements = self.apply_outline_settings(elements)

            # Загружаем базовое изображение
            base_image_path = self.config_manager.get_base_image_path()
            if not base_image_path or not os.path.exists(base_image_path):
                print(f"❌ ChordsPage: Базовое изображение не найдено: {base_image_path}")
                return QPixmap()

            original_pixmap = QPixmap(base_image_path)
            if original_pixmap.isNull():
                print(f"❌ ChordsPage: Не удалось загрузить базовое изображение")
                return QPixmap()

            # Получаем область обрезки
            crop_rect = chord_config.get('crop_rect')
            if not crop_rect:
                print(f"❌ ChordsPage: Нет области обрезки для аккорда {variant_key}")
                return QPixmap()

            crop_x, crop_y, crop_width, crop_height = crop_rect

            # Проверяем границы
            crop_x = max(0, min(crop_x, original_pixmap.width() - 1))
            crop_y = max(0, min(crop_y, original_pixmap.height() - 1))
            crop_width = max(1, min(crop_width, original_pixmap.width() - crop_x))
            crop_height = max(1, min(crop_height, original_pixmap.height() - crop_y))

            # Создаем новое изображение
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

            # Масштабируем
            display_width = min(400, crop_width)
            scale_factor = display_width / crop_width
            display_height = int(crop_height * scale_factor)

            scaled_pixmap = result_pixmap.scaled(
                display_width, display_height,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            return scaled_pixmap

        except Exception as e:
            print(f"❌ ChordsPage: Ошибка генерации изображения для {chord_name} вариант {variant}: {e}")
            return QPixmap()

    def apply_outline_settings(self, elements):
        """Применение настроек обводки к элементам"""
        modified_elements = []
        for element in elements:
            if element['type'] == 'barre':
                modified_element = element.copy()
                modified_element['data'] = element['data'].copy()
                modified_element['data']['outline_width'] = 4
                modified_element['data']['outline_color'] = [0, 0, 0]
                modified_elements.append(modified_element)
            elif element['type'] == 'note':
                modified_element = element.copy()
                modified_element['data'] = element['data'].copy()
                modified_element['data']['outline_width'] = 6
                modified_element['data']['outline_color'] = [0, 0, 0]
                modified_elements.append(modified_element)
            else:
                modified_elements.append(element)

        return modified_elements

    def draw_elements_on_canvas(self, painter, elements, crop_rect):
        """Рисование элементов на canvas"""
        if not DrawingElements:
            print("❌ ChordsPage: DrawingElements не доступен")
            return

        for element in elements:
            try:
                if element['type'] == 'fret':
                    self.draw_fret_on_canvas(painter, element['data'], crop_rect)
                elif element['type'] == 'note':
                    self.draw_note_on_canvas(painter, element['data'], crop_rect)
                elif element['type'] == 'barre':
                    self.draw_barre_on_canvas(painter, element['data'], crop_rect)
            except Exception as e:
                print(f"❌ ChordsPage: Ошибка рисования элемента {element['type']}: {e}")

    def draw_fret_on_canvas(self, painter, fret_data, crop_rect):
        """Рисование лада на canvas"""
        try:
            adapted_data = self.adapt_coordinates(fret_data, crop_rect)
            DrawingElements.draw_fret(painter, adapted_data)
        except Exception as e:
            print(f"❌ ChordsPage: Ошибка рисования лада: {e}")

    def draw_note_on_canvas(self, painter, note_data, crop_rect):
        """Рисование ноты на canvas"""
        try:
            adapted_data = self.adapt_coordinates(note_data, crop_rect)
            DrawingElements.draw_note(painter, adapted_data)
        except Exception as e:
            print(f"❌ ChordsPage: Ошибка рисования ноты: {e}")

    def draw_barre_on_canvas(self, painter, barre_data, crop_rect):
        """Рисование баре на canvas"""
        try:
            adapted_data = self.adapt_coordinates(barre_data, crop_rect)
            DrawingElements.draw_barre(painter, adapted_data)
        except Exception as e:
            print(f"❌ ChordsPage: Ошибка рисования баре: {e}")

    def adapt_coordinates(self, element_data, crop_rect):
        """Адаптация координат элементов"""
        if not crop_rect:
            return element_data.copy()

        adapted_data = element_data.copy()
        crop_x, crop_y, crop_width, crop_height = crop_rect

        original_x = element_data.get('x', 0)
        original_y = element_data.get('y', 0)

        if 'x' in adapted_data:
            adapted_data['x'] = original_x - crop_x
        if 'y' in adapted_data:
            adapted_data['y'] = original_y - crop_y

        adapted_data['x'] = int(round(adapted_data.get('x', 0)))
        adapted_data['y'] = int(round(adapted_data.get('y', 0)))

        if adapted_data.get('type') == 'barre':
            barre_width = adapted_data.get('width', 100)
            barre_height = adapted_data.get('height', 20)
            if 'x' in adapted_data:
                adapted_data['x'] = adapted_data['x'] - (barre_width // 2)
            if 'y' in adapted_data:
                adapted_data['y'] = adapted_data['y'] - (barre_height // 2)

        return adapted_data

    def show_chord_not_found(self):
        """Показ сообщения об отсутствии аккорда"""
        self.chord_image_label.clear()

        # Создаем красный крестик
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
            print(
                f"🔊 ChordsPage: Попытка воспроизведения звука для аккорда: {self.current_chord_name}, вариант: {self.current_variant}")
            success = self.sound_player.play_chord_sound(self.current_chord_name, str(self.current_variant))

            if not success:
                # Если не нашли с вариантом, пробуем без варианта
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

                viewer = ChordViewerWindow(
                    self.current_chord_name,
                    temp_path,
                    sound_path or "",
                    self
                )
                viewer.exec_()

                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except Exception as e:
                    print(f"⚠️ ChordsPage: Ошибка удаления временного файла: {e}")

        except Exception as e:
            print(f"❌ ChordsPage: Ошибка при открытии окна просмотра аккорда: {e}")
            import traceback
            traceback.print_exc()

    def get_chord_sound_path(self, chord_name, variant):
        """Получение пути к звуковому файлу аккорда"""
        try:
            sounds_dir = os.path.join("source", "sounds")

            # Пробуем с вариантом
            sound_file = os.path.join(sounds_dir, f"{chord_name}/{chord_name}_{variant}.mp3")
            if os.path.exists(sound_file):
                return sound_file

            # Пробуем без варианта
            sound_file = os.path.join(sounds_dir, f"{chord_name}/{chord_name}.mp3")
            if os.path.exists(sound_file):
                return sound_file

            # Пробуем в корне папки с аккордом
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
            # Возврат к выбору типа/ноты
            self.selected_type = None
            self.selected_note = None
            self.back_button.hide()
            self.clear_chord_display()

            if self.current_view == "type":
                self.show_type_selection()
            else:
                self.show_note_selection()
        else:
            # Возврат к главному меню
            self.switch_mode(self.current_view)

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

        # Очищаем варианты
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