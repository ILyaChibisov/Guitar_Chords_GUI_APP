import os
import sys
import base64
import json
from pathlib import Path

try:
    from pydub import AudioSegment
    from pydub.effects import compress_dynamic_range, high_pass_filter

    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False
    print("⚠️ pydub не установлен. Установите: pip install pydub")
    print("⚠️ Звуки будут сохраняться без оптимизации")


class SimpleChordConverter:
    """Упрощенный конвертер с оптимизацией MP3"""

    def __init__(self, config_path, sounds_base_dir):
        self.config_path = Path(config_path)
        self.sounds_base_dir = Path(sounds_base_dir)
        self.converted_data = {
            'metadata': {},
            'template_image': None,
            'original_json_config': None,
            'chords': {}
        }
        self.compression_stats = {
            'chords_processed': 0,
            'sounds_optimized': 0,
            'chords_with_sound': 0,
            'chords_without_sound': 0,
            'original_size': 0,
            'compressed_size': 0
        }

        self.config = self.load_configuration()
        if self.config:
            self.load_template_image()

    def load_configuration(self):
        """Загружает JSON-конфигурацию и сохраняет её в данных"""
        try:
            if not self.config_path.exists():
                print(f"❌ Файл конфигурации не существует: {self.config_path}")
                return {}

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            chords_count = len(config.get('chords', {}))
            print(f"✅ Загружена конфигурация: {chords_count} аккордов")

            # Заменяем NaN на None во всей конфигурации
            config = self.replace_nan_with_none(config)

            # Сохраняем всю JSON конфигурацию
            self.converted_data['original_json_config'] = config
            self.converted_data['metadata']['original_config_path'] = str(self.config_path).replace('\\', '/')

            return config
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигурации: {e}")
            return {}

    def replace_nan_with_none(self, obj):
        """Рекурсивно заменяет NaN на None в JSON объекте"""
        if isinstance(obj, dict):
            return {k: self.replace_nan_with_none(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.replace_nan_with_none(item) for item in obj]
        elif isinstance(obj, float) and obj != obj:  # Проверка на NaN
            return None
        else:
            return obj

    def load_template_image(self):
        """Загружает и сохраняет основной шаблон изображения в base64"""
        possible_paths = [
            self.config_path.parent / 'img.png',
            self.config_path.parent / 'img.jpg',
            self.config_path.parent / 'template.png',
            Path('chords_config/img.png'),
            Path('chords_config/img.jpg'),
            Path('templates2/img.png'),
            Path('templates2/img.jpg'),
            Path('img.png'),
            Path('img.jpg'),
            Path('template.png'),
            self.config_path.with_name('img.png'),
            self.config_path.with_name('img.jpg'),
        ]

        template_path = None
        for image_path in possible_paths:
            if image_path.exists():
                template_path = image_path
                print(f"🔍 Найден шаблон: {image_path}")
                break

        if not template_path:
            print("❌ Шаблон изображения не найден. Проверенные пути:")
            for path in possible_paths:
                print(f"   - {path}")
            return

        try:
            with open(template_path, 'rb') as f:
                template_data = f.read()

            template_b64 = base64.b64encode(template_data).decode('utf-8')
            self.converted_data['template_image'] = template_b64
            self.converted_data['metadata']['template_size'] = len(template_data)
            self.converted_data['metadata']['template_path'] = str(template_path).replace('\\', '/')
            print(f"✅ Шаблон изображения сохранен в данных: {len(template_data)} bytes")

        except Exception as e:
            print(f"❌ Ошибка загрузки шаблона: {e}")

    def optimize_sound(self, sound_path):
        """Оптимизирует звуковой файл с реальным сжатием"""
        try:
            original_size = os.path.getsize(sound_path)

            if not HAS_PYDUB:
                # Если pydub не установлен, просто читаем файл
                with open(sound_path, 'rb') as file:
                    sound_data = file.read()
                compressed_size = len(sound_data)
            else:
                # Реальная оптимизация с pydub
                sound_data = self._optimize_with_pydub(sound_path)
                compressed_size = len(sound_data) if sound_data else 0

            if not sound_data:
                return None

            self.compression_stats['original_size'] += original_size
            self.compression_stats['compressed_size'] += compressed_size
            self.compression_stats['sounds_optimized'] += 1

            compression_ratio = (original_size - compressed_size) / original_size * 100
            print(
                f"    🔊 {sound_path.name}: {original_size / 1024:.1f}KB → {compressed_size / 1024:.1f}KB ({compression_ratio:+.1f}%)")

            return sound_data

        except Exception as e:
            print(f"    ❌ Ошибка оптимизации звука {sound_path}: {e}")
            return None

    def _optimize_with_pydub(self, sound_path):
        """Оптимизирует звук с помощью pydub"""
        try:
            # Загружаем аудио файл
            if sound_path.suffix.lower() == '.mp3':
                audio = AudioSegment.from_mp3(sound_path)
            elif sound_path.suffix.lower() == '.wav':
                audio = AudioSegment.from_wav(sound_path)
            elif sound_path.suffix.lower() == '.ogg':
                audio = AudioSegment.from_ogg(sound_path)
            else:
                # Для неизвестных форматов просто читаем файл
                with open(sound_path, 'rb') as f:
                    return f.read()

            # Оптимизации для гитарных аккордов:

            # 1. Обрезаем тишину в начале и конце
            audio = self._remove_silence(audio)

            # 2. Нормализуем громкость
            audio = self._normalize_volume(audio)

            # 3. Компрессия динамического диапазона
            audio = compress_dynamic_range(audio, threshold=-20.0, ratio=2.0)

            # 4. Легкий high-pass фильтр для удаления низкочастотного шума
            audio = high_pass_filter(audio, cutoff=80)

            # 5. Экспортируем с оптимизированными настройками MP3
            buffer = self._export_optimized_mp3(audio)

            return buffer.getvalue()

        except Exception as e:
            print(f"    ⚠️ Ошибка pydub оптимизации {sound_path}: {e}")
            # В случае ошибки возвращаем оригинальный файл
            with open(sound_path, 'rb') as f:
                return f.read()

    def _remove_silence(self, audio, silence_thresh=-40.0, chunk_size=10):
        """Обрезает тишину в начале и конце"""
        try:
            # Находим не-тихие сегменты
            non_silent = audio.detect_silence(
                silence_thresh=silence_thresh,
                min_silence_len=100,
                seek_step=chunk_size
            )

            if not non_silent:
                return audio

            # Получаем начало и конец не-тихих сегментов
            start_of_audio = non_silent[0][0] if non_silent[0][0] > 0 else 0
            end_of_audio = non_silent[-1][1] if non_silent[-1][1] < len(audio) else len(audio)

            # Добавляем небольшие отступы
            start_of_audio = max(0, start_of_audio - 50)  # 50ms до начала
            end_of_audio = min(len(audio), end_of_audio + 100)  # 100ms после конца

            return audio[start_of_audio:end_of_audio]

        except Exception as e:
            print(f"    ⚠️ Ошибка обрезки тишины: {e}")
            return audio

    def _normalize_volume(self, audio, target_dBFS=-16.0):
        """Нормализует громкость до целевого уровня"""
        try:
            change_in_dBFS = target_dBFS - audio.dBFS
            return audio.apply_gain(change_in_dBFS)
        except:
            return audio

    def _export_optimized_mp3(self, audio):
        """Экспортирует аудио с оптимизированными настройками MP3"""
        import io

        buffer = io.BytesIO()

        # Оптимизированные настройки для гитарных аккордов:
        # - bitrate=64kbps - достаточно для коротких аккордов
        # - VBR (переменный битрейт) для лучшего качества/размера
        audio.export(
            buffer,
            format="mp3",
            bitrate="64k",  # Низкий битрейт для экономии места
            parameters=[
                "-ac", "1",  # Моно для экономии места
                "-ar", "22050",  # Пониженная частота дискретизации
                "-compression_level", "9",  # Максимальное сжатие
            ]
        )

        return buffer

    def get_safe_chord_name(self, chord_name):
        """Создает безопасное имя папки"""
        safe_name = chord_name.replace('/', '_slash_')
        safe_name = safe_name.replace('#', '_sharp_')
        safe_name = safe_name.replace('\\', '_')
        safe_name = safe_name.replace(' ', '_')
        return safe_name

    def get_base_chord_name(self, chord_name):
        """Извлекает базовое имя аккорда (A, B, C и т.д.)"""
        import re
        base_name = re.sub(r'\d+$', '', chord_name)
        return self.get_safe_chord_name(base_name)

    def find_sound_files(self, chord_name):
        """Находит звуковые файлы для аккорда"""
        safe_chord_name = self.get_safe_chord_name(chord_name)
        chord_sound_dir = self.sounds_base_dir / safe_chord_name

        if not chord_sound_dir.exists():
            base_chord = self.get_base_chord_name(chord_name)
            if base_chord != safe_chord_name:
                chord_sound_dir = self.sounds_base_dir / base_chord

        if not chord_sound_dir.exists():
            print(f"    🔍 Папка со звуками не найдена: {chord_sound_dir}")
            return []

        sound_files = []
        for ext in ['.mp3', '.wav', '.ogg', '.m4a']:
            sound_files.extend(list(chord_sound_dir.glob(f'*{ext}')))

        sorted_files = self.sort_sound_files_by_variant(sound_files, chord_name)
        print(f"    🔊 Найдено звуковых файлов: {len(sorted_files)}")
        return sorted_files

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

    def process_chords(self):
        """Обрабатывает все аккорды из конфигурации"""
        if not self.config:
            print("❌ Конфигурация не загружена, пропускаем обработку аккордов")
            return

        chords_data = self.config.get('chords', {})

        if not chords_data:
            print("❌ В конфигурации нет данных об аккордов")
            return

        print(f"🔧 Обработка {len(chords_data)} аккордов...")

        for chord_key, chord_data in chords_data.items():
            print(f"  🎵 {chord_key}")

            # Получаем информацию об аккорде
            base_info = chord_data.get('base_info', {})
            chord_name = base_info.get('base_chord', chord_key)
            group_name = chord_data.get('group', 'unknown')

            # Ищем звуки
            sound_files = self.find_sound_files(chord_name)
            variants = []
            has_sound = False

            # Создаем варианты с параметрами JSON
            for i, sound_file in enumerate(sound_files, 1):
                sound_data = self.optimize_sound(sound_file)
                sound_b64 = base64.b64encode(sound_data).decode() if sound_data else None

                if sound_b64:
                    has_sound = True

                # Сохраняем параметры JSON для ОБОИХ вариантов отображения
                variant_data = {
                    'position': i,
                    'description': f"Вариант {i}",
                    'json_parameters': {
                        'crop_rect': chord_data.get('crop_rect', []),
                        'elements_fingers': chord_data.get('elements_fingers', []),
                        'elements_notes': chord_data.get('elements_notes', []),
                        'display_settings': chord_data.get('display_settings', {})
                    },
                    'sound_data': sound_b64
                }
                variants.append(variant_data)

            # Если нет звуков, создаем базовый вариант
            if not variants:
                variants.append({
                    'position': 1,
                    'description': "Основной вариант",
                    'json_parameters': {
                        'crop_rect': chord_data.get('crop_rect', []),
                        'elements_fingers': chord_data.get('elements_fingers', []),
                        'elements_notes': chord_data.get('elements_notes', []),
                        'display_settings': chord_data.get('display_settings', {})
                    },
                    'sound_data': None
                })

            if variants:
                # Получаем описание аккорда
                description = base_info.get('caption', f'Аккорд {chord_name}')
                chord_type = base_info.get('type', 'major').lower()

                self.converted_data['chords'][chord_name] = {
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
        """Сохраняет данные аккордов в новом формате"""
        print(f"💾 Сохранение в {output_file}...")

        # Создаем директорию если не существует
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('"""\nДанные аккордов (с шаблоном и JSON конфигурацией)\nГенерация: SimpleChordConverter\n"""\n\n')
            f.write('CHORDS_DATA = {\n')

            # Сохраняем метаданные
            f.write('    "metadata": {\n')
            f.write(f'        "template_size": {self.converted_data["metadata"].get("template_size", 0)},\n')
            f.write(f'        "total_chords": {len(self.converted_data["chords"])},\n')
            f.write(f'        "converter_version": "3.1",\n')
            config_path = self.converted_data["metadata"].get("original_config_path", "").replace('\\', '/')
            f.write(f'        "original_config_path": "{config_path}"\n')
            f.write('    },\n')

            # Сохраняем шаблон изображения
            f.write('    "template_image": """\n')
            if self.converted_data['template_image']:
                f.write(self.converted_data['template_image'])
            f.write('""",\n')

            # Сохраняем всю JSON конфигурацию с заменой null на None
            f.write('    "original_json_config": ')
            json_str = json.dumps(self.converted_data['original_json_config'], ensure_ascii=False, indent=4)
            # Заменяем JSON null на Python None
            json_str = json_str.replace(': null', ': None').replace(':null', ':None')
            f.write(json_str)
            f.write(',\n')

            # Сохраняем аккорды
            f.write('    "chords": {\n')

            for chord_name, chord_data in sorted(self.converted_data['chords'].items()):
                f.write(f'        "{chord_name}": {{\n')
                f.write(f'            "name": "{chord_data["name"]}",\n')
                f.write(f'            "folder": "{chord_data["folder"]}",\n')
                f.write(f'            "description": "{chord_data["description"]}",\n')
                f.write(f'            "type": "{chord_data["type"]}",\n')
                f.write(f'            "variants": [\n')

                for variant in chord_data['variants']:
                    f.write('                {\n')
                    f.write(f'                    "position": {variant["position"]},\n')
                    f.write(f'                    "description": "{variant["description"]}",\n')

                    # Сохраняем JSON параметры
                    f.write(f'                    "json_parameters": {{\n')
                    json_params = variant["json_parameters"]
                    f.write(f'                        "crop_rect": {json.dumps(json_params["crop_rect"])},\n')
                    f.write(
                        f'                        "elements_fingers": {json.dumps(json_params["elements_fingers"], ensure_ascii=False)},\n')
                    f.write(
                        f'                        "elements_notes": {json.dumps(json_params["elements_notes"], ensure_ascii=False)},\n')
                    f.write(
                        f'                        "display_settings": {json.dumps(json_params["display_settings"])}\n')
                    f.write(f'                    }},\n')

                    # Сохраняем звук
                    if variant['sound_data']:
                        f.write(f'                    "sound_data": """{variant["sound_data"]}"""\n')
                    else:
                        f.write(f'                    "sound_data": None\n')

                    f.write('                },\n')

                f.write('            ]\n')
                f.write('        },\n')

            f.write('    }\n')
            f.write('}\n')

    def print_stats(self):
        """Выводит статистику"""
        template_size = self.converted_data["metadata"].get("template_size", 0)
        total_savings = self.compression_stats['original_size'] - self.compression_stats['compressed_size']
        savings_percent = (total_savings / self.compression_stats['original_size'] * 100) if self.compression_stats[
                                                                                                 'original_size'] > 0 else 0

        print(f"\n📊 Статистика:")
        print(f"   🎸 Аккордов: {self.compression_stats['chords_processed']}")
        if template_size > 0:
            print(f"   🖼️  Шаблон: {template_size / 1024:.1f} KB")
        else:
            print(f"   🖼️  Шаблон: не загружен")
        print(f"   📋 JSON конфигурация: {'сохранена' if self.converted_data['original_json_config'] else 'нет'}")
        print(f"   🔊 Звуков: {self.compression_stats['sounds_optimized']}")
        print(f"   🔊 Со звуком: {self.compression_stats['chords_with_sound']}")
        print(f"   🔇 Без звука: {self.compression_stats['chords_without_sound']}")

        if self.compression_stats['sounds_optimized'] > 0:
            print(f"   💾 Экономия места: {total_savings / 1024 / 1024:.2f} MB ({savings_percent:+.1f}%)")
            print(f"   📦 Исходный размер: {self.compression_stats['original_size'] / 1024 / 1024:.2f} MB")
            print(f"   📦 Сжатый размер: {self.compression_stats['compressed_size'] / 1024 / 1024:.2f} MB")


def find_config_file():
    """Находит файл конфигурации автоматически"""
    possible_paths = [
        Path("chords_config/chords_configuration.json"),
        Path("chords_configuration.json"),
        Path("templates2/chords_configuration.json"),
        Path("config/chords_configuration.json"),
        Path("../chords_configuration.json"),
        Path("./chords_configuration.json"),
        Path("chords_config.json"),
        Path("config.json"),
    ]

    for path in possible_paths:
        if path.exists():
            print(f"✅ Найден файл конфигурации: {path}")
            return path

    print("❌ Файл конфигурации не найден. Проверенные пути:")
    for path in possible_paths:
        exists = "✅ СУЩЕСТВУЕТ" if path.exists() else "❌ не существует"
        print(f"   {exists}: {path}")

    return None


def find_sounds_dir():
    """Находит папку со звуками автоматически"""
    possible_paths = [
        Path("sound"),
        Path("sounds"),
        Path("chords_config/sound"),
        Path("chords_config/sounds"),
        Path("templates2/sound"),
        Path("templates2/sounds"),
        Path("../sound"),
        Path("../sounds"),
    ]

    for path in possible_paths:
        if path.exists():
            print(f"✅ Найдена папка со звуками: {path}")
            return path

    print("⚠️ Папка со звуками не найдена. Проверенные пути:")
    for path in possible_paths:
        exists = "✅ СУЩЕСТВУЕТ" if path.exists() else "❌ не существует"
        print(f"   {exists}: {path}")

    return None


def main():
    """Основная функция"""
    print("🎸 Упрощенный конвертер аккордов с оптимизацией MP3")
    print("=" * 50)

    if HAS_PYDUB:
        print("✅ pydub доступен - звуки будут оптимизированы")
    else:
        print("⚠️ pydub не доступен - звуки будут сохранены как есть")
        print("💡 Установите: pip install pydub")

    # Автопоиск путей
    config_path = find_config_file()
    if not config_path:
        print("\n💡 Решение: поместите chords_configuration.json в одну из папок:")
        print("   - chords_config/")
        print("   - templates2/")
        print("   - корневая папка проекта")
        return

    sounds_dir = find_sounds_dir()
    if not sounds_dir:
        print("\n⚠️ Продолжаем без звуков...")

    print(f"✅ Конфигурация: {config_path}")
    print(f"✅ Звуки: {sounds_dir if sounds_dir else 'не найдены'}")

    # Создаем директорию data если не существует
    os.makedirs('data', exist_ok=True)

    try:
        converter = SimpleChordConverter(config_path, sounds_dir)
        converter.process_chords()

        if converter.converted_data['chords']:
            converter.save_chords_data("data/chords_data.py")
            converter.print_stats()
            print(f"\n✅ Готово! Файл: data/chords_data.py")

            # Проверяем созданный файл
            output_path = Path("data/chords_data.py")
            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"📦 Размер файла: {file_size / 1024 / 1024:.2f} MB")
            else:
                print("❌ Выходной файл не создан")
        else:
            print("❌ Нет данных для сохранения")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()