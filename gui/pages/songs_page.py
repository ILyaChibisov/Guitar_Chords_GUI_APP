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
from gui.widgets.labels import ChordImageLabel
from gui.widgets.media import ScrollChordButtonsWidget
from database.queries import SongQueries, ChordQueries
import database.db_scripts as db
from const import *


class SongsPage(BasePage):
    """Страница песен и аккордов - полная версия из оригинального кода"""

    def __init__(self, parent=None):
        super().__init__("songs", parent)

        # Переменные для пагинации аккордов
        self.current_chord_index = 0
        self.chords_list = []
        self.current_chord_folder = ""
        self.last_variant_mp3_path = ""
        self.current_chord_name = ""
        self.current_song_title = ""

        self.player = QMediaPlayer()
        self.player.error.connect(self.handle_error)

        self.initialize_page()

    def setup_ui(self):
        """Полная настройка UI из оригинального MusicApp"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ДОБАВИТЬ: Главное меню сверху
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

        # Добавляем кнопки в меню
        menu_layout.addWidget(self.songs_btn)
        menu_layout.addWidget(self.chords_btn)
        menu_layout.addWidget(self.tuner_btn)
        menu_layout.addWidget(self.learning_btn)
        menu_layout.addWidget(self.theory_btn)

        # Добавляем меню в основной layout
        main_layout.addWidget(menu_widget)

        # Создаем горизонтальный layout для основного содержимого
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # Левая часть: текст песни
        left_widget = QFrame()
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок текста песни (будет меняться динамически)
        self.song_title_label = QLabel("🎵 Текст песни с аккордами")
        self.song_title_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 18px;
                font-weight: bold;
                padding: 12px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                margin-bottom: 8px;
                text-align: center;
            }
        """)
        self.song_title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.song_title_label)

        self.song_text = QTextBrowser()
        self.song_text.setReadOnly(True)
        self.song_text.setOpenLinks(False)
        self.song_text.anchorClicked.connect(self.chord_clicked)

        # Отключаем горизонтальную прокрутку
        self.song_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.song_text.setWordWrapMode(True)

        left_layout.addWidget(self.song_text, 1)

        # ДОБАВИТЬ: Контейнер для кнопок аккордов песни ПОД текстом песни
        chords_container = QWidget()
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

        # Область с кнопками аккордов
        self.scroll_chords_widget = ScrollChordButtonsWidget()
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
        self.chords_container.hide()  # Сначала скрываем
        left_layout.addWidget(self.chords_container)

        content_layout.addWidget(left_widget, 2)

        # Правая часть: поиск и аккорды
        right_widget = QFrame()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        # Область поиска (поднята вверх)
        search_frame = QFrame()
        search_layout = QVBoxLayout(search_frame)

        search_input_layout = QHBoxLayout()

        # Поле поиска с иконкой
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Введите название песни...")
        self.search_input.returnPressed.connect(self.search_songs)

        self.search_button = ModernButton("Найти")
        self.search_button.clicked.connect(self.search_songs)

        search_input_layout.addWidget(self.search_input, 3)
        search_input_layout.addWidget(self.search_button, 1)

        search_layout.addLayout(search_input_layout)

        # Список результатов поиска (динамическая высота)
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.load_song)
        # Отключаем горизонтальную прокрутку
        self.results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.results_list.hide()  # Скрываем до первого поиска
        search_layout.addWidget(self.results_list)

        right_layout.addWidget(search_frame)

        # Область аккордов (теперь занимает оставшееся пространство)
        chords_frame = QFrame()
        chords_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chords_layout_right = QVBoxLayout(chords_frame)

        # Красивое отображение названия аккорда
        self.chord_title_label = QLabel("")
        self.chord_title_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4CAF50, stop: 1 #45a049);
                color: white;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
                padding: 8px 15px;
                border-radius: 20px;
                margin: 5px;
            }
        """)
        self.chord_title_label.setAlignment(Qt.AlignCenter)
        self.chord_title_label.setMinimumHeight(40)
        chords_layout_right.addWidget(self.chord_title_label)

        # Область для картинки аккорда (кликабельная)
        self.chord_image_label = ChordImageLabel()
        self.chord_image_label.setMinimumSize(200, 300)
        self.chord_image_label.setAlignment(Qt.AlignCenter)
        self.chord_image_label.clicked.connect(self.show_chord_large)

        # ДОБАВИТЬ: Установить политику размера для растягивания
        self.chord_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        chords_layout_right.addWidget(self.chord_image_label, 1)

        # Контейнер для кнопок вариантов (под картинкой)
        self.variants_container = QWidget()
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

        content_layout.addWidget(right_widget, 1)

        # Добавляем контент в основной layout
        main_layout.addLayout(content_layout, 1)

    def connect_signals(self):
        """Подключение сигналов"""
        # Сигналы уже подключены в setup_ui через clicked.connect
        pass

    def search_songs(self):
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
            # Высота основывается на количестве элементов (макс 6 элементов)
            item_height = 50
            max_height = min(item_count, 6) * item_height + 20
            self.results_list.setFixedHeight(max_height)
            self.results_list.show()

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
                # Смещаем на ширину одной кнопки + отступ
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
                # Смещаем на ширину одной кнопки + отступ
                if chords_layout.itemAt(0).widget():
                    button_width = chords_layout.itemAt(0).widget().width() + 5
                    scrollbar.setValue(scrollbar.value() + button_width)
            self.update_scroll_buttons()

    def update_scroll_buttons(self):
        """Обновляет состояние кнопок прокрутки"""
        scroll_area = self.scroll_chords_widget
        if scroll_area:
            scrollbar = scroll_area.horizontalScrollBar()
            # Проверяем, нужно ли вообще показывать кнопки прокрутки
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
        chord_url = QUrl(chord_name)
        self.chord_clicked(chord_url)

    def load_song(self, item):
        if not item:
            return

        self.sound_button.hide()
        self.chord_title_label.setText("")
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
                # Пропускаем первые три строки
                lines = lines[3:]

            # Убираем только полностью пустые строки, но сохраняем пробелы
            processed_lines = []
            for line in lines:
                # Сохраняем строку, даже если в ней есть только пробелы
                if line.strip() != '' or line.rstrip('\n') != '':
                    processed_lines.append(line.rstrip('\n'))

            # Формируем HTML-ссылки для аккордов (синий цвет)
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
                chord_url = QUrl(first_chord)
                self.chord_clicked(chord_url)

        except Exception as e:
            print(f"Ошибка загрузки песни: {e}")
            import traceback
            traceback.print_exc()

    def chord_clicked(self, url):
        try:
            chord_name = url.toString()
            self.current_chord_name = chord_name

            # Обновляем заголовок с названием аккорда
            self.chord_title_label.setText(f"Аппликатура: {chord_name}")
            self.sound_button.show()

            chord_info = db.select_chord(chord_name)
            if not chord_info:
                print(f"Аккорд {chord_name} не найден в базе данных")
                return

            self.current_chord_folder = chord_info[2]

            # Очищаем предыдущие варианты
            for i in reversed(range(self.variants_layout.count())):
                widget = self.variants_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Загружаем варианты аккорда
            variants = get_files_in_folder(chord_info[2])
            print(chord_info[2])
            print(chord_info[3])
            if not variants:
                print(f"Варианты аккорда {chord_name} не найдены")
                return

            # Создаем кнопки для вариантов
            for idx, variant in enumerate(variants):
                btn = ChordVariantButton(str(idx + 1))
                btn.setProperty('variant_data', (variant[1], variant[2]))

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

                handler = make_handler(variant[1], variant[2], btn)
                btn.clicked.connect(handler)
                self.variants_layout.addWidget(btn)

            # Активируем первый вариант
            if variants:
                first_variant = variants[0]
                first_btn = self.variants_layout.itemAt(0).widget()
                if first_btn:
                    self.load_chord_variant(first_variant[1], first_variant[2])
                    first_btn.setChecked(True)
                    first_btn.update_style()

        except Exception as e:
            print(f"Ошибка загрузки аккорда: {e}")
            import traceback
            traceback.print_exc()

    def load_chord_variant(self, image_path, mp3_path):
        try:
            # Загружаем изображение
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Масштабируем изображение для отображения в интерфейсе
                scaled_pixmap = pixmap.scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.chord_image_label.setPixmap(scaled_pixmap)
            else:
                print(f"Не удалось загрузить изображение: {image_path}")

            # Сохраняем путь к MP3 для воспроизведения
            self.last_variant_mp3_path = mp3_path

        except Exception as e:
            print(f"Ошибка загрузки варианта аккорда: {e}")

    def play_last_variant_sound(self):
        if self.last_variant_mp3_path and os.path.exists(self.last_variant_mp3_path):
            url = QUrl.fromLocalFile(self.last_variant_mp3_path)
            self.player.setMedia(QMediaContent(url))
            self.player.play()
        else:
            print(f"Файл не найден: {self.last_variant_mp3_path}")

    def show_chord_large(self):
        if not self.current_chord_name or not self.current_chord_folder:
            return

        try:
            # Получаем все варианты аккорда
            chord_info = db.select_chord(self.current_chord_name)
            if not chord_info:
                return

            variants = get_files_in_folder(chord_info[2])
            print(chord_info[2])
            print(chord_info[3])
            if not variants:
                return

            # Создаем окно просмотра
            first_variant = variants[0]
            from gui.windows.chord_viewer import ChordViewerWindow
            viewer = ChordViewerWindow(
                self.current_chord_name,
                first_variant[1],
                first_variant[2],
                self
            )

            # Добавляем кнопки вариантов
            variants_data = [(v[1], v[2]) for v in variants]
            viewer.add_variant_buttons(variants_data)

            viewer.exec_()

        except Exception as e:
            print(f"Ошибка открытия окна аккорда: {e}")
            import traceback
            traceback.print_exc()

    def handle_error(self, error):
        print(f"Ошибка медиаплеера: {error}")

    def on_page_show(self):
        """Вызывается при показе страницы"""
        print("Страница песен показана")

    def on_page_hide(self):
        """Вызывается при скрытии страницы"""
        print("Страница песен скрыта")