import base64
import tempfile
import os
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QBuffer, QIODevice
import io
import json



try:
    from data.chords_data import CHORDS_DATA  # ⬅️ ПРЯМОЙ ИМПОРТ ДАННЫХ

    CHORD_DATA_AVAILABLE = True
    print(f"✅ Данные аккордов загружены. Аккордов: {len(CHORDS_DATA.get('chords', {}))}")
    print(f"✅ Шаблон: {'есть' if CHORDS_DATA.get('template_image') else 'нет'}")
    print(f"✅ JSON конфигурация: {'есть' if CHORDS_DATA.get('original_json_config') else 'нет'}")

    # Отладочная информация
    print("🔍 Проверка конкретных аккордов:")
    test_chords = ['A', 'B', 'C', 'G', 'D', 'Am', 'Em', 'D6']
    chords_dict = CHORDS_DATA.get('chords', {})
    for chord in test_chords:
        exists = chord in chords_dict
        status = "✅" if exists else "❌"
        print(f"   {status} {chord}: {'найден' if exists else 'не найден'}")

except ImportError as e:
    print(f"⚠️ Не удалось загрузить данные аккордов: {e}")
    CHORD_DATA_AVAILABLE = False
    CHORDS_DATA = {}

# Импорт для генерации изображений
try:
    from PIL import Image, ImageDraw

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("❌ Pillow не установлен! Установите: pip install Pillow")

try:
    from drawing_elements import draw_chord_elements

    HAS_DRAWING = True
except ImportError as e:
    HAS_DRAWING = False
    print(f"❌ Модуль drawing_elements не найден: {e}")


class ChordData:
    """Класс-обертка для работы с данными аккордов"""

    @classmethod
    def get_chord_data(cls, chord_name):
        """Получить данные аккорда по имени"""
        chords_dict = CHORDS_DATA.get('chords', {})

        # Пробуем разные варианты написания
        names_to_try = [
            chord_name,
            chord_name.upper(),
            chord_name.upper().replace('M', '').replace('М', ''),
            chord_name.upper().replace('M', 'm').replace('М', 'm'),
            chord_name.upper().replace('6', '').replace('7', '').replace('9', ''),
        ]

        for name in names_to_try:
            if name in chords_dict:
                print(f"✅ Аккорд '{chord_name}' найден как '{name}'")
                return chords_dict[name]

        # Если не нашли, выводим отладочную информацию
        available_chords = list(chords_dict.keys())
        print(f"❌ Аккорд '{chord_name}' не найден в данных")
        if available_chords:
            print(f"   Доступные аккорды: {', '.join(sorted(available_chords)[:10])}...")
        return None

    @classmethod
    def get_all_chords(cls):
        """Получить список всех доступных аккордов"""
        return list(CHORDS_DATA.get('chords', {}).keys())

    @classmethod
    def get_chords_by_folder(cls, folder_num):
        """Получить аккорды из указанной папки"""
        folder_name = f'group_{folder_num}'
        chords_dict = CHORDS_DATA.get('chords', {})
        return [chord for chord, data in chords_dict.items()
                if data.get('folder') == folder_name]

    @classmethod
    def get_chord_description(cls, chord_name):
        """Получить описание аккорда"""
        chord_data = cls.get_chord_data(chord_name)
        if chord_data:
            return chord_data.get('description', f'Аккорд {chord_name}')
        return f'Аккорд {chord_name}'

    @classmethod
    def is_data_available(cls):
        """Проверка доступности данных"""
        return CHORD_DATA_AVAILABLE and len(CHORDS_DATA.get('chords', {})) > 0

    @classmethod
    def get_template_image(cls):
        """Получить шаблон изображения"""
        return CHORDS_DATA.get('template_image')

    @classmethod
    def get_display_types(cls):
        """Получить доступные типы отображения"""
        return ["fingers", "notes"]

    @classmethod
    def get_original_json_config(cls):
        """Получить оригинальную JSON конфигурацию"""
        return CHORDS_DATA.get('original_json_config', {})

    @classmethod
    def get_stats(cls):
        """Получить статистику данных"""
        chords_dict = CHORDS_DATA.get('chords', {})
        metadata = CHORDS_DATA.get('metadata', {})

        return {
            'total_chords': len(chords_dict),
            'template_size_kb': metadata.get('template_size', 0) / 1024,
            'has_template': bool(CHORDS_DATA.get('template_image')),
            'has_json_config': bool(CHORDS_DATA.get('original_json_config')),
            'converter_version': metadata.get('converter_version', 'unknown')
        }


class ChordManager:
    """Управляет оптимизированными данными аккордов с генерацией изображений из JSON"""

    def __init__(self):
        self.temp_files = []
        self.base_image = None
        self._setup_temp_dir()
        self.load_template_image()

        if not ChordData.is_data_available():
            print("❌ Данные аккордов не загружены! Запустите конвертер.")
        else:
            stats = ChordData.get_stats()
            print(f"✅ Данные аккордов загружены:")
            print(f"   🎸 Аккордов: {stats['total_chords']}")
            print(f"   🖼️  Шаблон: {stats['template_size_kb']:.1f} KB")
            print(f"   📋 JSON конфигурация: {'есть' if stats['has_json_config'] else 'нет'}")

    def _setup_temp_dir(self):
        """Создает временную директорию для файлов"""
        self.temp_dir = tempfile.mkdtemp(prefix="guitar_chords_")

    def load_template_image(self):
        """Загружает шаблон изображения из данных"""
        if not HAS_PILLOW:
            print("❌ Pillow не доступен, изображения не будут генерироваться")
            return

        template_b64 = ChordData.get_template_image()
        if not template_b64:
            print("❌ Шаблон изображения не найден в данных")
            return

        try:
            template_data = base64.b64decode(template_b64)
            self.base_image = Image.open(io.BytesIO(template_data))
            print(f"✅ Шаблон изображения загружен: {self.base_image.size}")
        except Exception as e:
            print(f"❌ Ошибка загрузки шаблона: {e}")

    def process_crop_rect(self, crop_rect):
        """Обрабатывает crop_rect"""
        if isinstance(crop_rect, list) and len(crop_rect) == 4:
            return {
                'x': crop_rect[0],
                'y': crop_rect[1],
                'width': crop_rect[2],
                'height': crop_rect[3]
            }
        elif isinstance(crop_rect, dict):
            return crop_rect
        else:
            return {'x': 0, 'y': 0, 'width': 400, 'height': 200}

    def generate_chord_image(self, json_parameters, display_type="fingers"):
        """Генерирует изображение аккорда из JSON параметров"""
        print(f"🎨 Генерация изображения, тип: {display_type}")
        print(f"📐 Размер шаблона: {self.base_image.size if self.base_image else 'нет'}")
        print(f"📋 Параметры: {list(json_parameters.keys())}")
        if not self.base_image or not HAS_DRAWING:
            print("❌ Не могу сгенерировать изображение: нет шаблона или drawing_elements")
            return None

        try:
            # Обрабатываем crop_rect
            crop_rect_data = self.process_crop_rect(json_parameters.get('crop_rect', []))
            crop_x = crop_rect_data.get('x', 0)
            crop_y = crop_rect_data.get('y', 0)
            crop_width = crop_rect_data.get('width', 400)
            crop_height = crop_rect_data.get('height', 200)

            # Проверяем границы обрезки
            img_width, img_height = self.base_image.size
            crop_x = max(0, min(crop_x, img_width - 1))
            crop_y = max(0, min(crop_y, img_height - 1))
            crop_width = max(1, min(crop_width, img_width - crop_x))
            crop_height = max(1, min(crop_height, img_height - crop_y))

            print(f"📐 Обрезка: ({crop_x}, {crop_y}, {crop_width}, {crop_height}) из {img_width}x{img_height}")

            # Обрезаем изображение
            cropped_image = self.base_image.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))
            chord_image = cropped_image.copy()
            draw = ImageDraw.Draw(chord_image)

            # Подготавливаем данные для отрисовки с учетом смещения
            drawing_data = self.prepare_drawing_data(json_parameters, display_type, crop_x, crop_y)
            if drawing_data and drawing_data.get('elements'):
                print(f"🎯 Отрисовка {len(drawing_data['elements'])} элементов на изображении {chord_image.size}")
                draw_chord_elements(draw, drawing_data, display_type, chord_image.size)
            else:
                print("⚠️ Нет элементов для отрисовки")

            # Сохраняем в buffer
            buffer = io.BytesIO()
            chord_image.save(buffer, format='PNG', optimize=True)
            image_data = buffer.getvalue()
            print(f"✅ Изображение сгенерировано: {len(image_data)} bytes, размер: {chord_image.size}")
            return image_data

        except Exception as e:
            print(f"❌ Ошибка генерации изображения: {e}")
            import traceback
            traceback.print_exc()
            return None

    def prepare_drawing_data(self, json_parameters, display_type, crop_x=0, crop_y=0):
        """Подготавливает данные для отрисовки из JSON с учетом смещения"""
        if display_type == "fingers":
            elements = json_parameters.get('elements_fingers', [])
            print(f"🎯 Используются элементы для пальцев: {len(elements)}")
        elif display_type == "notes":
            elements = json_parameters.get('elements_notes', [])
            print(f"🎵 Используются элементы для нот: {len(elements)}")
        else:
            elements = []
            print(f"⚠️ Неизвестный тип отображения: {display_type}")

        if not elements:
            print("⚠️ Нет элементов для отрисовки")
            return None

        # КОРРЕКТИРУЕМ КООРДИНАТЫ С УЧЕТОМ CROP
        adjusted_elements = []
        for element in elements:
            if not isinstance(element, dict):
                continue

            element_type = element.get('type')
            element_data = element.get('data', {}).copy()

            # Корректируем координаты X и Y
            if 'x' in element_data:
                element_data['x'] = element_data['x'] - crop_x
            if 'y' in element_data:
                element_data['y'] = element_data['y'] - crop_y

            adjusted_elements.append({
                'type': element_type,
                'data': element_data
            })

        # ВЫВОДИМ СКОРРЕКТИРОВАННЫЕ КООРДИНАТЫ ДЛЯ ОТЛАДКИ
        print(f"📊 Скорректированные координаты (crop: {crop_x}, {crop_y}):")
        for i, element in enumerate(adjusted_elements):
            element_data = element.get('data', {})
            x = element_data.get('x', 0)
            y = element_data.get('y', 0)
            print(f"  {i}: ({x}, {y}) - {element.get('type')}")

        # Применяем настройки отображения
        display_settings = json_parameters.get('display_settings', {})
        if display_settings:
            adjusted_elements = self.apply_display_settings(adjusted_elements, display_settings)

        return {'elements': adjusted_elements}

    def apply_display_settings(self, elements, display_settings):
        """Применяет настройки отображения"""
        barre_outline = display_settings.get('barre_outline', 'none')
        note_outline = display_settings.get('note_outline', 'none')

        outline_widths = {
            "none": 0, "thin": 2, "medium": 4, "thick": 6
        }

        barre_width = outline_widths.get(barre_outline, 0)
        note_width = outline_widths.get(note_outline, 0)

        modified_elements = []
        for element in elements:
            if not isinstance(element, dict):
                continue

            element_type = element.get('type')
            element_data = element.get('data', {})

            if element_type == 'barre' and barre_width > 0:
                modified_element = element.copy()
                modified_element['data'] = element_data.copy()
                modified_element['data']['outline_width'] = barre_width
                modified_elements.append(modified_element)
            elif element_type == 'note' and note_width > 0:
                modified_element = element.copy()
                modified_element['data'] = element_data.copy()
                modified_element['data']['outline_width'] = note_width
                modified_elements.append(modified_element)
            else:
                modified_elements.append(element)

        return modified_elements

    def get_chord_variants(self, chord_name):
        """Возвращает варианты аккорда"""
        if not ChordData.is_data_available():
            return []

        chord_data = ChordData.get_chord_data(chord_name)
        if not chord_data:
            print(f"❌ Аккорд '{chord_name}' не найден в данных")
            return []

        variants = chord_data.get('variants', [])

        # ДОБАВЛЯЕМ variant_index К КАЖДОМУ ВАРИАНТУ
        for i, variant in enumerate(variants):
            variant['variant_index'] = i  # Добавляем индекс для использования в get_chord_variant_data

        print(f"✅ Аккорд '{chord_name}': найдено {len(variants)} вариантов")
        return variants

    def get_chord_description(self, chord_name):
        """Возвращает описание аккорда"""
        return ChordData.get_chord_description(chord_name)

    def base64_to_pixmap(self, base64_data):
        """Конвертирует base64 в QPixmap с поддержкой прозрачности"""
        try:
            if not base64_data:
                return QPixmap()

            # Убираем возможные разрывы строк в base64 данных
            clean_base64 = base64_data.replace('\n', '').replace('\\', '')
            image_data = base64.b64decode(clean_base64)

            # Создаем QImage из данных
            image = QImage()
            image.loadFromData(image_data)

            if image.isNull():
                print("❌ Не удалось создать QImage из base64 данных")
                return QPixmap()

            # Конвертируем в правильный формат для прозрачности
            if image.hasAlphaChannel():
                image = image.convertToFormat(QImage.Format_ARGB32)
            else:
                image = image.convertToFormat(QImage.Format_RGB32)

            # Конвертируем QImage в QPixmap
            pixmap = QPixmap.fromImage(image)

            if pixmap.isNull():
                print("❌ Не удалось создать QPixmap из QImage")
                return QPixmap()

            return pixmap

        except Exception as e:
            print(f"❌ Ошибка создания pixmap: {e}")
            return QPixmap()

    def base64_to_temp_file(self, base64_data, extension):
        """Создает временный файл из base64 данных"""
        try:
            if not base64_data:
                return None

            clean_base64 = base64_data.replace('\n', '').replace('\\', '')
            file_data = base64.b64decode(clean_base64)
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=extension,
                dir=self.temp_dir
            )
            temp_file.write(file_data)
            temp_file.close()
            self.temp_files.append(temp_file.name)
            return temp_file.name
        except Exception as e:
            print(f"❌ Ошибка создания временного файла: {e}")
            return None

    def get_chord_image(self, chord_name, variant_index=0, display_type="fingers"):
        """Возвращает изображение аккорда как QPixmap"""
        print(f"🎸 Получение изображения: {chord_name}, вариант: {variant_index}, тип: {display_type}")

        variants = self.get_chord_variants(chord_name)
        if not variants or variant_index >= len(variants):
            print(f"❌ Вариант {variant_index} не найден для аккорда {chord_name}")
            return QPixmap()

        variant = variants[variant_index]
        json_parameters = variant.get('json_parameters', {})

        # Генерируем изображение из JSON параметров
        image_data = self.generate_chord_image(json_parameters, display_type)
        if not image_data:
            return QPixmap()

        # Конвертируем в QPixmap
        pixmap = self.base64_to_pixmap(base64.b64encode(image_data).decode())

        if not pixmap.isNull():
            print(f"✅ Изображение аккорда '{chord_name}' успешно сгенерировано")
        else:
            print(f"❌ Не удалось создать QPixmap для аккорда '{chord_name}'")

        return pixmap

    def get_chord_sound_path(self, chord_name, variant_index=0):
        """Возвращает путь к временному звуковому файлу"""
        variants = self.get_chord_variants(chord_name)
        if not variants or variant_index >= len(variants):
            return None

        sound_data = variants[variant_index].get('sound_data')
        if not sound_data:
            print(f"⚠️ Нет звуковых данных для варианта {variant_index} аккорда {chord_name}")
            return None

        return self.base64_to_temp_file(sound_data, '.mp3')

    def get_chord_variant_data(self, chord_name, variant_index=0, display_type="fingers"):
        """Возвращает полные данные варианта аккорда"""
        variants = self.get_chord_variants(chord_name)
        if not variants or variant_index >= len(variants):
            print(f"❌ Вариант {variant_index} не найден для аккорда {chord_name}")
            return None

        variant = variants[variant_index]

        # Генерируем изображение
        json_parameters = variant.get('json_parameters', {})
        image_data = self.generate_chord_image(json_parameters, display_type)

        if not image_data:
            print(f"❌ Не удалось сгенерировать изображение для варианта {variant_index}")
            return None

        # Создаем временный файл для изображения
        image_path = self.base64_to_temp_file(base64.b64encode(image_data).decode(), '.png')
        sound_path = self.base64_to_temp_file(variant.get('sound_data'), '.mp3')

        result = {
            'image_path': image_path,
            'sound_path': sound_path,
            'description': variant.get('description', ''),
            'position': variant.get('position', 0),
            'display_type': display_type
        }

        print(f"✅ Данные варианта {variant_index}: image={bool(image_path)}, sound={bool(sound_path)}")
        return result

    def get_chord_variant_data_with_pixmap(self, chord_name, variant_index=0, display_type="fingers"):
        """Возвращает данные варианта аккорда с готовым QPixmap"""
        print(f"🎯 Получение варианта {variant_index} для аккорда {chord_name}, тип: {display_type}")

        variants = self.get_chord_variants(chord_name)
        if not variants or variant_index >= len(variants):
            print(f"❌ Вариант {variant_index} не найден для аккорда {chord_name}")
            return None

        variant = variants[variant_index]
        print(f"🔍 Вариант данных: position={variant.get('position')}, description={variant.get('description')}")

        # ПРОВЕРЯЕМ РАЗЛИЧИЯ В JSON ПАРАМЕТРАХ
        json_params = variant.get('json_parameters', {})
        print(f"📋 JSON параметры варианта {variant_index}:")
        print(f"   - crop_rect: {json_params.get('crop_rect')}")
        print(f"   - elements_fingers: {len(json_params.get('elements_fingers', []))} элементов")
        print(f"   - elements_notes: {len(json_params.get('elements_notes', []))} элементов")

        # Генерируем изображение и создаем QPixmap
        image_data = self.generate_chord_image(json_params, display_type)

        if not image_data:
            print(f"❌ Не удалось сгенерировать изображение для варианта {variant_index}")
            return None

        pixmap = self.base64_to_pixmap(base64.b64encode(image_data).decode())
        if pixmap.isNull():
            print(f"❌ Не удалось создать QPixmap для варианта {variant_index}")
            return None

        # Создаем временный файл для звука
        sound_path = self.base64_to_temp_file(variant.get('sound_data'), '.mp3')

        result = {
            'pixmap': pixmap,
            'sound_path': sound_path,
            'description': variant.get('description', ''),
            'position': variant.get('position', variant_index + 1),
            'display_type': display_type
        }

        print(f"✅ Вариант {variant_index} загружен: {pixmap.size().width()}x{pixmap.size().height()}")
        return result

    # ⬅️ СОВМЕСТИМОСТЬ СО СТАРЫМ КОДОМ
    def get_chord_image_direct(self, chord_name, variant_index=0):
        """Совместимость со старым кодом - использует fingers по умолчанию"""
        return self.get_chord_image(chord_name, variant_index, "fingers")

    def check_chord_transparency(self, chord_name, variant_index=0):
        """Проверяет прозрачность (совместимость)"""
        pixmap = self.get_chord_image(chord_name, variant_index)
        if pixmap.isNull():
            return False

        temp_image = pixmap.toImage()
        has_transparency = temp_image.hasAlphaChannel()
        print(f"🔍 Аккорд '{chord_name}': {'с прозрачностью' if has_transparency else 'без прозрачности'}")
        return has_transparency

    # ⬅️ НОВЫЕ МЕТОДЫ
    def get_display_types(self):
        """Получить доступные типы отображения"""
        return ChordData.get_display_types()

    def get_stats(self):
        """Получить статистику данных"""
        return ChordData.get_stats()

    def get_original_json_config(self):
        """Получить оригинальную JSON конфигурацию"""
        return ChordData.get_original_json_config()

    def get_available_chords(self):
        """Возвращает список доступных аккордов"""
        return ChordData.get_all_chords()

    def get_chords_by_folder(self, folder_num):
        """Возвращает аккорды из указанной папки"""
        return ChordData.get_chords_by_folder(folder_num)

    def is_data_loaded(self):
        """Проверяет, загружены ли данные аккордов"""
        return ChordData.is_data_available()

    def cleanup(self):
        """Очищает временные файлы"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"⚠️ Ошибка удаления временного файла {temp_file}: {e}")

        self.temp_files.clear()

    def __del__(self):
        """Деструктор - очищает ресурсы"""
        self.cleanup()

