# core/chord_manager.py
import os
import base64
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path

# Импортируем конвертированные данные
try:
    from data.chords_config import CHORDS_DATA, RAM_DATA, NOTE_DATA
    from data.template import TEMPLATE_DATA
    from data.template_guitar import GUITAR_IMAGE_DATA
    from data.chord_sounds import SOUNDS_DATA

    print("✅ Все модули данных успешно загружены")
except ImportError as e:
    print(f"❌ Ошибка импорта модулей данных: {e}")
    # Создаем заглушки для избежания ошибок
    CHORDS_DATA = []
    RAM_DATA = []
    NOTE_DATA = []
    TEMPLATE_DATA = {}
    GUITAR_IMAGE_DATA = ""
    SOUNDS_DATA = {}


class ChordManager:
    """Менеджер для работы с данными аккордов из конвертированных модулей"""

    _initialized = False
    _chords_cache = {}
    _template_image_path = None
    _temp_sounds_dir = None

    @classmethod
    def initialize(cls):
        """Инициализация менеджера аккордов"""
        if cls._initialized:
            return

        try:
            print("🎵 Инициализация менеджера аккордов...")

            # Создаем структуру аккордов из Excel данных
            cls._build_chords_cache()

            # Создаем временные файлы для ресурсов
            cls._create_temp_resources()

            cls._initialized = True
            print(f"✅ Менеджер аккордов инициализирован. Загружено {len(cls._chords_cache)} аккордов")

        except Exception as e:
            print(f"❌ Ошибка инициализации менеджера аккордов: {e}")
            import traceback
            traceback.print_exc()

    @classmethod
    def _build_chords_cache(cls):
        """Создание кэша аккордов из Excel данных"""
        cls._chords_cache = {}  # Очищаем кэш

        for chord_record in CHORDS_DATA:
            chord_name = chord_record["CHORD"]
            variant = chord_record["VARIANT"]

            # Нормализуем имя аккорда (обрабатываем варианты типа "B | H")
            normalized_names = cls._normalize_chord_name(chord_name)

            for name in normalized_names:
                if name not in cls._chords_cache:
                    cls._chords_cache[name] = {
                        'name': name,
                        'caption': chord_record["CAPTION"],
                        'type': chord_record["TYPE"],
                        'variants': []
                    }

                # Создаем вариант аккорда
                variant_data = cls._create_variant_data(chord_record)
                if variant_data:
                    # Убедимся, что варианты отсортированы по номеру
                    cls._chords_cache[name]['variants'].append(variant_data)
                    cls._chords_cache[name]['variants'].sort(key=lambda x: x['variant_number'])

    @classmethod
    def _normalize_chord_name(cls, chord_name: str) -> List[str]:
        """Нормализация имени аккорда (обработка вариантов типа 'B | H')"""
        if '|' in chord_name:
            return [name.strip() for name in chord_name.split('|')]
        return [chord_name.strip()]

    @classmethod
    def _create_variant_data(cls, chord_record: Dict) -> Optional[Dict]:
        """Создание данных варианта аккорда из записи Excel"""
        try:
            # Получаем элементы для отрисовки на основе FN кодов
            drawing_elements = cls._get_drawing_elements(chord_record)

            # Получаем область обрезки на основе RAM
            crop_rect = cls._get_crop_rect(chord_record.get("RAM"))

            # Получаем звуковые файлы (может быть пустым списком)
            sound_files = cls._get_sound_files(chord_record["CHORD"], chord_record["VARIANT"])

            return {
                'variant_number': chord_record["VARIANT"],
                'description': f"Вариант {chord_record['VARIANT']}",
                'ram': chord_record.get("RAM"),
                'barre': chord_record.get("BAR"),
                'crop_rect': crop_rect,
                'drawing_elements': drawing_elements,
                'sound_files': sound_files
            }

        except Exception as e:
            print(f"❌ Ошибка создания варианта для {chord_record['CHORD']} v{chord_record['VARIANT']}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def _get_drawing_elements(cls, chord_record: Dict) -> Dict[str, List]:
        """Получение элементов для отрисовки на основе FN кодов"""
        elements = {
            'frets': [],
            'notes': [],
            'open_notes': [],
            'barres': []
        }

        # Обрабатываем FN коды (ноты/пальцы)
        fn_codes = cls._parse_fn_codes(chord_record.get("FN"))
        for fn_code in fn_codes:
            element_data = cls._get_element_by_fn_code(fn_code)
            if element_data:
                elements['notes'].append(element_data)

        # Обрабатываем баре
        barre_data = cls._get_barre_element(chord_record.get("BAR"))
        if barre_data:
            elements['barres'].append(barre_data)

        # Обрабатываем открытые струны (FNL, FPXL, FPOL)
        open_notes = cls._get_open_notes(chord_record)
        elements['open_notes'].extend(open_notes)

        return elements

    @classmethod
    def _parse_fn_codes(cls, fn_value) -> List[str]:
        """Парсинг FN кодов из строки или числа"""
        if fn_value is None:
            return []

        if isinstance(fn_value, (int, float)):
            return [str(int(fn_value))]

        if isinstance(fn_value, str):
            # Обрабатываем строки типа "22,23,24" или "51,22,23,24"
            codes = []
            for part in fn_value.split(','):
                part = part.strip()
                if part and (part.isdigit() or ('.' in part and part.replace('.', '').isdigit())):
                    # Преобразуем в целое число, если это float
                    try:
                        codes.append(str(int(float(part))))
                    except ValueError:
                        codes.append(part)
            return codes

        return []

    @classmethod
    def _get_element_by_fn_code(cls, fn_code: str) -> Optional[Dict]:
        """Получение элемента отрисовки по FN коду"""
        try:
            # Ищем в NOTE_DATA по полю FN
            for note_record in NOTE_DATA:
                if note_record.get("FN") is not None:
                    record_fn = str(note_record.get("FN"))
                    if record_fn == fn_code:
                        element_id = note_record.get("FN_ELEM")
                        if element_id and element_id in TEMPLATE_DATA.get("notes", {}):
                            return {
                                'type': 'note',
                                'element_id': element_id,
                                'data': TEMPLATE_DATA["notes"][element_id]
                            }
        except Exception as e:
            print(f"❌ Ошибка получения элемента по FN коду {fn_code}: {e}")

        return None

    @classmethod
    def _get_barre_element(cls, barre_code: str) -> Optional[Dict]:
        """Получение элемента баре по коду"""
        if not barre_code or barre_code == "None":
            return None

        try:
            # Пример: "2BAR2-4" -> ищем "2BAR2-4" в шаблонах
            if barre_code in TEMPLATE_DATA.get("barres", {}):
                return {
                    'type': 'barre',
                    'element_id': barre_code,
                    'data': TEMPLATE_DATA["barres"][barre_code]
                }
        except Exception as e:
            print(f"❌ Ошибка получения баре элемента {barre_code}: {e}")

        return None

    @classmethod
    def _get_open_notes(cls, chord_record: Dict) -> List[Dict]:
        """Получение элементов открытых струн"""
        open_notes = []

        # Обрабатываем FNL (ноты на ладах)
        fnl_value = chord_record.get("FNL")
        if fnl_value is not None and fnl_value != "None":
            fnl_element = cls._find_note_element_by_value("FNL", fnl_value)
            if fnl_element:
                open_notes.append(fnl_element)

        # Обрабатываем FPXL (крестики)
        fpxl_value = chord_record.get("FPXL")
        if fpxl_value is not None and fpxl_value != "None":
            fpxl_element = cls._find_note_element_by_value("FPXL", fpxl_value)
            if fpxl_element:
                open_notes.append(fpxl_element)

        return open_notes

    @classmethod
    def _find_note_element_by_value(cls, field: str, value) -> Optional[Dict]:
        """Поиск элемента ноты по значению поля"""
        try:
            for note_record in NOTE_DATA:
                if note_record.get(field) == value:
                    element_id = note_record.get(f"{field}_ELEM")
                    if element_id:
                        if field == "FPXL" and element_id in TEMPLATE_DATA.get("open_notes", {}):
                            return {
                                'type': 'open_note',
                                'element_id': element_id,
                                'data': TEMPLATE_DATA["open_notes"][element_id]
                            }
                        elif element_id in TEMPLATE_DATA.get("notes", {}):
                            return {
                                'type': 'note',
                                'element_id': element_id,
                                'data': TEMPLATE_DATA["notes"][element_id]
                            }
        except Exception as e:
            print(f"❌ Ошибка поиска элемента по полю {field}: {e}")

        return None

    @classmethod
    def _get_crop_rect(cls, ram_code: str) -> Optional[Dict]:
        """Получение области обрезки по RAM коду"""
        if not ram_code or ram_code == "None":
            return None

        if ram_code in TEMPLATE_DATA.get("crop_rects", {}):
            return TEMPLATE_DATA["crop_rects"][ram_code]
        return None

    @classmethod
    def _get_sound_files(cls, chord_name: str, variant: int) -> List[str]:
        """Получение путей к звуковым файлам аккорда"""
        sound_files = []

        try:
            normalized_names = cls._normalize_chord_name(chord_name)

            for name in normalized_names:
                if name in SOUNDS_DATA:
                    chord_sounds = SOUNDS_DATA[name]
                    # Ищем звук для конкретного варианта
                    variant_key = f"{name}_{variant}"
                    if variant_key in chord_sounds:
                        sound_path = cls._get_sound_file_path(variant_key, chord_sounds[variant_key])
                        if sound_path:
                            sound_files.append(sound_path)

                    # Также добавляем общие звуки аккорда
                    for sound_key, sound_data in chord_sounds.items():
                        if sound_key != variant_key:  # Чтобы не дублировать
                            sound_path = cls._get_sound_file_path(sound_key, sound_data)
                            if sound_path and sound_path not in sound_files:
                                sound_files.append(sound_path)
        except Exception as e:
            print(f"❌ Ошибка получения звуковых файлов для {chord_name}: {e}")

        return sound_files

    @classmethod
    def _create_temp_resources(cls):
        """Создание временных файлов для ресурсов"""
        try:
            # Создаем временную директорию для звуков
            cls._temp_sounds_dir = tempfile.mkdtemp(prefix="guitar_chords_sounds_")
            print(f"✅ Создана временная директория для звуков: {cls._temp_sounds_dir}")

            # Создаем временный файл для изображения грифа
            cls._create_template_image_file()
        except Exception as e:
            print(f"❌ Ошибка создания временных ресурсов: {e}")

    @classmethod
    def _create_template_image_file(cls):
        """Создание временного файла для изображения грифа"""
        try:
            if GUITAR_IMAGE_DATA and GUITAR_IMAGE_DATA.strip():
                image_data = base64.b64decode(GUITAR_IMAGE_DATA.strip())
                temp_dir = tempfile.gettempdir()
                cls._template_image_path = os.path.join(temp_dir, "guitar_template.png")

                with open(cls._template_image_path, 'wb') as f:
                    f.write(image_data)

                print(f"✅ Создан временный файл изображения: {cls._template_image_path}")
            else:
                print("⚠️ Нет данных для создания изображения грифа")
        except Exception as e:
            print(f"❌ Ошибка создания временного файла изображения: {e}")

    @classmethod
    def _get_sound_file_path(cls, sound_key: str, sound_data: str) -> Optional[str]:
        """Получение пути к звуковому файлу (создает временный файл если нужно)"""
        try:
            if not sound_data or not isinstance(sound_data, str):
                return None

            sound_path = os.path.join(cls._temp_sounds_dir, f"{sound_key}.mp3")

            if not os.path.exists(sound_path):
                # Декодируем base64 и создаем файл
                sound_bytes = base64.b64decode(sound_data)
                with open(sound_path, 'wb') as f:
                    f.write(sound_bytes)

            return sound_path
        except Exception as e:
            print(f"❌ Ошибка создания звукового файла {sound_key}: {e}")
            return None

    # Публичные методы API
    @classmethod
    def is_initialized(cls) -> bool:
        return cls._initialized

    @classmethod
    def get_all_chords(cls) -> List[str]:
        return list(cls._chords_cache.keys())

    @classmethod
    def get_chord_data(cls, chord_name: str) -> Optional[Dict]:
        # Пробуем разные варианты написания
        names_to_try = [
            chord_name,
            chord_name.upper(),
            chord_name.upper().replace('M', 'm'),
            chord_name.upper().replace('М', 'm'),  # Кириллическая 'М'
            chord_name.strip()
        ]

        for name in names_to_try:
            if name in cls._chords_cache:
                return cls._chords_cache[name]

        print(f"❌ Аккорд '{chord_name}' не найден. Доступные: {list(cls._chords_cache.keys())}")
        return None

    @classmethod
    def get_chord_variants(cls, chord_name: str) -> List[Dict]:
        chord_data = cls.get_chord_data(chord_name)
        return chord_data.get('variants', []) if chord_data else []

    @classmethod
    def get_template_image_path(cls) -> Optional[str]:
        return cls._template_image_path

    @classmethod
    def search_chords(cls, query: str) -> List[str]:
        query_lower = query.lower()
        return [
            chord_name for chord_name in cls._chords_cache.keys()
            if query_lower in chord_name.lower()
        ]

    @classmethod
    def get_chord_config(cls, chord_name: str, variant: int = 1) -> Optional[Dict]:
        """Получение конфигурации конкретного варианта аккорда"""
        variants = cls.get_chord_variants(chord_name)
        for var in variants:
            if var.get('variant_number') == variant:
                return var
        return None

    @classmethod
    def cleanup(cls):
        """Очистка временных ресурсов"""
        try:
            if cls._temp_sounds_dir and os.path.exists(cls._temp_sounds_dir):
                import shutil
                shutil.rmtree(cls._temp_sounds_dir)
                print(f"✅ Удалена временная директория звуков: {cls._temp_sounds_dir}")

            if cls._template_image_path and os.path.exists(cls._template_image_path):
                os.remove(cls._template_image_path)
                print(f"✅ Удален временный файл изображения: {cls._template_image_path}")

        except Exception as e:
            print(f"❌ Ошибка очистки временных ресурсов: {e}")


# Автоматическая инициализация при импорте
ChordManager.initialize()