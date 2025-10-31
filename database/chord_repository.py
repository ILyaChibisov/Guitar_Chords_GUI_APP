"""
Репозиторий для работы с оптимизированными данными аккордов
"""

from core.chord_manager import ChordManager
from data.chord_data import ChordData

class ChordRepository:
    """Репозиторий для доступа к данным аккордов"""

    def __init__(self):
        self.chord_manager = ChordManager()
        self.chord_data = ChordData()

    def get_chord_info(self, chord_name):
        """
        Возвращает информацию об аккорде в формате совместимом с БД
        """
        variants = self.chord_manager.get_chord_variants(chord_name)
        if not variants:
            return None

        chord_id = hash(chord_name) % 100000
        folder = self.chord_data.get_chord_folder(chord_name)
        chord_type = self.chord_data.get_chord_type(chord_name)

        return {
            'id': chord_id,
            'name': chord_name,
            'folder': folder,
            'type': chord_type,
            'variants_count': len(variants),
            'description': self.chord_data.get_chord_description(chord_name)
        }

    def _get_folder_number(self, chord_name):
        """Определяет номер папки для аккорда"""
        try:
            from const import CHORDS_TYPE_LIST

            for i, chords_list in enumerate(CHORDS_TYPE_LIST, 1):
                if chord_name in chords_list:
                    return i
        except ImportError:
            pass

        # Альтернативный способ определения папки
        folder = self.chord_data.get_chord_folder(chord_name)
        if folder and folder.startswith('group_'):
            try:
                return int(folder.replace('group_', ''))
            except ValueError:
                pass
        return 1

    def get_chord_variants_by_name(self, chord_name, display_type="fingers"):
        """
        Возвращает варианты аккорда по имени с поддержкой типов отображения
        """
        variants_data = []
        variants = self.chord_manager.get_chord_variants(chord_name)

        if not variants:
            print(f"❌ Нет вариантов для аккорда {chord_name}")
            return []

        print(f"🎯 Обработка {len(variants)} вариантов для аккорда {chord_name}")

        for variant in variants:
            variant_index = variant.get('variant_index', 0)

            # Получаем данные с указанным типом отображения
            variant_data = self.chord_manager.get_chord_variant_data_with_pixmap(
                chord_name, variant_index, display_type
            )

            if variant_data and variant_data['pixmap'] and not variant_data['pixmap'].isNull():
                variants_data.append({
                    'position': variant.get('position', 1),
                    'chord_name': chord_name,
                    'pixmap': variant_data['pixmap'],
                    'sound_path': variant_data['sound_path'],
                    'description': variant_data['description'],
                    'display_type': display_type,
                    'variant_index': variant_index
                })
                print(f"✅ Вариант {variant.get('position', 1)}: {variant_data['description']}")

        # СОРТИРУЕМ ПО position чтобы первый вариант был первым
        variants_data.sort(key=lambda x: x['position'])
        print(f"🎯 Успешно загружено вариантов для {chord_name}: {len(variants_data)}")

        return variants_data

    def get_chord_image(self, chord_name, variant_index=0, display_type="fingers"):
        """
        Возвращает изображение аккорда как QPixmap
        """
        return self.chord_manager.get_chord_image(chord_name, variant_index, display_type)

    def get_chord_sound_path(self, chord_name, variant_index=0):
        """
        Возвращает путь к звуковому файлу аккорда
        """
        return self.chord_manager.get_chord_sound_path(chord_name, variant_index)

    def search_chords(self, query):
        """Поиск аккордов по запросу"""
        all_chords = self.chord_manager.get_available_chords()
        query = query.lower()

        results = []
        for chord in all_chords:
            if query in chord.lower():
                chord_info = self.get_chord_info(chord)
                if chord_info:
                    results.append(chord_info)

        return results

    def get_chord_description(self, chord_name):
        """Возвращает описание аккорда"""
        return self.chord_manager.get_chord_description(chord_name)

    def is_data_available(self):
        """Проверяет, доступны ли данные аккордов"""
        return self.chord_manager.is_data_loaded()

    def get_all_chords(self):
        """Возвращает список всех доступных аккордов"""
        return self.chord_manager.get_available_chords()

    def get_chords_by_folder(self, folder_num):
        """Возвращает аккорды из указанной папки"""
        return self.chord_manager.get_chords_by_folder(folder_num)

    def get_display_types(self):
        """Возвращает доступные типы отображения"""
        return self.chord_manager.get_display_types()

    def get_stats(self):
        """Возвращает статистику данных"""
        return self.chord_manager.get_stats()

    def get_chord_variants_count(self, chord_name):
        """Возвращает количество вариантов аккорда"""
        variants = self.chord_manager.get_chord_variants(chord_name)
        return len(variants) if variants else 0

    def get_chord_variant_info(self, chord_name, variant_index=0):
        """
        Возвращает информацию о конкретном варианте аккорда
        """
        variants = self.chord_manager.get_chord_variants(chord_name)
        if not variants or variant_index >= len(variants):
            return None

        variant = variants[variant_index]
        return {
            'position': variant.get('position', variant_index + 1),
            'description': variant.get('description', f'Вариант {variant_index + 1}'),
            'has_sound': bool(variant.get('sound_data')),
            'json_parameters': variant.get('json_parameters', {})
        }

    def check_chord_exists(self, chord_name):
        """Проверяет существование аккорда"""
        return chord_name in self.chord_manager.get_available_chords()

    def get_chord_categories(self):
        """Возвращает категории/папки аккордов"""
        all_chords = self.get_all_chords()
        categories = set()

        for chord in all_chords:
            folder = self.chord_data.get_chord_folder(chord)
            if folder:
                categories.add(folder)

        return sorted(list(categories))

    def get_chords_by_type(self, chord_type):
        """Возвращает аккорды по типу (major, minor, etc.)"""
        all_chords = self.get_all_chords()
        result = []

        for chord in all_chords:
            if self.chord_data.get_chord_type(chord).lower() == chord_type.lower():
                result.append(chord)

        return result