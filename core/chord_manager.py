# core/chord_manager.py
import os
import base64
import tempfile
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice, Qt
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

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


class ChordSoundPlayer:
    """Класс для воспроизведения звуков аккордов с кэшированием временных файлов"""

    # Словарь для кэширования путей к временным файлам
    _sound_cache = {}
    _temp_dir = None

    @staticmethod
    def initialize():
        """Инициализация звукового плеера"""
        try:
            # Создаем временную директорию для звуков
            ChordSoundPlayer._temp_dir = tempfile.mkdtemp(prefix="guitar_chords_sounds_")
            print(f"✅ Создана временная директория для звуков: {ChordSoundPlayer._temp_dir}")
        except Exception as e:
            print(f"❌ Ошибка инициализации звукового плеера: {e}")

    @staticmethod
    def play_chord_sound(player: QMediaPlayer, chord_name: str, variant: int = 1) -> bool:
        """Воспроизведение звука аккорда"""
        try:
            print(f"🔊 Попытка воспроизведения звука для аккорда: {chord_name}, вариант: {variant}")

            normalized_names = ChordManager._normalize_chord_name(chord_name)

            for name in normalized_names:
                if name in SOUNDS_DATA:
                    chord_sounds = SOUNDS_DATA[name]

                    # Ищем звук для конкретного варианта
                    variant_key = f"{name}_{variant}"
                    if variant_key in chord_sounds:
                        sound_data = chord_sounds[variant_key]
                        if ChordManager._is_valid_sound_data(sound_data):
                            return ChordSoundPlayer._play_cached_sound(player, sound_data, variant_key)

                    # Также ищем общие звуки аккорда
                    for sound_key, sound_data in chord_sounds.items():
                        if ChordManager._is_valid_sound_data(sound_data):
                            return ChordSoundPlayer._play_cached_sound(player, sound_data, sound_key)

            print(f"🔇 Звук для аккорда {chord_name} вариант {variant} не найден")
            return False

        except Exception as e:
            print(f"❌ Ошибка воспроизведения звука для {chord_name}: {e}")
            return False

    @staticmethod
    def _play_cached_sound(player: QMediaPlayer, base64_data: str, sound_key: str) -> bool:
        """Воспроизведение звука с кэшированием временного файла"""
        try:
            # Проверяем кэш
            if sound_key in ChordSoundPlayer._sound_cache:
                sound_path = ChordSoundPlayer._sound_cache[sound_key]
                if os.path.exists(sound_path):
                    print(f"🔊 Используем кэшированный файл для: {sound_key}")
                    return ChordSoundPlayer._play_from_file(player, sound_path, sound_key)
                else:
                    # Файл был удален, удаляем из кэша
                    del ChordSoundPlayer._sound_cache[sound_key]

            # Создаем временный файл
            sound_path = ChordSoundPlayer._create_temp_sound_file(base64_data, sound_key)
            if not sound_path:
                return False

            # Сохраняем в кэш
            ChordSoundPlayer._sound_cache[sound_key] = sound_path

            # Воспроизводим
            return ChordSoundPlayer._play_from_file(player, sound_path, sound_key)

        except Exception as e:
            print(f"❌ Ошибка воспроизведения кэшированного звука {sound_key}: {e}")
            return False

    @staticmethod
    def _create_temp_sound_file(base64_data: str, sound_key: str) -> Optional[str]:
        """Создание временного звукового файла"""
        try:
            if not ChordSoundPlayer._temp_dir:
                ChordSoundPlayer.initialize()

            # Декодируем base64
            sound_bytes = base64.b64decode(base64_data.strip())
            if len(sound_bytes) == 0:
                print(f"⚠️ Пустой звук после декодирования для {sound_key}")
                return None

            # Создаем путь к файлу
            sound_path = os.path.join(ChordSoundPlayer._temp_dir, f"{sound_key}.mp3")

            # Записываем данные в файл
            with open(sound_path, 'wb') as f:
                f.write(sound_bytes)

            print(f"✅ Создан временный файл: {sound_key} ({len(sound_bytes)} байт)")
            return sound_path

        except Exception as e:
            print(f"❌ Ошибка создания временного файла для {sound_key}: {e}")
            return None

    @staticmethod
    def _play_from_file(player: QMediaPlayer, sound_path: str, sound_key: str) -> bool:
        """Воспроизведение звука из файла"""
        try:
            # Создаем медиа-контент из файла
            from PyQt5.QtCore import QUrl
            media_content = QMediaContent(QUrl.fromLocalFile(sound_path))

            # Устанавливаем медиа и воспроизводим
            player.setMedia(media_content)
            player.play()

            print(f"🔊 Воспроизведение: {sound_key}")
            return True

        except Exception as e:
            print(f"❌ Ошибка воспроизведения файла {sound_key}: {e}")
            return False

    @staticmethod
    def has_sound(chord_name: str, variant: int = 1) -> bool:
        """Проверка наличия звука для аккорда"""
        try:
            normalized_names = ChordManager._normalize_chord_name(chord_name)

            for name in normalized_names:
                if name in SOUNDS_DATA:
                    chord_sounds = SOUNDS_DATA[name]

                    # Ищем звук для конкретного варианта
                    variant_key = f"{name}_{variant}"
                    if variant_key in chord_sounds:
                        if ChordManager._is_valid_sound_data(chord_sounds[variant_key]):
                            return True

                    # Также ищем общие звуки аккорда
                    for sound_data in chord_sounds.values():
                        if ChordManager._is_valid_sound_data(sound_data):
                            return True

            return False

        except Exception as e:
            print(f"❌ Ошибка проверки звука для {chord_name}: {e}")
            return False

    @staticmethod
    def cleanup():
        """Очистка временных файлов"""
        try:
            # Удаляем временные файлы
            if ChordSoundPlayer._temp_dir and os.path.exists(ChordSoundPlayer._temp_dir):
                import shutil
                shutil.rmtree(ChordSoundPlayer._temp_dir)
                print(f"✅ Удалена временная директория звуков: {ChordSoundPlayer._temp_dir}")

            # Очищаем кэш
            ChordSoundPlayer._sound_cache.clear()
            ChordSoundPlayer._temp_dir = None

        except Exception as e:
            print(f"❌ Ошибка очистки временных звуковых файлов: {e}")


class ChordManager:
    """Менеджер для работы с данными аккордов из конвертированных модулей"""

    _initialized = False
    _chords_cache = {}
    _template_image_path = None

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
            print(f"\n🎸 СОЗДАНИЕ ВАРИАНТА ДЛЯ {chord_record['CHORD']} вариант {chord_record['VARIANT']}")

            # Получаем элементы для ОБОИХ типов отображения
            drawing_elements_fingers = cls._get_drawing_elements(chord_record, "fingers")
            drawing_elements_notes = cls._get_drawing_elements(chord_record, "notes")

            # Получаем область обрезки на основе RAM
            crop_rect = cls._get_crop_rect(chord_record.get("RAM"))

            variant_data = {
                'variant_number': chord_record["VARIANT"],
                'description': f"Вариант {chord_record['VARIANT']}",
                'ram': chord_record.get("RAM"),
                'barre': chord_record.get("BAR"),
                'crop_rect': crop_rect,
                'drawing_elements_fingers': drawing_elements_fingers,
                'drawing_elements_notes': drawing_elements_notes
            }

            print(f"✅ Вариант {chord_record['VARIANT']} создан:")
            print(f"   👆 Пальцы: {len(drawing_elements_fingers.get('notes', []))} нот, "
                  f"{len(drawing_elements_fingers.get('open_notes', []))} открытых")
            print(f"   🎵 Ноты: {len(drawing_elements_notes.get('notes', []))} нот, "
                  f"{len(drawing_elements_notes.get('open_notes', []))} открытых")

            return variant_data

        except Exception as e:
            print(f"❌ Ошибка создания варианта для {chord_record['CHORD']} v{chord_record['VARIANT']}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def _get_drawing_elements(cls, chord_record: Dict, display_type: str = "fingers") -> Dict[str, List]:
        """Получение элементов для отрисовки на основе типа отображения (пальцы/ноты)"""
        elements = {
            'frets': [],
            'notes': [],
            'open_notes': [],
            'barres': []
        }

        print(f"\n🎸 СБОРКА ЭЛЕМЕНТОВ ДЛЯ {chord_record['CHORD']} вариант {chord_record['VARIANT']} ({display_type})")

        # Добавляем лады на основе RAM
        ram_code = chord_record.get("RAM")
        if ram_code and ram_code != "None":
            frets = cls._get_frets_for_ram(ram_code)
            elements['frets'] = frets
            print(f"🎻 Добавлены лады для {ram_code}: {[f['data'].get('symbol') for f in frets]}")

        # Добавляем баре (одинаково для обоих режимов)
        barre_data = cls._get_barre_element(chord_record.get("BAR"))
        if barre_data:
            elements['barres'].append(barre_data)
            print(f"🎸 Добавлено баре: {chord_record.get('BAR')}")

        if display_type == "fingers":
            # РЕЖИМ ПАЛЬЦЕВ
            print("👆 РЕЖИМ ПАЛЬЦЕВ:")

            # Обрабатываем FPOL (открытые струны - кружки)
            fnl_value = chord_record.get("FPOL")
            if fnl_value is not None and fnl_value != "None":
                print(f"  🎯 FPOL: {fnl_value}")
                fnl_elements = cls._parse_fp_fields(fnl_value, "FPOL")
                elements['open_notes'].extend(fnl_elements)

            # Обрабатываем FPXL (крестики - заглушенные струны)
            fpxl_value = chord_record.get("FPXL")
            if fpxl_value is not None and fpxl_value != "None":
                print(f"  🎯 FPXL: {fpxl_value}")
                fpxl_elements = cls._parse_fp_fields(fpxl_value, "FPXL")
                elements['open_notes'].extend(fpxl_elements)

            # Обрабатываем FP1-FP4 (пальцы)
            finger_notes = []
            for fp_field in ["FP1", "FP2", "FP3", "FP4"]:
                fp_value = chord_record.get(fp_field)
                if fp_value is not None and fp_value != "None":
                    print(f"  🎯 {fp_field}: {fp_value}")
                    fp_elements = cls._parse_fp_fields(fp_value, fp_field)
                    for element in fp_elements:
                        # Для пальцев устанавливаем отображение пальца
                        if element['type'] == 'note':
                            element['data']['display_text'] = 'finger'
                            # Устанавливаем номер пальца из названия поля
                            finger_number = fp_field.replace("FP", "")
                            element['data']['finger'] = finger_number
                            finger_notes.append(element)

            elements['notes'].extend(finger_notes)
            print(f"  👆 Добавлено пальцев: {len(finger_notes)}")

        else:
            # РЕЖИМ НОТ
            print("🎵 РЕЖИМ НОТ:")

            # Обрабатываем FNL (ноты на ладах - открытые струны)
            fnl_value = chord_record.get("FNL")
            if fnl_value is not None and fnl_value != "None":
                print(f"  🎯 FNL: {fnl_value}")
                fnl_elements = cls._parse_fp_fields(fnl_value, "FNL")
                for element in fnl_elements:
                    if element['type'] == 'note':
                        # Для нот устанавливаем отображение имени ноты
                        element['data']['display_text'] = 'note_name'
                        elements['notes'].append(element)

            # Обрабатываем FN коды (основные ноты)
            fn_codes = cls._parse_fn_codes(chord_record.get("FN"))
            print(f"  📋 FN коды: {fn_codes}")

            for fn_code in fn_codes:
                element_data = cls._get_element_by_fn_code(fn_code)
                if element_data:
                    # Для нот устанавливаем отображение имени ноты
                    element_data['data']['display_text'] = 'note_name'
                    elements['notes'].append(element_data)
                    print(f"  ✅ Добавлена нота из FN{fn_code}")

        print(f"🎉 ИТОГО элементов для {display_type}:")
        print(f"   🎵 Ноты: {len(elements['notes'])}")
        print(f"   🔘 Открытые: {len(elements['open_notes'])}")
        print(f"   🎸 Баре: {len(elements['barres'])}")
        print(f"   🎻 Лады: {len(elements['frets'])}")

        return elements

    @classmethod
    def _get_frets_for_ram(cls, ram_code: str) -> List[Dict]:
        """Получение ладов для указанного RAM кода"""
        frets = []

        try:
            # Ищем RAM в данных
            for ram_record in RAM_DATA:
                if ram_record["RAM"] == ram_code:
                    lad_numbers = ram_record.get("LAD", [])
                    print(f"  🎻 Найдены лады для {ram_code}: {lad_numbers}")

                    for lad_num in lad_numbers:
                        # Ищем элемент лада в шаблонах
                        lad_id = f"{lad_num}LAD"
                        if lad_id in TEMPLATE_DATA.get("frets", {}):
                            fret_data = TEMPLATE_DATA["frets"][lad_id].copy()
                            frets.append({
                                'type': 'fret',
                                'element_id': lad_id,
                                'data': fret_data
                            })
                            print(f"    ✅ Добавлен лад {lad_num}")
                        else:
                            print(f"    ⚠️  Лад {lad_id} не найден в шаблонах")
                    break
            else:
                print(f"    ❌ RAM код {ram_code} не найден в RAM_DATA")

        except Exception as e:
            print(f"❌ Ошибка получения ладов для {ram_code}: {e}")

        return frets

    @classmethod
    def _parse_fn_codes(cls, fn_value) -> List[str]:
        """Парсинг FN кодов из строки, числа или списка"""
        if fn_value is None:
            return []

        # Если это список
        if isinstance(fn_value, list):
            return [str(int(item)) for item in fn_value if item is not None]

        # Если это число
        if isinstance(fn_value, (int, float)):
            return [str(int(fn_value))]

        # Если это строка
        if isinstance(fn_value, str):
            if fn_value == "None" or not fn_value.strip():
                return []
            # Обрабатываем строки типа "22,23,24" или "51,22,23,24"
            codes = []
            for part in fn_value.split(','):
                part = part.strip()
                if part and (part.isdigit() or ('.' in part and part.replace('.', '').isdigit())):
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
                            element_data = TEMPLATE_DATA["notes"][element_id].copy()
                            # Сохраняем оригинальные настройки отображения
                            return {
                                'type': 'note',
                                'element_id': element_id,
                                'data': element_data
                            }
            print(f"    ⚠️  Элемент не найден для FN кода: {fn_code}")
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
            else:
                print(f"    ⚠️  Баре элемент не найден: {barre_code}")
        except Exception as e:
            print(f"❌ Ошибка получения баре элемента {barre_code}: {e}")

        return None

    @classmethod
    def _get_open_notes(cls, chord_record: Dict) -> List[Dict]:
        """Получение элементов открытых струн с новыми полями FPOL, FPXL, FP1-FP4"""
        open_notes = []

        print(f"🔍 Анализ открытых струн для аккорда {chord_record['CHORD']} вариант {chord_record['VARIANT']}")

        # Обрабатываем FPOL (открытые струны - кружки)
        fnl_value = chord_record.get("FPOL")
        if fnl_value is not None and fnl_value != "None":
            print(f"  🎯 FPOL: {fnl_value}")
            fnl_elements = cls._parse_fp_fields(fnl_value, "FPOL")
            open_notes.extend(fnl_elements)

        # Обрабатываем FPXL (крестики - заглушенные струны)
        fpxl_value = chord_record.get("FPXL")
        if fpxl_value is not None and fpxl_value != "None":
            print(f"  🎯 FPXL: {fpxl_value}")
            fpxl_elements = cls._parse_fp_fields(fpxl_value, "FPXL")
            open_notes.extend(fpxl_elements)

        # Обрабатываем FP1-FP4 (пальцы)
        for fp_field in ["FP1", "FP2", "FP3", "FP4"]:
            fp_value = chord_record.get(fp_field)
            if fp_value is not None and fp_value != "None":
                print(f"  🎯 {fp_field}: {fp_value}")
                fp_elements = cls._parse_fp_fields(fp_value, fp_field)
                open_notes.extend(fp_elements)

        print(f"  ✅ Найдено открытых струн: {len(open_notes)}")
        return open_notes

    @classmethod
    def _parse_fp_fields(cls, fp_value, field_name: str) -> List[Dict]:
        """Парсинг полей FP* (FPOL, FPXL, FP1-FP4)"""
        elements = []

        # Парсим значения (может быть число, список или строка)
        fp_codes = cls._parse_fn_codes(fp_value)

        print(f"    📊 Парсинг {field_name}: {fp_value} -> коды: {fp_codes}")

        for fp_code in fp_codes:
            element_data = cls._find_note_element_by_value(field_name, fp_code)
            if element_data:
                print(f"    ✅ Найден элемент для {field_name}_{fp_code}")
                elements.append(element_data)
            else:
                print(f"    ❌ Элемент не найден для {field_name}_{fp_code}")

        return elements

    @classmethod
    def _find_note_element_by_value(cls, field: str, value) -> Optional[Dict]:
        """Поиск элемента ноты по значению поля с улучшенной логикой"""
        try:
            print(f"    🔎 Поиск элемента: поле={field}, значение={value}")

            for note_record in NOTE_DATA:
                record_value = note_record.get(field)

                # Обрабатываем разные типы данных
                if record_value is None:
                    continue

                # Если в записи список - проверяем вхождение
                if isinstance(record_value, list):
                    if value in [str(item) for item in record_value if item is not None]:
                        element_id = note_record.get(f"{field}_ELEM")
                        return cls._create_element_from_template(field, element_id, value)

                # Если в записи число или строка
                elif str(record_value) == str(value):
                    element_id = note_record.get(f"{field}_ELEM")
                    return cls._create_element_from_template(field, element_id, value)

            print(f"    ⚠️  Элемент не найден в NOTE_DATA для {field}={value}")
            return None

        except Exception as e:
            print(f"    ❌ Ошибка поиска элемента по полю {field}: {e}")
            return None

    @classmethod
    def _create_element_from_template(cls, field: str, element_id: str, value: str) -> Optional[Dict]:
        """Создание элемента из шаблона на основе поля и ID"""
        if not element_id:
            return None

        try:
            print(f"      🎨 Создание элемента: {element_id} для {field}")

            # Определяем тип элемента на основе поля
            if field == "FPXL":
                # Крестики - открытые ноты с символом X
                if element_id in TEMPLATE_DATA.get("open_notes", {}):
                    element_data = TEMPLATE_DATA["open_notes"][element_id].copy()
                    # Убедимся, что отображается символ X
                    element_data['display_text'] = 'symbol'
                    element_data['symbol'] = 'X'
                    return {
                        'type': 'open_note',
                        'element_id': element_id,
                        'data': element_data
                    }

            elif field == "FPOL":
                # Открытые струны - кружки
                if element_id in TEMPLATE_DATA.get("open_notes", {}):
                    element_data = TEMPLATE_DATA["open_notes"][element_id].copy()
                    # Для открытых струн может быть символ O или пусто
                    element_data['display_text'] = 'symbol'
                    element_data['symbol'] = element_data.get('symbol', 'O')
                    return {
                        'type': 'open_note',
                        'element_id': element_id,
                        'data': element_data
                    }

            elif field in ["FP1", "FP2", "FP3", "FP4"]:
                # Пальцы - обычные ноты
                if element_id in TEMPLATE_DATA.get("notes", {}):
                    element_data = TEMPLATE_DATA["notes"][element_id].copy()
                    # Устанавливаем номер пальца из названия поля
                    finger_number = field.replace("FP", "")
                    element_data['finger'] = finger_number
                    element_data['display_text'] = 'finger'
                    return {
                        'type': 'note',
                        'element_id': element_id,
                        'data': element_data
                    }

            elif field == "FNL":
                # Ноты на ладах
                if element_id in TEMPLATE_DATA.get("notes", {}):
                    element_data = TEMPLATE_DATA["notes"][element_id].copy()
                    # Используем оригинальные настройки отображения
                    return {
                        'type': 'note',
                        'element_id': element_id,
                        'data': element_data
                    }

            print(f"      ⚠️  Элемент {element_id} не найден в шаблонах для поля {field}")
            return None

        except Exception as e:
            print(f"      ❌ Ошибка создания элемента {element_id}: {e}")
            return None

    @classmethod
    def _get_crop_rect(cls, ram_code: str) -> Optional[Dict]:
        """Получение области обрезки по RAM коду"""
        if not ram_code or ram_code == "None":
            return None

        if ram_code in TEMPLATE_DATA.get("crop_rects", {}):
            return TEMPLATE_DATA["crop_rects"][ram_code]

        print(f"    ⚠️  Область обрезки не найдена: {ram_code}")
        return None

    @classmethod
    def _create_temp_resources(cls):
        """Создание временных файлов для ресурсов"""
        try:
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
    def _is_valid_sound_data(cls, sound_data) -> bool:
        """Проверка валидности звуковых данных"""
        if not sound_data:
            return False

        if not isinstance(sound_data, str):
            return False

        if not sound_data.strip():
            return False

        # Проверяем, что это похоже на base64
        import re
        base64_pattern = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
        return base64_pattern.match(sound_data) is not None

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
    def get_crop_rect(cls, chord_name: str, variant: int = 1) -> Optional[tuple]:
        """Получение области обрезки в виде кортежа (x, y, width, height)"""
        chord_config = cls.get_chord_config(chord_name, variant)
        if not chord_config:
            return None

        crop_rect = chord_config.get('crop_rect')
        if not crop_rect:
            return None

        try:
            # Преобразуем словарь в кортеж
            x = crop_rect.get('x', 0)
            y = crop_rect.get('y', 0)
            width = crop_rect.get('width', 0)
            height = crop_rect.get('height', 0)

            return (x, y, width, height)
        except Exception as e:
            print(f"❌ Ошибка преобразования crop_rect для {chord_name}: {e}")
            return None

    @classmethod
    def has_sound(cls, chord_name: str, variant: int = 1) -> bool:
        """Проверка наличия звука для аккорда (прокси метод)"""
        return ChordSoundPlayer.has_sound(chord_name, variant)

    @classmethod
    def debug_chord_structure(cls, chord_name: str, variant: int = 1):
        """Отладка структуры аккорда"""
        print(f"\n{'=' * 80}")
        print(f"🔍 ДЕТАЛЬНЫЙ АНАЛИЗ АККОРДА: {chord_name} вариант {variant}")
        print(f"{'=' * 80}")

        # Находим запись аккорда
        chord_record = None
        for record in CHORDS_DATA:
            if record["CHORD"] == chord_name and record["VARIANT"] == variant:
                chord_record = record
                break

        if not chord_record:
            print(f"❌ Аккорд {chord_name} вариант {variant} не найден")
            return

        print(f"📊 СЫРЫЕ ДАННЫЕ ИЗ CHORDS_DATA:")
        for key, value in chord_record.items():
            print(f"   {key}: {value} ({type(value).__name__})")

        # Анализируем элементы для пальцев
        print(f"\n👆 ЭЛЕМЕНТЫ ДЛЯ ПАЛЬЦЕВ:")
        drawing_elements_fingers = cls._get_drawing_elements(chord_record, "fingers")
        for element_type, elements_list in drawing_elements_fingers.items():
            print(f"\n📋 {element_type.upper()} ({len(elements_list)}):")
            for i, element in enumerate(elements_list):
                print(f"   {i + 1}. ID: {element.get('element_id')}")
                print(f"      Данные: {json.dumps(element.get('data'), indent=6, ensure_ascii=False)}")

        # Анализируем элементы для нот
        print(f"\n🎵 ЭЛЕМЕНТЫ ДЛЯ НОТ:")
        drawing_elements_notes = cls._get_drawing_elements(chord_record, "notes")
        for element_type, elements_list in drawing_elements_notes.items():
            print(f"\n📋 {element_type.upper()} ({len(elements_list)}):")
            for i, element in enumerate(elements_list):
                print(f"   {i + 1}. ID: {element.get('element_id')}")
                print(f"      Данные: {json.dumps(element.get('data'), indent=6, ensure_ascii=False)}")

    @classmethod
    def cleanup(cls):
        """Очистка временных ресурсов"""
        try:
            if cls._template_image_path and os.path.exists(cls._template_image_path):
                os.remove(cls._template_image_path)
                print(f"✅ Удален временный файл изображения: {cls._template_image_path}")

            # Очищаем звуковые файлы
            ChordSoundPlayer.cleanup()

        except Exception as e:
            print(f"❌ Ошибка очистки временных ресурсов: {e}")


# Автоматическая инициализация при импорте
ChordManager.initialize()