#!/usr/bin/env python3
"""
Оптимизированный конвертер аккордов со сжатием
"""

import os
import sys
import base64
from pathlib import Path

try:
    from PIL import Image
    import io

    HAS_PILLOW = True
except ImportError:
    print("❌ Pillow не установлен! Установите: pip install Pillow")
    HAS_PILLOW = False
    sys.exit(1)


class ChordStructureConverter:
    """Оптимизированный конвертер со сжатием изображений"""

    def __init__(self, chords_base_dir):
        self.chords_base_dir = Path(chords_base_dir)
        self.converted_data = {}
        self.compression_stats = {
            'original_size': 0,
            'compressed_size': 0,
            'images_optimized': 0,
            'sounds_optimized': 0,
            'chords_with_sound': 0,
            'chords_without_sound': 0
        }

    def optimize_image(self, image_path, max_size=(400, 200), quality=85):
        """Оптимизирует изображение: уменьшает размер и качество"""
        try:
            with Image.open(image_path) as img:
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)

                optimized_data = buffer.getvalue()

                original_size = os.path.getsize(image_path)
                self.compression_stats['original_size'] += original_size
                self.compression_stats['compressed_size'] += len(optimized_data)
                self.compression_stats['images_optimized'] += 1

                print(f"    📊 Изображение: {original_size / 1024:.1f}KB → {len(optimized_data) / 1024:.1f}KB")

                return optimized_data

        except Exception as e:
            print(f"    ❌ Ошибка оптимизации {image_path}: {e}")
            return None

    def optimize_sound(self, sound_path):
        """Оптимизирует звуковой файл (пока просто копирует)"""
        try:
            with open(sound_path, 'rb') as file:
                sound_data = file.read()

            original_size = os.path.getsize(sound_path)
            self.compression_stats['original_size'] += original_size
            self.compression_stats['compressed_size'] += len(sound_data)
            self.compression_stats['sounds_optimized'] += 1

            print(f"    🔊 Звук: {original_size / 1024:.1f}KB → {len(sound_data) / 1024:.1f}KB")

            return sound_data

        except Exception as e:
            print(f"    ❌ Ошибка оптимизации звука {sound_path}: {e}")
            return None

    def file_to_optimized_base64(self, file_path, is_image=True):
        """Конвертирует файл в оптимизированный base64"""
        try:
            if is_image:
                optimized_data = self.optimize_image(file_path)
                if optimized_data:
                    return base64.b64encode(optimized_data).decode('utf-8')
            else:
                optimized_data = self.optimize_sound(file_path)
                if optimized_data:
                    return base64.b64encode(optimized_data).decode('utf-8')

        except Exception as e:
            print(f"    ❌ Ошибка конвертации {file_path}: {e}")
            return None
        return None

    def scan_chords_structure(self):
        """Сканирует структуру папок с оптимизацией"""
        print("🔍 Сканирование структуры аккордов...")

        for folder_num in range(1, 19):
            folder_path = self.chords_base_dir / str(folder_num)

            if not folder_path.exists():
                print(f"⚠️ Папка {folder_num} не найдена, пропускаем")
                continue

            print(f"📁 Обработка папки {folder_num}...")

            chords_list = self.get_chords_for_folder(folder_num)
            if not chords_list:
                print(f"⚠️ Не найден список аккордов для папки {folder_num}")
                continue

            for chord_name in chords_list:
                chord_folder = folder_path / chord_name
                if chord_folder.exists() and chord_folder.is_dir():
                    self.process_chord_folder(chord_name, chord_folder, folder_num)

    def get_chords_for_folder(self, folder_num):
        """Возвращает список аккордов для указанной папки"""
        try:
            project_root = Path(__file__).parent.parent
            sys.path.insert(0, str(project_root))

            from const import CHORDS_TYPE_LIST

            if 1 <= folder_num <= len(CHORDS_TYPE_LIST):
                return CHORDS_TYPE_LIST[folder_num - 1]
            return []
        except ImportError as e:
            print(f"❌ Не удалось импортировать const.py: {e}")
            return []

    def get_chord_description(self, chord_name, folder_num):
        """Возвращает описание аккорда"""
        try:
            from const import CHORDS_TYPE_NAME_LIST_DSR

            if 1 <= folder_num <= len(CHORDS_TYPE_NAME_LIST_DSR):
                descriptions = CHORDS_TYPE_NAME_LIST_DSR[folder_num - 1]
                chords_list = self.get_chords_for_folder(folder_num)

                if chord_name in chords_list:
                    index = chords_list.index(chord_name)
                    if index < len(descriptions):
                        return descriptions[index]
            return f"Аккорд {chord_name}"
        except ImportError:
            return f"Аккорд {chord_name}"

    def process_chord_folder(self, chord_name, chord_folder, folder_num):
        """Обрабатывает папку с аккордом"""
        print(f"  🎵 Обработка аккорда: {chord_name}")

        variants = []
        image_files = []
        sound_files = []

        for file_path in chord_folder.iterdir():
            if file_path.is_file():
                if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    image_files.append(file_path)
                elif file_path.suffix.lower() in ['.mp3', '.wav']:
                    sound_files.append(file_path)

        image_files.sort()
        sound_files.sort()

        has_sound = False

        for i, img_file in enumerate(image_files):
            variant_data = {
                'position': i + 1,
                'description': f"Вариант {i + 1}",
                'image_data': self.file_to_optimized_base64(img_file, is_image=True),
                'sound_data': None
            }

            if i < len(sound_files):
                sound_data = self.file_to_optimized_base64(sound_files[i], is_image=False)
                if sound_data:
                    variant_data['sound_data'] = sound_data
                    has_sound = True
            else:
                sound_file = self.find_matching_sound(img_file, sound_files)
                if sound_file:
                    sound_data = self.file_to_optimized_base64(sound_file, is_image=False)
                    if sound_data:
                        variant_data['sound_data'] = sound_data
                        has_sound = True

            if variant_data['image_data']:
                variants.append(variant_data)

        if variants:
            chord_data = {
                'name': chord_name,
                'folder': f'folder_{folder_num}',
                'description': self.get_chord_description(chord_name, folder_num),
                'variants': variants
            }
            self.converted_data[chord_name] = chord_data

            # Статистика по звуку
            if has_sound:
                self.compression_stats['chords_with_sound'] += 1
                sound_status = "🔊 со звуком"
            else:
                self.compression_stats['chords_without_sound'] += 1
                sound_status = "🔇 без звука"

            print(f"  ✅ Аккорд {chord_name}: {len(variants)} вариантов, {sound_status}")
        else:
            print(f"  ❌ Аккорд {chord_name}: нет валидных вариантов")

    def find_matching_sound(self, image_file, sound_files):
        """Находит соответствующий звуковой файл"""
        img_stem = image_file.stem
        patterns = [img_stem, img_stem.split('_')[0]]

        for pattern in patterns:
            for sound_file in sound_files:
                if pattern in sound_file.stem:
                    return sound_file
        return None

    def save_chords_data(self, output_file):
        """Сохраняет ТОЛЬКО данные аккордов в отдельный файл"""
        print(f"💾 Сохранение данных аккордов в {output_file}...")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('"""\n')
            f.write('Данные аккордов в формате base64\n')
            f.write('Сгенерировано автоматически конвертером\n')
            f.write('"""\n\n')

            f.write('CHORDS_DATA = {\n')

            for chord_name, chord_data in sorted(self.converted_data.items()):
                f.write(f'    "{chord_name}": {{\n')
                f.write(f'        "name": "{chord_data["name"]}",\n')
                f.write(f'        "folder": "{chord_data["folder"]}",\n')
                f.write(f'        "description": "{chord_data["description"]}",\n')
                f.write(f'        "variants": [\n')

                for variant in chord_data['variants']:
                    f.write('            {\n')
                    f.write(f'                "position": {variant["position"]},\n')
                    f.write(f'                "description": "{variant["description"]}",\n')

                    if variant['image_data']:
                        image_data = self.split_long_string(variant['image_data'], 100)
                        f.write(f'                "image_data": """{image_data}""",\n')
                    else:
                        f.write(f'                "image_data": None,\n')

                    if variant['sound_data']:
                        sound_data = self.split_long_string(variant['sound_data'], 100)
                        f.write(f'                "sound_data": """{sound_data}"""\n')
                    else:
                        f.write(f'                "sound_data": None\n')

                    f.write('            },\n')

                f.write('        ]\n')
                f.write('    },\n')

            f.write('}\n')

    def split_long_string(self, long_string, line_length):
        """Разбивает длинную строку на несколько строк"""
        return '\\\n'.join([long_string[i:i + line_length]
                            for i in range(0, len(long_string), line_length)])

    def print_compression_stats(self):
        """Выводит статистику сжатия"""
        print("\n📊 Статистика оптимизации:")
        print(f"   🖼️ Оптимизировано изображений: {self.compression_stats['images_optimized']}")
        print(f"   🔊 Оптимизировано звуковых файлов: {self.compression_stats['sounds_optimized']}")
        print(f"   📦 Исходный размер: {self.compression_stats['original_size'] / 1024 / 1024:.2f} MB")
        print(f"   🗜️ Сжатый размер: {self.compression_stats['compressed_size'] / 1024 / 1024:.2f} MB")

        if self.compression_stats['original_size'] > 0:
            ratio = (1 - self.compression_stats['compressed_size'] / self.compression_stats['original_size']) * 100
            print(f"   📈 Экономия: {ratio:.1f}%")

        print(f"   🎵 Аккордов со звуком: {self.compression_stats['chords_with_sound']}")
        print(f"   🔇 Аккордов без звука: {self.compression_stats['chords_without_sound']}")
        print(f"   🎸 Всего аккордов: {len(self.converted_data)}")


def main():
    """Основная функция конвертера"""
    print("🎸 Оптимизированный конвертер аккордов")
    print("=" * 50)

    if not HAS_PILLOW:
        print("❌ Pillow не установлен. Установите: pip install Pillow")
        return

    possible_paths = [
        Path("chords"),
        Path("аккорды"),
        Path("data/chords"),
        Path("../chords"),
        Path("C:/guitar_chords"),
        Path("D:/guitar_chords"),
    ]

    chords_directory = None
    for path in possible_paths:
        if path.exists() and path.is_dir():
            chords_directory = path
            break

    if not chords_directory:
        user_path = input("📁 Введите путь к папке с аккордами: ").strip('"\' ')
        chords_directory = Path(user_path)

    if not chords_directory.exists():
        print(f"❌ Папка {chords_directory} не существует!")
        return

    print(f"✅ Используется папка: {chords_directory}")

    os.makedirs('data', exist_ok=True)
    data_file = "data/chords_data.py"

    try:
        converter = ChordStructureConverter(chords_directory)
        converter.scan_chords_structure()

        if not converter.converted_data:
            print("❌ Не найдено данных для конвертации!")
            return

        converter.save_chords_data(data_file)
        converter.print_compression_stats()

        print(f"\n✅ Конвертация завершена! Файл: {data_file}")

    except Exception as e:
        print(f"❌ Ошибка при конвертации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()