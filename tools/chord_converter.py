#!/usr/bin/env python3
"""
Исправленный конвертер аккордов для работы с JSON-конфигурацией
"""

import os
import sys
import base64
import json
from pathlib import Path

try:
    from PIL import Image, ImageDraw
    import io

    HAS_PILLOW = True
except ImportError:
    print("❌ Pillow не установлен! Установите: pip install Pillow")
    HAS_PILLOW = False
    sys.exit(1)

try:
    from drawing_elements import draw_chord_elements

    HAS_DRAWING = True
except ImportError as e:
    print(f"❌ Модуль drawing_elements не найден: {e}")
    HAS_DRAWING = False


class FixedChordConverter:
    """Исправленный конвертер для правильной структуры JSON"""

    def __init__(self, config_path, sounds_base_dir):
        self.config_path = Path(config_path)
        self.sounds_base_dir = Path(sounds_base_dir)
        self.converted_data = {}
        self.compression_stats = {
            'images_generated': 0,
            'sounds_optimized': 0,
            'chords_with_sound': 0,
            'chords_without_sound': 0,
            'chords_processed': 0
        }

        self.config = self.load_configuration()
        self.base_image = self.load_base_image()

    def load_configuration(self):
        """Загружает JSON-конфигурацию"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            chords_count = len(config.get('chords', {}))
            print(f"✅ Загружена конфигурация: {chords_count} аккордов")
            return config
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигурации: {e}")
            return {}

    def load_base_image(self):
        """Загружает основное изображение грифа"""
        try:
            possible_paths = [
                self.config_path.parent / 'img.png',
                Path('chords_config/img.png'),
                Path('templates2/img.png'),
                Path('img.png'),
                self.config_path.with_name('img.png')
            ]

            for image_path in possible_paths:
                if image_path.exists():
                    image = Image.open(image_path)
                    print(f"✅ Загружено изображение грифа: {image_path}")
                    return image

            print("❌ Изображение грифа не найдено")
            return None

        except Exception as e:
            print(f"❌ Ошибка загрузки изображения грифа: {e}")
            return None

    def process_crop_rect(self, crop_rect):
        """Обрабатывает crop_rect (может быть списком или словарем)"""
        if isinstance(crop_rect, list) and len(crop_rect) == 4:
            # Формат: [x, y, width, height]
            return {
                'x': crop_rect[0],
                'y': crop_rect[1],
                'width': crop_rect[2],
                'height': crop_rect[3]
            }
        elif isinstance(crop_rect, dict):
            # Формат: {'x': ..., 'y': ..., 'width': ..., 'height': ...}
            return crop_rect
        else:
            print(f"    ⚠️ Неизвестный формат crop_rect: {crop_rect}")
            return {'x': 0, 'y': 0, 'width': 400, 'height': 200}

    def generate_chord_image(self, chord_data, display_type="fingers"):
        """Генерирует изображение аккорда"""
        if not self.base_image or not HAS_DRAWING:
            return None

        try:
            # Обрабатываем crop_rect
            crop_rect_data = self.process_crop_rect(chord_data.get('crop_rect', []))
            x = crop_rect_data.get('x', 0)
            y = crop_rect_data.get('y', 0)
            width = crop_rect_data.get('width', 400)
            height = crop_rect_data.get('height', 200)

            # Проверяем границы обрезки
            img_width, img_height = self.base_image.size
            x = max(0, min(x, img_width - 1))
            y = max(0, min(y, img_height - 1))
            width = max(1, min(width, img_width - x))
            height = max(1, min(height, img_height - y))

            # Обрезаем изображение
            cropped_image = self.base_image.crop((x, y, x + width, y + height))
            chord_image = cropped_image.copy()
            draw = ImageDraw.Draw(chord_image)

            # Подготавливаем данные для отрисовки
            drawing_data = self.prepare_drawing_data(chord_data, display_type)
            if drawing_data and drawing_data.get('elements'):
                draw_chord_elements(draw, drawing_data, display_type, chord_image.size)

            # Сохраняем в buffer
            buffer = io.BytesIO()
            chord_image.save(buffer, format='PNG', optimize=True)
            optimized_data = buffer.getvalue()

            self.compression_stats['images_generated'] += 1
            return optimized_data

        except Exception as e:
            print(f"    ❌ Ошибка генерации изображения: {e}")
            return None

    def prepare_drawing_data(self, chord_data, display_type):
        """Подготавливает данные для отрисовки"""
        if display_type == "fingers":
            elements = chord_data.get('elements_fingers', [])
        else:
            elements = chord_data.get('elements_notes', [])

        if not elements:
            return None

        # Применяем настройки отображения
        display_settings = chord_data.get('display_settings', {})
        if display_settings:
            elements = self.apply_display_settings(elements, display_settings)

        return {'elements': elements}

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

    def find_sound_files(self, chord_name):
        """Находит звуковые файлы для аккорда"""
        # Используем base_chord из base_info для поиска звуков
        safe_chord_name = self.get_safe_chord_name(chord_name)
        chord_sound_dir = self.sounds_base_dir / safe_chord_name

        if not chord_sound_dir.exists():
            # Пробуем найти по базовому имени аккорда (A, B, C и т.д.)
            base_chord = self.get_base_chord_name(chord_name)
            if base_chord != safe_chord_name:
                chord_sound_dir = self.sounds_base_dir / base_chord

        if not chord_sound_dir.exists():
            print(f"    🔍 Папка со звуками не найдена: {chord_sound_dir}")
            return []

        sound_files = []
        for ext in ['.mp3', '.wav', '.ogg']:
            sound_files.extend(list(chord_sound_dir.glob(f'*{ext}')))

        # Сортируем по вариантам
        sorted_files = self.sort_sound_files_by_variant(sound_files, chord_name)
        print(f"    🔊 Найдено звуковых файлов: {len(sorted_files)}")
        return sorted_files

    def get_base_chord_name(self, chord_name):
        """Извлекает базовое имя аккорда (A, B, C и т.д.)"""
        # Убираем цифры вариантов (A1 -> A, B2 -> B)
        import re
        base_name = re.sub(r'\d+$', '', chord_name)
        return self.get_safe_chord_name(base_name)

    def get_safe_chord_name(self, chord_name):
        """Создает безопасное имя папки"""
        safe_name = chord_name.replace('/', '_slash_')
        safe_name = safe_name.replace('#', '_sharp_')
        safe_name = safe_name.replace('\\', '_')
        safe_name = safe_name.replace(' ', '_')
        return safe_name

    def sort_sound_files_by_variant(self, sound_files, chord_name):
        """Сортирует звуковые файлы по вариантам"""
        variants = {}
        for sound_file in sound_files:
            variant = self.detect_variant_from_filename(sound_file, chord_name)
            variants[variant] = sound_file

        return [variants[v] for v in sorted(variants.keys())]

    def detect_variant_from_filename(self, sound_file, chord_name):
        """Определяет номер варианта"""
        filename = sound_file.stem.lower()
        chord_name_lower = chord_name.lower()

        if filename == chord_name_lower:
            return 1

        patterns = [
            f"{chord_name_lower}(вариант",
            f"{chord_name_lower}_вариант",
            f"{chord_name_lower}_variant",
            f"{chord_name_lower}(",
            f"{chord_name_lower}_"
        ]

        for pattern in patterns:
            if pattern in filename:
                import re
                numbers = re.findall(r'\d+', filename.split(pattern)[1])
                if numbers:
                    return int(numbers[0])

        return 1

    def optimize_sound(self, sound_path):
        """Оптимизирует звуковой файл"""
        try:
            with open(sound_path, 'rb') as file:
                sound_data = file.read()

            self.compression_stats['sounds_optimized'] += 1
            file_size_kb = len(sound_data) / 1024
            print(f"      🔊 {sound_path.name}: {file_size_kb:.1f}KB")
            return sound_data

        except Exception as e:
            print(f"      ❌ Ошибка звука {sound_path}: {e}")
            return None

    def process_chords(self):
        """Обрабатывает все аккорды из конфигурации"""
        chords_data = self.config.get('chords', {})

        if not chords_data:
            print("❌ В конфигурации нет данных об аккордах")
            return

        print(f"🔧 Обработка {len(chords_data)} аккордов...")

        for chord_key, chord_data in chords_data.items():
            print(f"  🎵 {chord_key}")

            # Получаем информацию об аккорде
            base_info = chord_data.get('base_info', {})
            chord_name = base_info.get('base_chord', chord_key)
            group_name = chord_data.get('group', 'unknown')

            # Генерируем изображения
            image_fingers = self.generate_chord_image(chord_data, "fingers")
            image_notes = self.generate_chord_image(chord_data, "notes")

            if not image_fingers and not image_notes:
                print(f"    ⚠️ Не удалось сгенерировать изображения")
                continue

            # Ищем звуки
            sound_files = self.find_sound_files(chord_name)
            variants = []
            has_sound = False

            # Создаем варианты
            for i, sound_file in enumerate(sound_files, 1):
                sound_data = self.optimize_sound(sound_file)
                sound_b64 = base64.b64encode(sound_data).decode() if sound_data else None

                if sound_b64:
                    has_sound = True

                variant_data = {
                    'position': i,
                    'description': f"Вариант {i}",
                    'image_data_fingers': base64.b64encode(image_fingers).decode() if image_fingers else None,
                    'image_data_notes': base64.b64encode(image_notes).decode() if image_notes else None,
                    'sound_data': sound_b64
                }
                variants.append(variant_data)

            # Если нет звуков, создаем базовый вариант
            if not variants and (image_fingers or image_notes):
                variants.append({
                    'position': 1,
                    'description': "Основной вариант",
                    'image_data_fingers': base64.b64encode(image_fingers).decode() if image_fingers else None,
                    'image_data_notes': base64.b64encode(image_notes).decode() if image_notes else None,
                    'sound_data': None
                })

            if variants:
                # Получаем описание аккорда
                description = base_info.get('caption', f'Аккорд {chord_name}')
                chord_type = base_info.get('type', 'major').lower()

                self.converted_data[chord_name] = {
                    'name': chord_name,
                    'folder': f'group_{group_name}',
                    'description': description,
                    'type': chord_type,
                    'variants': variants
                }

                if has_sound:
                    self.compression_stats['chords_with_sound'] += 1
                    sound_status = "🔊 со звуком"
                else:
                    self.compression_stats['chords_without_sound'] += 1
                    sound_status = "🔇 без звука"

                self.compression_stats['chords_processed'] += 1
                print(f"    ✅ {len(variants)} вариантов, {sound_status}")

    def save_chords_data(self, output_file):
        """Сохраняет данные аккордов"""
        print(f"💾 Сохранение в {output_file}...")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('"""\nДанные аккордов\nГенерация: FixedChordConverter\n"""\n\n')
            f.write('CHORDS_DATA = {\n')

            for chord_name, chord_data in sorted(self.converted_data.items()):
                f.write(f'    "{chord_name}": {{\n')
                f.write(f'        "name": "{chord_data["name"]}",\n')
                f.write(f'        "folder": "{chord_data["folder"]}",\n')
                f.write(f'        "description": "{chord_data["description"]}",\n')
                f.write(f'        "type": "{chord_data["type"]}",\n')
                f.write(f'        "variants": [\n')

                for variant in chord_data['variants']:
                    f.write('            {\n')
                    f.write(f'                "position": {variant["position"]},\n')
                    f.write(f'                "description": "{variant["description"]}",\n')

                    if variant['image_data_fingers']:
                        f.write(f'                "image_data_fingers": """{variant["image_data_fingers"]}""",\n')
                    else:
                        f.write(f'                "image_data_fingers": None,\n')

                    if variant['image_data_notes']:
                        f.write(f'                "image_data_notes": """{variant["image_data_notes"]}""",\n')
                    else:
                        f.write(f'                "image_data_notes": None,\n')

                    if variant['sound_data']:
                        f.write(f'                "sound_data": """{variant["sound_data"]}"""\n')
                    else:
                        f.write(f'                "sound_data": None\n')

                    f.write('            },\n')

                f.write('        ]\n')
                f.write('    },\n')

            f.write('}\n')

    def print_stats(self):
        """Выводит статистику"""
        print(f"\n📊 Статистика:")
        print(f"   🎸 Аккордов: {self.compression_stats['chords_processed']}")
        print(f"   🖼️ Изображений: {self.compression_stats['images_generated']}")
        print(f"   🔊 Звуков: {self.compression_stats['sounds_optimized']}")
        print(f"   🔊 Со звуком: {self.compression_stats['chords_with_sound']}")
        print(f"   🔇 Без звука: {self.compression_stats['chords_without_sound']}")


def main():
    """Основная функция"""
    print("🎸 Исправленный конвертер аккордов")
    print("=" * 50)

    if not HAS_PILLOW or not HAS_DRAWING:
        return

    # Автопоиск путей
    config_path = None
    for path in [
        Path("chords_config/chords_configuration.json"),
        Path("chords_configuration.json"),
        Path("templates2/chords_configuration.json")
    ]:
        if path.exists():
            config_path = path
            break

    if not config_path:
        print("❌ Конфигурация не найдена")
        return

    sounds_dir = None
    for path in [Path("sound"), Path("sounds")]:
        if path.exists():
            sounds_dir = path
            break

    if not sounds_dir:
        print("❌ Папка со звуками не найдена")
        return

    print(f"✅ Конфигурация: {config_path}")
    print(f"✅ Звуки: {sounds_dir}")

    os.makedirs('data', exist_ok=True)

    try:
        converter = FixedChordConverter(config_path, sounds_dir)
        converter.process_chords()

        if converter.converted_data:
            converter.save_chords_data("data/chords_data.py")
            converter.print_stats()
            print(f"\n✅ Готово! Файл: data/chords_data.py")
        else:
            print("❌ Нет данных для сохранения")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()