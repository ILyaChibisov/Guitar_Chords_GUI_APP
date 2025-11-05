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

# Импортируем систему отображения аккордов из первого приложения
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
                # os.path.join(self.sounds_dir, f"{chord_name}{variant}.mp3"),
                # os.path.join(self.sounds_dir, f"{chord_name}.mp3"),
                # os.path.join(self.sounds_dir, f"{chord_name.upper()}v{variant}.mp3"),
                # os.path.join(self.sounds_dir, f"{chord_name.upper()}{variant}.mp3"),
                # os.path.join(self.sounds_dir, f"{chord_name.upper()}.mp3"),
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
    """Менеджер конфигураций аккордов - читает из Excel и JSON как в оригинальном приложении"""

    def __init__(self):
        self.excel_path = os.path.join("source", "chord_config.xlsx")
        self.template_path = os.path.join("source", "template.json")
        self.image_path = os.path.join("source", "img.png")
        self.chord_data = {}
        self.ram_data = {}
        self.note_data = []  # Данные из листа NOTE - ВАЖНО!
        self.templates = {}
        self.chord_configs_cache = {}

    def load_configurations(self):
        """Загрузка конфигураций из source как в оригинальном приложении"""
        try:
            print("🎵 Загрузка конфигураций из source...")

            # Загружаем Excel как в оригинале
            if os.path.exists(self.excel_path):
                # Основной лист с аккордами
                df_chords = pd.read_excel(self.excel_path, sheet_name='CHORDS')
                self.chord_data = df_chords.to_dict('records')
                print(f"✅ Загружено {len(self.chord_data)} аккордов из Excel")

                # Загружаем данные RAM
                try:
                    df_ram = pd.read_excel(self.excel_path, sheet_name='RAM')
                    self.ram_data = df_ram.to_dict('records')
                    print(f"✅ Загружено {len(self.ram_data)} RAM конфигураций")
                except Exception as e:
                    print(f"⚠️ Лист RAM не найден: {e}")

                # Загружаем данные NOTE - ЭТО ВАЖНО!
                try:
                    df_note = pd.read_excel(self.excel_path, sheet_name='NOTE')
                    self.note_data = df_note.to_dict('records')
                    print(f"✅ Загружено {len(self.note_data)} NOTE конфигураций")
                except Exception as e:
                    print(f"⚠️ Лист NOTE не найден: {e}")
                    self.note_data = []
            else:
                print(f"❌ Excel файл не найден: {self.excel_path}")
                return False

            # Загружаем JSON
            if os.path.exists(self.template_path):
                with open(self.template_path, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
                print("✅ JSON шаблоны загружены")
            else:
                print(f"❌ JSON файл не найден: {self.template_path}")
                return False

            # Проверяем изображение
            if not os.path.exists(self.image_path):
                print(f"❌ Изображение не найдено: {self.image_path}")
                return False

            # Создаем кэш конфигураций
            self.create_chord_configs_cache()
            print(f"📊 Создано конфигураций: {len(self.chord_configs_cache)}")
            return True

        except Exception as e:
            print(f"❌ Ошибка загрузки конфигураций: {e}")
            import traceback
            traceback.print_exc()
            return False

    def create_chord_configs_cache(self):
        """Создание кэша конфигураций аккордов"""
        for chord_row in self.chord_data:
            chord_name = str(chord_row.get('CHORD', '')).strip()
            variant = str(chord_row.get('VARIANT', '')).strip()

            if chord_name:
                chord_key = f"{chord_name}v{variant}" if variant else chord_name

                self.chord_configs_cache[chord_key] = {
                    'base_info': {
                        'chord': chord_name,
                        'variant': variant,
                        'caption': chord_row.get('CAPTION', ''),
                        'type': chord_row.get('TYPE', '')
                    },
                    'excel_data': chord_row,
                    'crop_rect': self.get_crop_rect(chord_row.get('RAM')),
                    'elements_fingers': self.get_chord_elements(chord_row, "fingers"),
                    'elements_notes': self.get_chord_elements(chord_row, "notes")
                }

    def get_crop_rect(self, ram_value):
        """Получение области обрезки из RAM в JSON"""
        if not ram_value or self._is_empty_value(ram_value):
            return None

        ram_name = str(ram_value).strip()

        # Ищем RAM в разделе crop_rects
        if 'crop_rects' in self.templates and ram_name in self.templates['crop_rects']:
            crop_data = self.templates['crop_rects'][ram_name]
            return (
                crop_data.get('x', 0),
                crop_data.get('y', 0),
                crop_data.get('width', 100),
                crop_data.get('height', 100)
            )
        return None

    def get_chord_elements(self, chord_config, display_type):
        """Получение элементов аккорда в зависимости от типа отображения - как в оригинале"""
        elements = []

        # Получаем значение LAD из таблицы RAM на основе RAM аккорда
        ram_key = chord_config.get('RAM')
        lad_value = None
        if ram_key:
            lad_value = self.get_ram_lad_value(ram_key)

        # Добавляем RAM элементы из колонки RAM (для обрезки)
        if ram_key:
            ram_elements = self.get_ram_elements(ram_key)
            elements.extend(ram_elements)

        # Добавляем LAD элементы на основе значения из таблицы RAM
        if lad_value:
            lad_elements = self.get_ram_elements_from_lad(lad_value)
            elements.extend(lad_elements)

        # Добавляем элементы баре ТОЛЬКО для режима пальцев
        if display_type == "fingers":
            bar_elements = self.get_barre_elements(chord_config.get('BAR'))
            elements.extend(bar_elements)

        if display_type == "notes":
            # Для нот: используем FNL и FN
            fnl_elements = self.get_note_elements_from_column(chord_config.get('FNL'), 'FNL')
            fn_elements = self.get_note_elements_from_column(chord_config.get('FN'), 'FN')
            elements.extend(fnl_elements)
            elements.extend(fn_elements)
        else:  # fingers
            # Для пальцев: используем FPOL, FPXL, FP1, FP2, FP3, FP4
            fpol_elements = self.get_note_elements_from_column(chord_config.get('FPOL'), 'FPOL')
            fpxl_elements = self.get_note_elements_from_column(chord_config.get('FPXL'), 'FPXL')
            fp1_elements = self.get_note_elements_from_column(chord_config.get('FP1'), 'FP1')
            fp2_elements = self.get_note_elements_from_column(chord_config.get('FP2'), 'FP2')
            fp3_elements = self.get_note_elements_from_column(chord_config.get('FP3'), 'FP3')
            fp4_elements = self.get_note_elements_from_column(chord_config.get('FP4'), 'FP4')
            elements.extend(fpol_elements)
            elements.extend(fpxl_elements)
            elements.extend(fp1_elements)
            elements.extend(fp2_elements)
            elements.extend(fp3_elements)
            elements.extend(fp4_elements)

        return elements

    def get_ram_lad_value(self, ram_name):
        """Получение значения LAD для указанного RAM из таблицы RAM"""
        if not ram_name or self._is_empty_value(ram_name):
            return None

        ram_name = str(ram_name).strip()

        # Ищем RAM в таблице RAM
        for ram_item in self.ram_data:
            item_ram = ram_item.get('RAM')
            if item_ram and str(item_ram).strip() == ram_name:
                return ram_item.get('LAD')
        return None

    def get_ram_elements(self, ram_name):
        """Получение элементов RAM по имени"""
        elements = []
        if not ram_name or self._is_empty_value(ram_name):
            return elements

        ram_name = str(ram_name).strip()

        # Ищем элементы RAM в frets
        if ram_name in self.templates.get('frets', {}):
            element_data = self.templates['frets'][ram_name]
            element_data['_key'] = ram_name
            element_data['type'] = 'fret'
            elements.append({
                'type': 'fret',
                'data': element_data
            })

        # Ищем элементы с суффиксами (RAM1, RAM2 и т.д.)
        for i in range(1, 5):
            element_key = f"{ram_name}{i}"
            if element_key in self.templates.get('frets', {}):
                element_data = self.templates['frets'][element_key]
                element_data['_key'] = element_key
                element_data['type'] = 'fret'
                elements.append({
                    'type': 'fret',
                    'data': element_data
                })

        return elements

    def get_ram_elements_from_lad(self, lad_value):
        """Получение элементов RAM на основе значения LAD"""
        elements = []
        if not lad_value or self._is_empty_value(lad_value):
            return elements

        lad_value = str(lad_value).strip()
        lad_keys = [key.strip() for key in lad_value.split(',')]

        for lad_key in lad_keys:
            json_key = f"{lad_key}LAD"
            if json_key in self.templates.get('frets', {}):
                element_data = self.templates['frets'][json_key]
                element_data['_key'] = json_key
                element_data['type'] = 'fret'
                elements.append({
                    'type': 'fret',
                    'data': element_data
                })

        return elements

    def get_barre_elements(self, bar_value):
        """Получение элементов баре из колонки BAR"""
        elements = []
        if self._is_empty_value(bar_value):
            return elements

        bar_str = str(bar_value).strip()
        if bar_str in self.templates.get('barres', {}):
            barre_data = self.templates['barres'][bar_str]
            barre_data['_key'] = bar_str
            barre_data['type'] = 'barre'
            elements.append({
                'type': 'barre',
                'data': barre_data
            })

        return elements

    def get_note_elements_from_column(self, column_value, column_name):
        """Получение элементов нот из колонки с поиском в таблице NOTE - КЛЮЧЕВАЯ ФУНКЦИЯ!"""
        elements = []
        if self._is_empty_value(column_value):
            return elements

        # Преобразуем значение в строку
        note_str = self._convert_value_to_string(column_value)
        note_list = self._parse_note_values(note_str)

        for note_key in note_list:
            # Ищем в таблице NOTE
            element_found = self._find_element_in_note_table(note_key, column_name)
            if element_found:
                elements.append(element_found)

        return elements

    def _parse_note_values(self, note_str):
        """Парсит значения нот, обрабатывая специальные случаи с числами"""
        note_str = str(note_str).strip()

        # Сначала пробуем разделить по запятой (нормальный случай)
        if ',' in note_str:
            return [item.strip() for item in note_str.split(',') if item.strip()]

        # Если есть точка и выглядит как несколько чисел (например "21.25" вместо "21,25")
        if '.' in note_str:
            parts = note_str.split('.')
            # Проверяем, может ли это быть несколько целых чисел
            if len(parts) == 2 and all(part.isdigit() for part in parts):
                # Вероятно это "21,25" превратилось в "21.25"
                return [parts[0], parts[1]]
            elif len(parts) > 2 and all(part.isdigit() for part in parts):
                # Множественные числа через точку
                return parts

        # Если ничего не подошло, возвращаем как одно значение
        return [note_str]

    def _convert_value_to_string(self, value):
        """Конвертирует значение в строку, правильно обрабатывая числа с плавающей точкой"""
        if value is None:
            return ""

        if isinstance(value, float):
            # Если число выглядит как целое - преобразуем в int
            if value.is_integer():
                return str(int(value))
            else:
                # Для дробных чисел проверяем, не является ли это несколькими значениями
                str_value = str(value)
                if '.' in str_value:
                    parts = str_value.split('.')
                    # Если после точки 2 цифры и обе части выглядят как отдельные значения
                    if len(parts) == 2 and len(parts[1]) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        # Вероятно это "21,25" -> 21.25
                        return f"{parts[0]}.{parts[1]}"  # Оставляем как есть для дальнейшего парсинга
                return str(value)
        elif isinstance(value, int):
            return str(value)
        else:
            return str(value)

    def _find_element_in_note_table(self, note_key, column_name):
        """Поиск элемента в таблице NOTE по ключу и колонке - ВАЖНО!"""
        if not self.note_data:
            return self._find_element_in_json(note_key)

        # Определяем соответствие колонок как в оригинале
        column_mapping = {
            'FNL': ('FNL', 'FNL_ELEM'),
            'FN': ('FN', 'FN_ELEM'),
            'FPOL': ('FPOL', 'FPOL_ELEM'),
            'FPXL': ('FPXL', 'FPXL_ELEM'),
            'FP1': ('FP1', 'FP1_ELEM'),
            'FP2': ('FP2', 'FP2_ELEM'),
            'FP3': ('FP3', 'FP3_ELEM'),
            'FP4': ('FP4', 'FP4_ELEM')
        }

        if column_name not in column_mapping:
            return None

        source_col, elem_col = column_mapping[column_name]

        # Ищем в таблице NOTE
        for note_item in self.note_data:
            item_value = note_item.get(source_col)
            if item_value and not self._is_empty_value(item_value):
                # Конвертируем значение из таблицы для сравнения
                item_value_str = self._convert_value_to_string(item_value)

                # Пробуем разные варианты сравнения
                if self._values_match(item_value_str, note_key):
                    elem_value = note_item.get(elem_col)
                    if elem_value and not self._is_empty_value(elem_value):
                        elem_key = self._convert_value_to_string(elem_value)
                        return self._find_element_in_json(elem_key)

        return None

    def _values_match(self, value1, value2):
        """Проверяет, совпадают ли значения с учетом специальных случаев"""
        # Прямое сравнение
        if str(value1).strip() == str(value2).strip():
            return True

        # Если одно значение с точкой, а другое с запятой
        v1_clean = str(value1).replace('.', ',').strip()
        v2_clean = str(value2).replace('.', ',').strip()
        if v1_clean == v2_clean:
            return True

        # Если одно значение целое, а другое дробное с .0
        try:
            v1_float = float(value1)
            v2_float = float(value2)
            if abs(v1_float - v2_float) < 0.001:
                return True
        except (ValueError, TypeError):
            pass

        return False

    def _find_element_in_json(self, element_key):
        """Поиск элемента в различных разделах JSON"""
        element_key = element_key.strip()

        # Ищем в notes
        if element_key in self.templates.get('notes', {}):
            element_data = self.templates['notes'][element_key]
            element_data['_key'] = element_key
            element_data['type'] = 'note'
            return {
                'type': 'note',
                'data': element_data
            }

        # Ищем в open_notes
        if element_key in self.templates.get('open_notes', {}):
            element_data = self.templates['open_notes'][element_key]
            element_data['_key'] = element_key
            element_data['type'] = 'note'
            return {
                'type': 'note',
                'data': element_data
            }

        # Ищем в frets (лады)
        if element_key in self.templates.get('frets', {}):
            element_data = self.templates['frets'][element_key]
            element_data['_key'] = element_key
            element_data['type'] = 'fret'
            return {
                'type': 'fret',
                'data': element_data
            }

        return None

    def _is_empty_value(self, value):
        """Проверка на пустое значение"""
        if value is None:
            return True
        if isinstance(value, float) and pd.isna(value):
            return True
        if isinstance(value, str) and value.strip() == '':
            return True
        return False

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
        count = 0
        for i in range(1, 10):  # Проверяем до 9 вариантов
            variant_key = f"{chord_name}v{i}"
            if variant_key in self.chord_configs_cache:
                count += 1
            else:
                break
        return count if count > 0 else 1

    def get_base_image_path(self):
        return self.image_path


class SongsPage(BasePage):
    """Страница песен и аккордов с системой конфигураций из Excel"""

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
        self.current_variant = 1  # Текущий вариант аккорда

        # Настройки отображения аккордов
        self.current_display_type = "fingers"  # Начинаем с пальцев

        # Менеджер конфигураций аккордов
        self.config_manager = ChordConfigManager()
        self.load_configurations()

        # Проигрыватель звуков
        self.sound_player = ChordSoundPlayer()

        self.player = QMediaPlayer()
        self.player.error.connect(self.handle_error)

        self.initialize_page()

    def load_configurations(self):
        """Загрузка конфигураций с диагностикой"""
        print("🎵 Загрузка конфигураций аккордов из Excel...")
        success = self.config_manager.load_configurations()

        if success:
            print("✅ Конфигурации успешно загружены из Excel")
            print(f"📊 Создано конфигураций: {len(self.config_manager.chord_configs_cache)}")
            print(f"🖼️ Базовое изображение: {self.config_manager.get_base_image_path()}")

            # Покажем несколько примеров загруженных аккордов
            sample_chords = list(self.config_manager.chord_configs_cache.keys())[:10]
            print(f"🔍 Примеры аккордов: {sample_chords}")
        else:
            print("❌ Ошибка загрузки конфигураций из Excel")

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
        """Настройка UI с правильной пагинацией и настройками отображения"""
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

        # ПАНЕЛЬ УПРАВЛЕНИЯ ОТОБРАЖЕНИЕМ АККОРДОВ
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        control_layout.setAlignment(Qt.AlignCenter)
        control_layout.setSpacing(10)

        # Кнопка переключения ноты/пальцы
        self.display_toggle_btn = QPushButton("🎵")
        self.display_toggle_btn.setCheckable(True)
        self.display_toggle_btn.setChecked(False)
        self.display_toggle_btn.setFixedSize(50, 35)
        self.display_toggle_btn.clicked.connect(self.toggle_display_type)

        # Кнопка звука
        self.sound_btn = QPushButton("🔊")
        self.sound_btn.setFixedSize(50, 35)
        self.sound_btn.clicked.connect(self.play_chord_sound)

        control_layout.addWidget(self.display_toggle_btn)
        control_layout.addWidget(self.sound_btn)

        chord_info_layout.addWidget(control_widget)
        chords_layout_right.addWidget(chord_info_widget)

        self.chord_image_label = AdaptiveChordLabel()
        self.chord_image_label.clicked.connect(self.show_chord_large)
        self.chord_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chords_layout_right.addWidget(self.chord_image_label, 1)

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

        # Стили для кнопок управления
        self.display_toggle_btn.setStyleSheet("""
            QPushButton {
                background: rgba(52, 152, 219, 0.7);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:checked {
                background: rgba(231, 76, 60, 0.7);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:hover {
                background: rgba(52, 152, 219, 0.9);
            }
            QPushButton:checked:hover {
                background: rgba(231, 76, 60, 0.9);
            }
        """)

        self.sound_btn.setStyleSheet("""
            QPushButton {
                background: rgba(46, 204, 113, 0.7);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                background: rgba(46, 204, 113, 0.9);
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
        """Обработчик клика по аккорду в тексте песни"""
        try:
            chord_name = url.toString()
            self.current_chord_name = chord_name
            self.current_variant = 1  # Сбрасываем на первый вариант

            print(f"🎯 Клик по аккорду: {chord_name}")

            # Показываем информацию об аккорде
            self.chord_name_label.setText(f"Аккорд {chord_name}")
            chord_description = self.get_chord_description(chord_name)
            self.chord_description_label.setText(chord_description)

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

    def load_chord_from_config(self, chord_name):
        """Загрузка аккорда из конфигурации"""
        try:
            # Получаем количество вариантов динамически
            variants_count = self.config_manager.get_chord_variants_count(chord_name)
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
        """Генерация изображения аккорда из конфигурации"""
        try:
            # Получаем конфигурацию для конкретного варианта
            variant_key = f"{chord_name}v{variant}" if variant > 1 else chord_name
            chord_config = self.config_manager.get_chord_config(variant_key)

            if not chord_config:
                print(f"❌ Конфигурация не найдена для: {variant_key}")
                return QPixmap()

            # Получаем элементы для текущего типа отображения
            if self.current_display_type == "fingers":
                elements = chord_config['elements_fingers']
                print(f"👆 Используем элементы пальцев: {len(elements)}")
            else:
                elements = chord_config['elements_notes']
                print(f"🎵 Используем элементы нот: {len(elements)}")

            if not elements:
                print(f"❌ Нет элементов для аккорда {variant_key}")
                return QPixmap()

            # Применяем обводку
            elements = self.apply_outline_settings(elements)

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

            crop_x, crop_y, crop_width, crop_height = crop_rect

            # Проверяем границы
            crop_x = max(0, min(crop_x, original_pixmap.width() - 1))
            crop_y = max(0, min(crop_y, original_pixmap.height() - 1))
            crop_width = max(1, min(crop_width, original_pixmap.width() - crop_x))
            crop_height = max(1, min(crop_height, original_pixmap.height() - crop_y))

            # Создаем новое изображение размером с область обрезки с прозрачным фоном
            result_pixmap = QPixmap(crop_width, crop_height)
            result_pixmap.fill(Qt.transparent)  # Прозрачный фон

            painter = QPainter(result_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)

            # Копируем область из оригинального изображения
            painter.drawPixmap(0, 0, original_pixmap, crop_x, crop_y, crop_width, crop_height)

            # Рисуем элементы
            self.draw_elements_on_canvas(painter, elements, (crop_x, crop_y, crop_width, crop_height))
            painter.end()

            # Применяем масштаб "Маленький 1" как в оригинальном приложении
            display_width = min(400, crop_width)  # Авто-масштаб как в оригинале
            scale_factor = display_width / crop_width
            display_height = int(crop_height * scale_factor)

            scaled_pixmap = result_pixmap.scaled(
                display_width, display_height,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            return scaled_pixmap

        except Exception as e:
            print(f"❌ Ошибка генерации изображения для {chord_name} вариант {variant}: {e}")
            return QPixmap()

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
        """Рисование ноты на canvas"""
        try:
            adapted_data = self.adapt_coordinates(note_data, crop_rect)
            DrawingElements.draw_note(painter, adapted_data)
        except Exception as e:
            print(f"❌ Ошибка рисования ноты: {e}")

    def draw_barre_on_canvas(self, painter, barre_data, crop_rect):
        """Рисование баре на canvas с правильными координатами"""
        try:
            adapted_data = self.adapt_coordinates(barre_data, crop_rect)
            DrawingElements.draw_barre(painter, adapted_data)
        except Exception as e:
            print(f"❌ Ошибка рисования баре: {e}")

    def adapt_coordinates(self, element_data, crop_rect):
        """Точная копия адаптации координат из оригинального приложения"""
        if not crop_rect:
            return element_data.copy()

        # Копируем данные элемента
        adapted_data = element_data.copy()

        # Получаем координаты обрезки
        crop_x, crop_y, crop_width, crop_height = crop_rect

        original_x = element_data.get('x', 0)
        original_y = element_data.get('y', 0)

        # Для ВСЕХ элементов просто вычитаем координаты обрезки
        if 'x' in adapted_data:
            adapted_data['x'] = original_x - crop_x

        if 'y' in adapted_data:
            adapted_data['y'] = original_y - crop_y

        # Преобразуем в целые числа для Qt
        adapted_data['x'] = int(round(adapted_data.get('x', 0)))
        adapted_data['y'] = int(round(adapted_data.get('y', 0)))

        # Для баре - дополнительная коррекция координат (центр -> левый верхний угол)
        if adapted_data.get('type') == 'barre':
            barre_width = adapted_data.get('width', 100)
            barre_height = adapted_data.get('height', 20)

            if 'x' in adapted_data:
                adapted_data['x'] = adapted_data['x'] - (barre_width // 2)
            if 'y' in adapted_data:
                adapted_data['y'] = adapted_data['y'] - (barre_height // 2)

        return adapted_data

    def apply_outline_settings(self, elements):
        """Применение настроек обводки к элементам"""
        modified_elements = []
        for element in elements:
            if element['type'] == 'barre':
                # Средняя обводка для баре
                modified_element = element.copy()
                modified_element['data'] = element['data'].copy()
                modified_element['data']['outline_width'] = 4
                modified_element['data']['outline_color'] = [0, 0, 0]
                modified_elements.append(modified_element)
            elif element['type'] == 'note':
                # Толстая обводка для нот
                modified_element = element.copy()
                modified_element['data'] = element['data'].copy()
                modified_element['data']['outline_width'] = 6
                modified_element['data']['outline_color'] = [0, 0, 0]
                modified_elements.append(modified_element)
            else:
                modified_elements.append(element)

        return modified_elements

    def toggle_display_type(self):
        """Переключение между нотами и пальцами"""
        if self.display_toggle_btn.isChecked():
            self.current_display_type = "notes"
            self.display_toggle_btn.setText("👆")
        else:
            self.current_display_type = "fingers"
            self.display_toggle_btn.setText("🎵")

        self.refresh_current_chord()

    def refresh_current_chord(self):
        """Обновление отображения текущего аккорда"""
        if self.current_chord_name:
            print(f"🔄 Обновление аккорда: {self.current_chord_name}")
            self.refresh_chord_display(self.current_chord_name)

    def play_chord_sound(self):
        """Воспроизведение звука аккорда"""
        if not self.current_chord_name:
            return

        try:
            print(
                f"🔊 Попытка воспроизведения звука для аккорда: {self.current_chord_name}, вариант: {self.current_variant}")
            success = self.sound_player.play_chord_sound(self.current_chord_name, str(self.current_variant))

            if not success:
                # Если не нашли с вариантом, пробуем без варианта
                success = self.sound_player.play_chord_sound(self.current_chord_name)

            if not success:
                print(f"❌ Не удалось найти звуковой файл для аккорда {self.current_chord_name}")

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

                viewer = ChordViewerWindow(
                    self.current_chord_name,
                    temp_path,
                    "",  # Нет звука
                    self
                )
                viewer.exec_()

                # Удаляем временный файл
                os.unlink(temp_path)

        except Exception as e:
            print(f"Ошибка открытия окна аккорда: {e}")

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