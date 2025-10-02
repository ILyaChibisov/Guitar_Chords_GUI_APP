import base64
import tempfile
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QBuffer, QIODevice

try:
    from data.chords_data import CHORDS_DATA  # ⬅️ ПРЯМОЙ ИМПОРТ ДАННЫХ

    CHORD_DATA_AVAILABLE = True
    print(f"✅ Данные аккордов загружены. Доступно: {len(CHORDS_DATA)} аккордов")

    # Отладочная информация
    print("🔍 Проверка конкретных аккордов:")
    test_chords = ['Bbm', 'Db', 'C', 'G', 'D', 'Am', 'Em', 'D6']  # Добавил D6 для теста
    for chord in test_chords:
        exists = chord in CHORDS_DATA
        status = "✅" if exists else "❌"
        print(f"   {status} {chord}: {'найден' if exists else 'не найден'}")

except ImportError as e:
    print(f"⚠️ Не удалось загрузить данные аккордов: {e}")
    CHORD_DATA_AVAILABLE = False
    CHORDS_DATA = {}


class ChordData:
    """Класс-обертка для работы с данными аккордов"""

    @classmethod
    def get_chord_data(cls, chord_name):
        """Получить данные аккорда по имени"""
        # Пробуем разные варианты написания
        names_to_try = [
            chord_name,
            chord_name.upper(),
            chord_name.upper().replace('M', '').replace('М', ''),
            chord_name.upper().replace('M', 'm').replace('М', 'm'),
            chord_name.upper().replace('6', '').replace('7', '').replace('9', ''),  # для аккордов типа D6
        ]

        for name in names_to_try:
            if name in CHORDS_DATA:
                print(f"✅ Аккорд '{chord_name}' найден как '{name}'")
                return CHORDS_DATA[name]

        # Если не нашли, выводим отладочную информацию
        available_chords = list(CHORDS_DATA.keys())
        print(f"❌ Аккорд '{chord_name}' не найден в данных")
        print(f"   Доступные аккорды: {', '.join(sorted(available_chords)[:10])}...")
        return None

    @classmethod
    def get_all_chords(cls):
        """Получить список всех доступных аккордов"""
        return list(CHORDS_DATA.keys())

    @classmethod
    def get_chords_by_folder(cls, folder_num):
        """Получить аккорды из указанной папки"""
        folder_name = f'folder_{folder_num}'
        return [chord for chord, data in CHORDS_DATA.items()
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
        return CHORD_DATA_AVAILABLE and len(CHORDS_DATA) > 0


class ChordManager:
    """Управляет оптимизированными данными аккордов"""

    def __init__(self):
        self.temp_files = []
        self._setup_temp_dir()

        if not ChordData.is_data_available():
            print("❌ Данные аккордов не загружены! Запустите конвертер.")
        else:
            print(f"✅ Данные аккордов загружены. Доступно: {len(ChordData.get_all_chords())} аккордов")

    def _setup_temp_dir(self):
        """Создает временную директорию для файлов"""
        self.temp_dir = tempfile.mkdtemp(prefix="guitar_chords_")

    def get_chord_variants(self, chord_name):
        """Возвращает варианты аккорда"""
        if not ChordData.is_data_available():
            return []

        chord_data = ChordData.get_chord_data(chord_name)
        if not chord_data:
            print(f"❌ Аккорд '{chord_name}' не найден в данных")
            return []

        variants = chord_data.get('variants', [])
        print(f"✅ Аккорд '{chord_name}': найдено {len(variants)} вариантов")
        return variants

    def get_chord_description(self, chord_name):
        """Возвращает описание аккорда"""
        return ChordData.get_chord_description(chord_name)

    def base64_to_pixmap(self, base64_data):
        """Конвертирует base64 в QPixmap"""
        try:
            if not base64_data:
                return QPixmap()

            # Убираем возможные разрывы строк в base64 данных
            clean_base64 = base64_data.replace('\n', '').replace('\\', '')
            image_data = base64.b64decode(clean_base64)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)

            if pixmap.isNull():
                print("❌ Не удалось создать QPixmap из base64 данных")
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

            # Убираем возможные разрывы строк в base64 данных
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

    def get_chord_image(self, chord_name, variant_index=0):
        """Возвращает изображение аккорда как QPixmap"""
        variants = self.get_chord_variants(chord_name)
        if not variants or variant_index >= len(variants):
            print(f"❌ Вариант {variant_index} не найден для аккорда {chord_name}")
            return QPixmap()

        variant = variants[variant_index]
        image_data = variant.get('image_data')
        if not image_data:
            print(f"❌ Нет данных изображения для варианта {variant_index} аккорда {chord_name}")
            return QPixmap()

        return self.base64_to_pixmap(image_data)

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

    def get_chord_variant_data(self, chord_name, variant_index=0):
        """Возвращает полные данные варианта аккорда - УЛУЧШЕННАЯ ВЕРСИЯ"""
        variants = self.get_chord_variants(chord_name)
        if not variants or variant_index >= len(variants):
            print(f"❌ Вариант {variant_index} не найден для аккорда {chord_name}")
            return None

        variant = variants[variant_index]

        # Создаем временные файлы для изображения и звука
        image_path = self.base64_to_temp_file(variant.get('image_data'), '.png')
        sound_path = self.base64_to_temp_file(variant.get('sound_data'), '.mp3')

        # ✅ ВАЖНО: звук может быть None, но изображение должно быть
        if not image_path:
            print(f"❌ Не удалось создать изображение для варианта {variant_index} аккорда {chord_name}")
            return None

        result = {
            'image_path': image_path,
            'sound_path': sound_path,  # может быть None
            'description': variant.get('description', ''),
            'position': variant.get('position', 0)
        }

        print(f"✅ Данные варианта {variant_index}: image={bool(image_path)}, sound={bool(sound_path)}")
        return result

    def cleanup(self):
        """Очищает временные файлы"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"⚠️ Ошибка удаления временного файла {temp_file}: {e}")

        self.temp_files.clear()

    def get_available_chords(self):
        """Возвращает список доступных аккордов"""
        return ChordData.get_all_chords()

    def get_chords_by_folder(self, folder_num):
        """Возвращает аккорды из указанной папки (1-18)"""
        return ChordData.get_chords_by_folder(folder_num)

    def is_data_loaded(self):
        """Проверяет, загружены ли данные аккордов"""
        return ChordData.is_data_available()