import os
import re
import html
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QListWidget, QTextBrowser, QLabel,
                             QFrame, QScrollArea, QSizePolicy)
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from .base_page import BasePage
from gui.widgets.buttons import ModernButton, MenuButton, ChordButton, SoundButtonLarge, ChordVariantButton
from gui.widgets.labels import AdaptiveChordLabel
from gui.widgets.media import ScrollChordButtonsWidget
from database.queries import SongQueries
from database.chord_repository import ChordRepository
import database.db_scripts as db
from config.styles import DarkTheme

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


class SongsPage(BasePage):
    """Страница песен и аккордов с адаптивным отображением"""

    def __init__(self, parent=None):
        super().__init__("songs", parent)

        # Переменные для пагинации аккордов
        self.current_chord_index = 0
        self.chords_list = []
        self.current_chord_folder = ""
        self.last_variant_mp3_path = ""
        self.current_chord_name = ""
        self.current_song_title = ""
        self.current_chord_variants = []

        # Репозиторий для работы с встроенными аккордами
        self.chord_repository = ChordRepository()

        self.player = QMediaPlayer()
        self.player.error.connect(self.handle_error)

        self.initialize_page()

    def get_chord_description(self, chord_name):
        """Получает описание аккорда из данных const"""
        # Пробуем разные варианты написания
        names_to_try = [
            chord_name,
            chord_name.upper(),
            chord_name.upper().replace('M', 'm'),
            chord_name.upper().replace('М', 'm'),
        ]

        for name in names_to_try:
            if name in CHORDS_DATA:
                return CHORDS_DATA[name]

        # Если не нашли, возвращаем описание по умолчанию
        return f"Гитарный аккорд {chord_name}"

    def setup_ui(self):
        """Настройка UI с адаптивным отображением аккордов"""
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

        # ОСНОВНОЙ КОНТЕНТ - ГОРИЗОНТАЛЬНОЕ РАСПОЛОЖЕНИЕ
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # ЛЕВАЯ ЧАСТЬ: название песни и текст (60% ширины)
        left_widget = QFrame()
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # ЗАГОЛОВОК ПЕСНИ - ПРОСТО ТЕКСТ БЕЗ РАМКИ
        self.song_title_label = QLabel("🎵 Текст песни с аккордами")
        self.song_title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 5px 0px;
                text-align: center;
                background: transparent;
                border: none;
            }
        """)
        self.song_title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.song_title_label)

        # ТЕКСТ ПЕСНИ - ТАКОЙ ЖЕ ФОН КАК У РЕЗУЛЬТАТОВ ПОИСКА
        self.song_text = QTextBrowser()
        self.song_text.setReadOnly(True)
        self.song_text.setOpenLinks(False)
        self.song_text.anchorClicked.connect(self.chord_clicked)
        self.song_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.song_text.setWordWrapMode(True)
        left_layout.addWidget(self.song_text, 1)

        # Контейнер для кнопок аккордов песни - ПРОЗРАЧНЫЙ ФОН
        chords_container = QWidget()
        chords_container.setStyleSheet("background: transparent; border: none;")
        chords_layout = QHBoxLayout(chords_container)
        chords_layout.setContentsMargins(0, 0, 0, 0)
        chords_layout.setSpacing(5)

        # Кнопка прокрутки влево
        self.scroll_left_btn = QPushButton("◀")
        self.scroll_left_btn.setFixedSize(30, 40)
        self.scroll_left_btn.setCursor(Qt.PointingHandCursor)
        self.scroll_left_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5a6fd8, stop: 1 #6a4190);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4c5bc6, stop: 1 #58357e);
            }
            QPushButton:disabled {
                background: #34495e;
                color: #7f8c8d;
            }
        """)
        self.scroll_left_btn.clicked.connect(self.scroll_chords_left)
        self.scroll_left_btn.hide()
        chords_layout.addWidget(self.scroll_left_btn)

        # Область с кнопками аккордов - ПРОЗРАЧНЫЙ ФОН
        self.scroll_chords_widget = ScrollChordButtonsWidget()
        self.scroll_chords_widget.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QWidget {
                background: transparent;
            }
        """)
        chords_layout.addWidget(self.scroll_chords_widget, 1)

        # Кнопка прокрутки вправо
        self.scroll_right_btn = QPushButton("▶")
        self.scroll_right_btn.setFixedSize(30, 40)
        self.scroll_right_btn.setCursor(Qt.PointingHandCursor)
        self.scroll_right_btn.setStyleSheet(self.scroll_left_btn.styleSheet())
        self.scroll_right_btn.clicked.connect(self.scroll_chords_right)
        self.scroll_right_btn.hide()
        chords_layout.addWidget(self.scroll_right_btn)

        self.chords_container = chords_container
        self.chords_container.hide()
        left_layout.addWidget(self.chords_container)

        content_layout.addWidget(left_widget, 3)  # 60% ширины

        # ПРАВАЯ ЧАСТЬ: поиск и аккорды (40% ширины)
        right_widget = QFrame()
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        # ОБЛАСТЬ ПОИСКА - НА ОДНОМ УРОВНЕ С НАЗВАНИЕМ ПЕСНИ (БЕЗ ЗАГОЛОВКА)
        search_frame = QFrame()
        search_layout = QVBoxLayout(search_frame)
        search_layout.setSpacing(10)
        search_layout.setContentsMargins(0, 0, 0, 0)

        # КОНТЕЙНЕР ДЛЯ ПОЛЯ ПОИСКА И КНОПКИ
        search_input_container = QWidget()
        search_input_container.setStyleSheet("background: transparent; border: none;")
        search_input_layout = QHBoxLayout(search_input_container)
        search_input_layout.setSpacing(10)
        search_input_layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Введите название песни...")
        self.search_input.returnPressed.connect(self.search_songs)

        # КНОПКА "НАЙТИ" С СИНИМ СТИЛЕМ
        self.search_button = QPushButton("Найти")
        self.search_button.setCursor(Qt.PointingHandCursor)
        self.search_button.setFixedHeight(40)
        self.search_button.clicked.connect(self.search_songs)

        search_input_layout.addWidget(self.search_input, 3)
        search_input_layout.addWidget(self.search_button, 1)

        search_layout.addWidget(search_input_container)

        # Список результатов поиска - ТЕПЕРЬ НА ОДНОМ УРОВНЕ С ПОИСКОМ
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.load_song)
        self.results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.results_list.hide()
        search_layout.addWidget(self.results_list)

        right_layout.addWidget(search_frame)

        # Область аккордов - АДАПТИВНАЯ
        chords_frame = QFrame()
        chords_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chords_layout_right = QVBoxLayout(chords_frame)
        chords_layout_right.setSpacing(5)

        # ИНФОРМАЦИЯ ОБ АККОРДЕ - ПРОСТО ТЕКСТ БЕЗ КНОПКИ
        chord_info_widget = QWidget()
        chord_info_widget.setStyleSheet("background: transparent; border: none;")
        chord_info_layout = QVBoxLayout(chord_info_widget)
        chord_info_layout.setSpacing(2)
        chord_info_layout.setContentsMargins(0, 0, 0, 0)

        # Название аккорда - белый шрифт, по центру
        self.chord_name_label = QLabel("")
        self.chord_name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                text-align: center;
                padding: 2px;
                background: transparent;
                border: none;
            }
        """)
        self.chord_name_label.setAlignment(Qt.AlignCenter)
        chord_info_layout.addWidget(self.chord_name_label)

        # Описание аккорда - шрифт чуть меньше, выравнивание по центру
        self.chord_description_label = QLabel("")
        self.chord_description_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                text-align: center;
                padding: 2px;
                background: transparent;
                border: none;
            }
        """)
        self.chord_description_label.setAlignment(Qt.AlignCenter)
        self.chord_description_label.setWordWrap(True)
        chord_info_layout.addWidget(self.chord_description_label)

        chords_layout_right.addWidget(chord_info_widget)

        # АДАПТИВНАЯ область для картинки аккорда
        self.chord_image_label = AdaptiveChordLabel()
        self.chord_image_label.clicked.connect(self.show_chord_large)

        # Устанавливаем политику размера для растягивания
        self.chord_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        chords_layout_right.addWidget(self.chord_image_label, 1)

        # Контейнер для кнопок вариантов - ПРОЗРАЧНЫЙ ФОН
        self.variants_container = QWidget()
        self.variants_container.setStyleSheet("background: transparent; border: none;")
        self.variants_layout = QHBoxLayout(self.variants_container)
        self.variants_layout.setAlignment(Qt.AlignCenter)
        self.variants_layout.setSpacing(8)

        chords_layout_right.addWidget(self.variants_container)

        # Кнопка звука
        self.sound_button = SoundButtonLarge()
        self.sound_button.setText("🔈 Слушать")
        self.sound_button.clicked.connect(self.play_last_variant_sound)
        self.sound_button.hide()
        chords_layout_right.addWidget(self.sound_button, 0, Qt.AlignCenter)

        right_layout.addWidget(chords_frame, 1)

        content_layout.addWidget(right_widget, 2)

        main_layout.addLayout(content_layout, 1)

    def apply_styles(self):
        """Применяет стили ко всем элементам страницы"""
        # Обновляем стили кнопок меню
        self.songs_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.chords_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.tuner_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.learning_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.theory_btn.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)

        # Обновляем стиль заголовка песни
        self.song_title_label.setStyleSheet(DarkTheme.SONG_TITLE_STYLE)

        # Обновляем стиль названия аккорда
        self.chord_name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                text-align: center;
                padding: 2px;
                background: transparent;
                border: none;
            }
        """)

        # Обновляем стиль описания аккорда
        self.chord_description_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                text-align: center;
                padding: 2px;
                background: transparent;
                border: none;
            }
        """)

        # Обновляем стиль поля поиска
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

        # Стиль для кнопки "Найти"
        self.search_button.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)

        # Стиль для текста песни
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

        # Стиль для списка результатов
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

        # Прозрачный фон для контейнеров с кнопками
        self.chords_container.setStyleSheet("background: transparent; border: none;")
        self.scroll_chords_widget.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QWidget {
                background: transparent;
            }
        """)
        self.variants_container.setStyleSheet("background: transparent; border: none;")

        # Убираем фон у всех фреймов
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

    def load_chord_variant(self, image_path, mp3_path):
        """Загрузка конкретного варианта аккорда с адаптивным отображением"""
        try:
            # Загружаем изображение
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.chord_image_label.setChordPixmap(pixmap)
                print(f"✅ Изображение загружено: {os.path.basename(image_path)}")
            else:
                print(f"❌ Не удалось загрузить изображение: {image_path}")
                self.chord_image_label.clear()

            # Сохраняем пути к MP3 для воспроизведения
            self.last_variant_mp3_path = mp3_path

            # Показываем/скрываем кнопку звука в зависимости от наличия звука
            if mp3_path and os.path.exists(mp3_path):
                self.sound_button.show()
                print(f"✅ Звуковой файл доступен: {os.path.basename(mp3_path)}")
            else:
                self.sound_button.hide()
                print(f"⚠️ Звуковой файл отсутствует")

        except Exception as e:
            print(f"❌ Ошибка загрузки варианта аккорда: {e}")
            self.chord_image_label.clear()

    def resizeEvent(self, event):
        """Обработчик изменения размера окна"""
        super().resizeEvent(event)
        if hasattr(self, 'chord_image_label') and self.chord_image_label:
            self.chord_image_label.updatePixmap()

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

            # Очищаем список и добавляем новые результаты
            self.results_list.clear()
            for elem in results:
                self.results_list.addItem(elem)

            # Показываем список результатов
            self.results_list.show()

            # Очищаем поле поиска
            self.search_input.clear()

            # Динамически настраиваем высоту списка результатов
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
            # Убедимся, что список занимает всю ширину контейнера
            self.results_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def create_chord_buttons(self):
        """Создает кнопки аккордов для текущей песни в одну строку с прокруткой"""
        # Очищаем предыдущие кнопки
        chords_layout = self.scroll_chords_widget.chords_layout
        for i in reversed(range(chords_layout.count())):
            widget = chords_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not self.chords_list:
            self.chords_container.hide()
            return

        unique_chords = sorted(set(self.chords_list))

        for chord in unique_chords:
            btn = ChordButton(chord)
            btn.clicked.connect(lambda checked, c=chord: self.on_chord_button_clicked(c))
            chords_layout.addWidget(btn)

        self.chords_container.show()
        self.update_scroll_buttons()

    def scroll_chords_left(self):
        """Прокрутка аккордов влево на один аккорд"""
        scroll_area = self.scroll_chords_widget
        if scroll_area:
            chords_layout = scroll_area.chords_layout
            if chords_layout.count() > 0:
                scrollbar = scroll_area.horizontalScrollBar()
                if chords_layout.itemAt(0).widget():
                    button_width = chords_layout.itemAt(0).widget().width() + 5
                    scrollbar.setValue(scrollbar.value() - button_width)
            self.update_scroll_buttons()

    def scroll_chords_right(self):
        """Прокрутка аккордов вправо на один аккорд"""
        scroll_area = self.scroll_chords_widget
        if scroll_area:
            chords_layout = scroll_area.chords_layout
            if chords_layout.count() > 0:
                scrollbar = scroll_area.horizontalScrollBar()
                if chords_layout.itemAt(0).widget():
                    button_width = chords_layout.itemAt(0).widget().width() + 5
                    scrollbar.setValue(scrollbar.value() + button_width)
            self.update_scroll_buttons()

    def update_scroll_buttons(self):
        """Обновляет состояние кнопок прокрутки"""
        scroll_area = self.scroll_chords_widget
        if scroll_area:
            scrollbar = scroll_area.horizontalScrollBar()
            needs_scrolling = scrollbar.maximum() > 0

            if needs_scrolling:
                self.scroll_left_btn.setEnabled(scrollbar.value() > 0)
                self.scroll_right_btn.setEnabled(scrollbar.value() < scrollbar.maximum())
                self.scroll_left_btn.show()
                self.scroll_right_btn.show()
            else:
                self.scroll_left_btn.hide()
                self.scroll_right_btn.hide()

    def on_chord_button_clicked(self, chord_name):
        """Обработчик клика по кнопке аккорда"""
        print(f"🎸 Клик по кнопке аккорда: {chord_name}")
        chord_url = QUrl(chord_name)
        self.chord_clicked(chord_url)

    def load_song(self, item):
        """Загрузка выбранной песни"""
        if not item:
            return

        self.sound_button.hide()
        # Очищаем информацию об аккорде
        self.chord_name_label.setText("")
        self.chord_description_label.setText("")

        try:
            # Очистка предыдущих элементов
            for i in reversed(range(self.variants_layout.count())):
                widget = self.variants_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Очищаем кнопки аккордов
            chords_layout = self.scroll_chords_widget.chords_layout
            for i in reversed(range(chords_layout.count())):
                widget = chords_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            self.chords_container.hide()

            self.current_chord_folder = ""
            self.last_variant_mp3_path = ""
            self.current_chord_name = ""
            self.current_song_title = item.text()

            # Обновляем заголовок с названием песни
            self.song_title_label.setText(f"🎵 {self.current_song_title}")

            song_info = db.select_chord_song_info(self.current_song_title)

            with open(f'{song_info[4]}', 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()

            # Обработка списка аккордов
            chords_raw = song_info[3]
            if chords_raw:
                self.chords_list = [ch.strip() for ch in chords_raw.split(',') if ch.strip()]
            else:
                self.chords_list = []

            # Создаем кнопки аккордов
            self.create_chord_buttons()

            # Убираем первые три строки: название, пустую строку и строку с аккордами
            if len(lines) >= 3:
                lines = lines[3:]

            # Убираем только полностью пустые строки, но сохраняем пробелы
            processed_lines = []
            for line in lines:
                if line.strip() != '' or line.rstrip('\n') != '':
                    processed_lines.append(line.rstrip('\n'))

            # Формируем HTML-ссылки для аккордов
            chord_links_dict = {}
            for chord in set(self.chords_list):
                safe_chord = html.escape(chord)
                link_html = f'<a href="{safe_chord}" style="color: #3498db; font-weight: bold; text-decoration: none; background: rgba(52, 152, 219, 0.1); padding: 2px 6px; border-radius: 4px;">{safe_chord}</a>'
                chord_links_dict[chord] = link_html

            # Объединяем текст, сохраняя пробелы и переносы
            full_text_raw = '<br>'.join(processed_lines)

            # Замена аккордов на ссылки
            if self.chords_list:
                for chord in sorted(set(self.chords_list), key=len, reverse=True):
                    if not chord:
                        continue
                    safe_chord = html.escape(chord)
                    link_html = chord_links_dict[chord]
                    pattern = r'(?<![a-zA-Z0-9#\-/])' + re.escape(chord) + r'(?![a-zA-Z0-9#\-/])'
                    full_text_raw = re.sub(pattern, link_html, full_text_raw)

            # Финальное оформление с уменьшенным межстрочным расстоянием
            styled_text = f"""
            <div style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt; line-height: 1.4; color: #ecf0f1;">
                {full_text_raw}
            </div>
            """
            self.song_text.setHtml(styled_text)

            # Автозагрузка первого аккорда
            if self.chords_list:
                first_chord = self.chords_list[0]
                print(f"🎵 Автозагрузка первого аккорда: {first_chord}")
                chord_url = QUrl(first_chord)
                self.chord_clicked(chord_url)

        except Exception as e:
            print(f"Ошибка загрузки песни: {e}")
            import traceback
            traceback.print_exc()

    def chord_clicked(self, url):
        """Обработчик клика по аккорду в тексте песни"""
        try:
            chord_name = url.toString()
            print(f"🔍 Загружаем аккорд: {chord_name}")
            self.current_chord_name = chord_name

            # Получаем информацию об аккорде из базы данных
            chord_info = self.chord_repository.get_chord_info(chord_name)
            if not chord_info:
                print(f"❌ Аккорд {chord_name} не найден в базе данных")
                return

            # Обновляем информацию об аккорде
            self.chord_name_label.setText(f"Аккорд {chord_name}")

            # Получаем описание аккорда из данных const
            chord_description = self.get_chord_description(chord_name)
            self.chord_description_label.setText(chord_description)

            self.current_chord_folder = chord_info[2]

            # Очищаем предыдущие варианты
            for i in reversed(range(self.variants_layout.count())):
                widget = self.variants_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Загружаем варианты аккорда через репозиторий
            variants = self.chord_repository.get_chord_variants_by_name(chord_name)
            if not variants:
                print(f"❌ Варианты аккорда {chord_name} не найдены")
                return

            self.current_chord_variants = variants

            # Создаем кнопки для вариантов
            for idx, variant in enumerate(variants):
                btn = ChordVariantButton(str(idx + 1))
                btn.setProperty('variant_data', (variant[2], variant[3]))

                def make_handler(variant_img_path, variant_mp3_path, button):
                    def handler():
                        self.load_chord_variant(variant_img_path, variant_mp3_path)
                        # Сброс выделения других кнопок и установка текущей
                        for i in range(self.variants_layout.count()):
                            other_btn = self.variants_layout.itemAt(i).widget()
                            if other_btn:
                                other_btn.setChecked(False)
                                other_btn.update_style()
                        button.setChecked(True)
                        button.update_style()

                    return handler

                handler = make_handler(variant[2], variant[3], btn)
                btn.clicked.connect(handler)
                self.variants_layout.addWidget(btn)

            # Активируем первый вариант
            self.activate_first_variant(variants)

        except Exception as e:
            print(f"❌ Ошибка загрузки аккорда: {e}")
            import traceback
            traceback.print_exc()

    def activate_first_variant(self, variants):
        """Автоматически активирует первый вариант аккорда"""
        if not variants:
            print("❌ Нет вариантов для активации")
            return

        try:
            first_variant = variants[0]

            # Загружаем изображение и звук первого варианта
            self.load_chord_variant(first_variant[2], first_variant[3])

            # Находим и активируем первую кнопку
            if self.variants_layout.count() > 0:
                first_btn = self.variants_layout.itemAt(0).widget()
                if first_btn:
                    first_btn.setChecked(True)
                    first_btn.update_style()
                    print(f"✅ Автоматически активирован вариант 1 для аккорда {self.current_chord_name}")

        except Exception as e:
            print(f"❌ Ошибка активации первого варианта: {e}")

    def play_last_variant_sound(self):
        """Воспроизведение звука текущего варианта аккорда"""
        if self.last_variant_mp3_path and os.path.exists(self.last_variant_mp3_path):
            url = QUrl.fromLocalFile(self.last_variant_mp3_path)
            self.player.setMedia(QMediaContent(url))
            self.player.play()
            print(f"🔊 Воспроизведение звука: {os.path.basename(self.last_variant_mp3_path)}")
        else:
            print(f"❌ Файл не найден: {self.last_variant_mp3_path}")

    def show_chord_large(self):
        """Показ увеличенного окна с аккордом"""
        if not self.current_chord_name or not self.current_chord_folder:
            return

        try:
            # Получаем все варианты аккорда через репозиторий
            variants = self.chord_repository.get_chord_variants_by_name(self.current_chord_name)
            if not variants:
                return

            # Создаем окно просмотра
            first_variant = variants[0]
            from gui.windows.chord_viewer import ChordViewerWindow
            viewer = ChordViewerWindow(
                self.current_chord_name,
                first_variant[2],
                first_variant[3],
                self
            )

            # Добавляем кнопки вариантов
            variants_data = [(v[2], v[3]) for v in variants]
            viewer.add_variant_buttons(variants_data)

            viewer.exec_()

        except Exception as e:
            print(f"Ошибка открытия окна аккорда: {e}")
            import traceback
            traceback.print_exc()

    def handle_error(self, error):
        """Обработчик ошибок медиаплеера"""
        print(f"Ошибка медиаплеера: {error}")

    def on_page_show(self):
        """Вызывается при показе страницы"""
        print("Страница песен показана")

    def on_page_hide(self):
        """Вызывается при скрытии страницы"""
        print("Страница песен скрыта")
        # Очищаем временные файлы при скрытии страницы
        self.chord_repository.chord_manager.cleanup()

    def cleanup(self):
        """Очистка ресурсов при закрытии приложения"""
        if hasattr(self, 'chord_repository'):
            self.chord_repository.chord_manager.cleanup()