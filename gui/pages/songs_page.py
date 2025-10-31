import os
import re
import html
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QListWidget, QTextBrowser, QLabel,
                             QFrame, QScrollArea, QSizePolicy)
from PyQt5.QtCore import QUrl, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from .base_page import BasePage
from gui.widgets.buttons import ModernButton, MenuButton, ChordButton, SoundButtonLarge, ChordVariantButton, \
    PaginationButton
from gui.widgets.labels import AdaptiveChordLabel
from gui.widgets.media import ScrollChordButtonsWidget
from database.queries import SongQueries
from database.chord_repository import ChordRepository
import database.db_scripts as db
from config.styles import DarkTheme


class SongsPage(BasePage):
    """Страница песен и аккордов с правильной пагинацией"""

    def __init__(self, parent=None):
        super().__init__("songs", parent)

        # Переменные для пагинации аккордов
        self.chords_per_page = 8  # Максимум аккордов на странице
        self.current_page = 0  # Текущая страница (начинаем с 0)
        self.unique_chords = []

        # Остальные переменные
        self.chords_list = []
        self.current_chord_folder = ""
        self.last_variant_mp3_path = ""
        self.current_chord_name = ""
        self.current_song_title = ""
        self.current_chord_variants = []
        self.variant_buttons = []  # Хранилище для кнопок вариантов

        # Репозиторий для работы с встроенными аккордами
        self.chord_repository = ChordRepository()

        self.player = QMediaPlayer()
        self.player.error.connect(self.handle_error)

        self.initialize_page()

    def get_chord_description(self, chord_name):
        """Получает описание аккорда из репозитория"""
        return self.chord_repository.get_chord_description(chord_name)

    def setup_ui(self):
        """Настройка UI с правильной пагинацией"""
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
        self.song_title_label.setStyleSheet(DarkTheme.SONG_TITLE_STYLE)
        self.song_title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.song_title_label)

        # ТЕКСТ ПЕСНИ
        self.song_text = QTextBrowser()
        self.song_text.setReadOnly(True)
        self.song_text.setOpenLinks(False)
        self.song_text.anchorClicked.connect(self.chord_clicked)
        self.song_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.song_text.setWordWrapMode(True)
        left_layout.addWidget(self.song_text, 1)

        # ОБЩИЙ КОНТЕЙНЕР ДЛЯ АККОРДОВ И ПАГИНАЦИИ
        self.chords_main_container = QWidget()
        self.chords_main_container.setStyleSheet("background: transparent; border: none;")
        self.chords_main_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.chords_main_container.setMinimumHeight(80)

        chords_main_layout = QVBoxLayout(self.chords_main_container)
        chords_main_layout.setContentsMargins(0, 0, 0, 0)
        chords_main_layout.setSpacing(0)

        # КОНТЕЙНЕР С КНОПКАМИ АККОРДОВ И ПАГИНАЦИЕЙ В ОДНОЙ СТРОКЕ
        chords_pagination_container = QWidget()
        chords_pagination_container.setStyleSheet("background: transparent; border: none;")
        chords_pagination_layout = QHBoxLayout(chords_pagination_container)
        chords_pagination_layout.setContentsMargins(0, 0, 0, 0)
        chords_pagination_layout.setSpacing(15)

        # Кнопка пагинации влево
        self.scroll_left_btn = PaginationButton("◀")
        self.scroll_left_btn.clicked.connect(self.previous_page)
        self.scroll_left_btn.hide()

        # Область с кнопками аккордов
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

        # Кнопка пагинации вправо
        self.scroll_right_btn = PaginationButton("▶")
        self.scroll_right_btn.clicked.connect(self.next_page)
        self.scroll_right_btn.hide()

        chords_pagination_layout.addWidget(self.scroll_left_btn)
        chords_pagination_layout.addWidget(self.scroll_chords_widget, 1)
        chords_pagination_layout.addWidget(self.scroll_right_btn)

        chords_main_layout.addWidget(chords_pagination_container)
        self.chords_main_container.hide()
        left_layout.addWidget(self.chords_main_container)

        content_layout.addWidget(left_widget, 3)

        # ПРАВАЯ ЧАСТЬ: поиск и аккорды (40% ширины)
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
        chords_layout_right.setSpacing(5)

        chord_info_widget = QWidget()
        chord_info_widget.setStyleSheet("background: transparent; border: none;")
        chord_info_layout = QVBoxLayout(chord_info_widget)
        chord_info_layout.setSpacing(2)
        chord_info_layout.setContentsMargins(0, 0, 0, 0)

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

        self.chord_image_label = AdaptiveChordLabel()
        self.chord_image_label.clicked.connect(self.show_chord_large)
        self.chord_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chords_layout_right.addWidget(self.chord_image_label, 1)

        # Контейнер для кнопок типов отображения
        self.display_type_container = QWidget()
        self.display_type_container.setStyleSheet("background: transparent; border: none;")
        self.display_type_layout = QHBoxLayout(self.display_type_container)
        self.display_type_layout.setAlignment(Qt.AlignCenter)
        self.display_type_layout.setSpacing(8)
        chords_layout_right.addWidget(self.display_type_container)

        # Контейнер для вариантов аккорда
        self.variants_container = QWidget()
        self.variants_container.setStyleSheet("background: transparent; border: none;")
        self.variants_layout = QHBoxLayout(self.variants_container)
        self.variants_layout.setAlignment(Qt.AlignCenter)
        self.variants_layout.setSpacing(8)
        chords_layout_right.addWidget(self.variants_container)

        # 🔧 ТЕСТОВАЯ КНОПКА
        self.test_button = QPushButton("🔧 ТЕСТ: Следующий вариант")
        self.test_button.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)
        self.test_button.clicked.connect(self.test_next_variant)
        self.test_button.hide()  # Сначала скрыта
        chords_layout_right.addWidget(self.test_button)

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

        self.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)

    def load_chord_variant(self, variant_data):
        """Загрузка конкретного варианта аккорда"""
        try:
            print(f"🎯 Загрузка варианта {variant_data.get('position', 'unknown')}")

            if isinstance(variant_data, dict) and 'pixmap' in variant_data:
                pixmap = variant_data['pixmap']
                if not pixmap.isNull():
                    print(f"🔄 Установка нового pixmap: {pixmap.size().width()}x{pixmap.size().height()}")

                    # ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ
                    self.chord_image_label.clear()  # Сначала очищаем
                    self.chord_image_label.setChordPixmap(pixmap)  # Затем устанавливаем

                    # Принудительная перерисовка
                    self.chord_image_label.repaint()
                    self.chord_image_label.update()
                    self.repaint()
                    self.update()

                    print(f"✅ Pixmap установлен и обновлен")
                else:
                    self.chord_image_label.clear()
                    print("❌ Pixmap пустой")

                self.last_variant_mp3_path = variant_data.get('sound_path', '')

            elif isinstance(variant_data, tuple) and len(variant_data) >= 2:
                image_path, mp3_path = variant_data[0], variant_data[1]
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    image = pixmap.toImage()
                    if image.hasAlphaChannel():
                        image = image.convertToFormat(QImage.Format_ARGB32)
                        pixmap = QPixmap.fromImage(image)
                    self.chord_image_label.setChordPixmap(pixmap)
                    print(f"✅ Изображение загружено: {image_path}")
                else:
                    self.chord_image_label.clear()
                    print(f"❌ Не удалось загрузить изображение: {image_path}")

                self.last_variant_mp3_path = mp3_path
            else:
                self.chord_image_label.clear()
                self.last_variant_mp3_path = ""
                print("❌ Неизвестный формат variant_data")

            # Показываем/скрываем кнопку звука
            if self.last_variant_mp3_path and os.path.exists(self.last_variant_mp3_path):
                self.sound_button.show()
                print(f"🔊 Звук доступен: {self.last_variant_mp3_path}")
            else:
                self.sound_button.hide()
                print("🔇 Звук не доступен")

        except Exception as e:
            print(f"❌ Ошибка загрузки варианта аккорда: {e}")
            self.chord_image_label.clear()
            self.sound_button.hide()

    def test_next_variant(self):
        """Тестовая функция для принудительного переключения варианта"""
        if not self.current_chord_variants:
            print("❌ Нет загруженных вариантов")
            return

        # Находим текущий выбранный вариант
        current_index = 0
        for i in range(self.variants_layout.count()):
            btn = self.variants_layout.itemAt(i).widget()
            if btn and btn.isChecked():
                current_index = i
                break

        # Переключаем на следующий вариант
        next_index = (current_index + 1) % len(self.current_chord_variants)
        next_variant = self.current_chord_variants[next_index]

        print(f"🧪 ТЕСТ: Переключение с варианта {current_index + 1} на {next_index + 1}")
        print(
            f"🧪 Данные варианта: position={next_variant.get('position')}, variant_index={next_variant.get('variant_index')}")
        self.load_chord_variant(next_variant)

        # Обновляем кнопку
        next_btn = self.variants_layout.itemAt(next_index).widget()
        if next_btn:
            for i in range(self.variants_layout.count()):
                btn = self.variants_layout.itemAt(i).widget()
                if btn:
                    btn.setChecked(False)
                    btn.update_style()
            next_btn.setChecked(True)
            next_btn.update_style()

    def initialize_page(self):
        """Инициализация страницы"""
        if not self.is_initialized:
            self.setup_ui()
            self.connect_signals()
            self.apply_styles()
            self.is_initialized = True

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

        self.unique_chords = sorted([chord for chord in set(self.chords_list)
                                     if self.chord_repository.check_chord_exists(chord)])

        if not self.unique_chords:
            self.chords_main_container.hide()
            print("⚠️ Нет доступных аккордов для отображения")
            return

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

        self.sound_button.hide()
        self.chord_name_label.setText("")
        self.chord_description_label.setText("")
        self.test_button.hide()  # Скрываем тестовую кнопку

        try:
            # Очистка предыдущих элементов
            for i in reversed(range(self.variants_layout.count())):
                widget = self.variants_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            for i in reversed(range(self.display_type_layout.count())):
                widget = self.display_type_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            chords_layout = self.scroll_chords_widget.chords_layout
            for i in reversed(range(chords_layout.count())):
                widget = chords_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            self.chords_main_container.hide()

            self.current_chord_folder = ""
            self.last_variant_mp3_path = ""
            self.current_chord_name = ""
            self.current_song_title = item.text()

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
                if self.chord_repository.check_chord_exists(first_chord):
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
            self.current_chord_name = chord_name

            # Проверяем существование аккорда
            if not self.chord_repository.check_chord_exists(chord_name):
                print(f"❌ Аккорд {chord_name} не найден в данных")
                return

            chord_info = self.chord_repository.get_chord_info(chord_name)
            if not chord_info:
                return

            self.chord_name_label.setText(f"Аккорд {chord_name}")
            chord_description = self.get_chord_description(chord_name)
            self.chord_description_label.setText(chord_description)

            self.current_chord_folder = chord_info.get('folder', 'unknown')

            # Очищаем предыдущие элементы
            for i in reversed(range(self.variants_layout.count())):
                widget = self.variants_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            for i in reversed(range(self.display_type_layout.count())):
                widget = self.display_type_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Создаем кнопки типов отображения
            display_types = self.chord_repository.get_display_types()
            for display_type in display_types:
                btn = ChordVariantButton(display_type.capitalize())
                btn.setProperty('display_type', display_type)

                def make_display_handler(disp_type):
                    def handler():
                        self.load_chord_with_display_type(chord_name, disp_type)

                    return handler

                btn.clicked.connect(make_display_handler(display_type))
                self.display_type_layout.addWidget(btn)

            # Загружаем аккорд с типом отображения по умолчанию
            self.load_chord_with_display_type(chord_name, "fingers")

            # ПОКАЗЫВАЕМ ТЕСТОВУЮ КНОПКУ
            self.test_button.show()

        except Exception as e:
            print(f"❌ Ошибка загрузки аккорда: {e}")

    def load_chord_with_display_type(self, chord_name, display_type):
        """Загружает аккорд с указанным типом отображения и ПЕРВЫМ вариантом"""
        try:
            # Очищаем варианты
            for i in reversed(range(self.variants_layout.count())):
                widget = self.variants_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Получаем варианты с указанным типом отображения
            variants = self.chord_repository.get_chord_variants_by_name(chord_name, display_type)
            if not variants:
                print(f"❌ Нет вариантов для аккорда {chord_name} с типом {display_type}")
                return

            self.current_chord_variants = variants
            print(f"🎯 Загружено вариантов: {len(variants)} для {chord_name}")

            # Храним ссылки на кнопки
            self.variant_buttons = []

            # Создаем кнопки вариантов
            for i, variant_data in enumerate(variants):
                btn = ChordVariantButton(str(variant_data['position']))
                btn.setProperty('variant_data', variant_data)
                btn.setProperty('variant_index', variant_data['variant_index'])
                btn.setProperty('button_index', i)

                # Прямое подключение с использованием индекса
                btn.clicked.connect(lambda checked, idx=i: self.on_variant_clicked(idx))

                self.variants_layout.addWidget(btn)
                self.variant_buttons.append(btn)

            # Активируем ПЕРВЫЙ вариант
            if variants:
                first_variant = variants[0]
                print(f"🎯 Активация первого варианта: {first_variant['position']}")
                self.load_chord_variant(first_variant)
                if self.variant_buttons:
                    self.variant_buttons[0].setChecked(True)
                    self.variant_buttons[0].update_style()

        except Exception as e:
            print(f"❌ Ошибка загрузки аккорда с типом {display_type}: {e}")
            import traceback
            traceback.print_exc()

    def on_variant_clicked(self, button_index):
        """Обработчик клика по варианту аккорда"""
        try:
            if (not self.variant_buttons or
                    button_index >= len(self.variant_buttons) or
                    button_index >= len(self.current_chord_variants)):
                return

            variant_data = self.current_chord_variants[button_index]
            btn = self.variant_buttons[button_index]

            print(f"🎯 Выбран вариант {variant_data['position']} (индекс: {button_index})")
            self.load_chord_variant(variant_data)

            # Сбрасываем выделение всех кнопок
            for variant_btn in self.variant_buttons:
                variant_btn.setChecked(False)
                variant_btn.update_style()

            # Выделяем текущую кнопку
            btn.setChecked(True)
            btn.update_style()

        except Exception as e:
            print(f"❌ Ошибка при переключении варианта: {e}")

    def play_last_variant_sound(self):
        """Воспроизведение звука текущего варианта аккорда"""
        if self.last_variant_mp3_path and os.path.exists(self.last_variant_mp3_path):
            url = QUrl.fromLocalFile(self.last_variant_mp3_path)
            self.player.setMedia(QMediaContent(url))
            self.player.play()

    def show_chord_large(self):
        """Показ увеличенного окна с аккордом"""
        if not self.current_chord_name:
            return
        print("ℹ️ Просмотр аккорда в основном интерфейсе")

    def handle_error(self, error):
        """Обработчик ошибок медиаплеера"""
        print(f"Ошибка медиаплеера: {error}")

    def on_page_show(self):
        """Вызывается при показе страницы"""
        print("Страница песен показана")

        if not self.chord_repository.is_data_available():
            print("⚠️ Данные аккордов не загружены")

    def on_page_hide(self):
        """Вызывается при скрытии страницы"""
        print("Страница песен скрыта")

    def cleanup(self):
        """Очистка ресурсов при закрытии приложения"""
        if hasattr(self, 'chord_repository'):
            self.chord_repository.chord_manager.cleanup()