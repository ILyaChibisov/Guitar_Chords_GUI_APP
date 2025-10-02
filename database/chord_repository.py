"""
Репозиторий для работы с оптимизированными данными аккордов
"""

from core.chord_manager import ChordManager

class ChordRepository:
    """Репозиторий для доступа к данным аккордов"""

    def __init__(self):
        self.chord_manager = ChordManager()

    def get_chord_info(self, chord_name):
        """
        Возвращает информацию об аккорде в формате совместимом с БД
        """
        variants = self.chord_manager.get_chord_variants(chord_name)
        if not variants:
            return None

        chord_id = hash(chord_name) % 100000
        folder = f"folder_{self._get_folder_number(chord_name)}"

        return (chord_id, chord_name, folder, len(variants))

    def _get_folder_number(self, chord_name):
        """Определяет номер папки для аккорда"""
        try:
            from const import CHORDS_TYPE_LIST

            for i, chords_list in enumerate(CHORDS_TYPE_LIST, 1):
                if chord_name in chords_list:
                    return i
        except ImportError:
            pass
        return 1

    def get_chord_variants_by_name(self, chord_name):
        """
        Возвращает варианты аккорда по имени - ИСПРАВЛЕННАЯ ВЕРСИЯ
        """
        variants_data = []
        variants = self.chord_manager.get_chord_variants(chord_name)

        if not variants:
            print(f"❌ Нет вариантов для аккорда {chord_name}")
            return []

        for i, variant in enumerate(variants):
            variant_data = self.chord_manager.get_chord_variant_data(chord_name, i)

            # ✅ ВАЖНОЕ ИСПРАВЛЕНИЕ: показываем вариант даже если есть только изображение
            if variant_data and variant_data['image_path']:
                variants_data.append((
                    i + 1,  # position
                    chord_name,
                    variant_data['image_path'],
                    variant_data['sound_path'] if variant_data['sound_path'] else "",  # может быть None
                    variant_data['position']
                ))
                print(f"✅ Добавлен вариант {i+1} для {chord_name}: image={bool(variant_data['image_path'])}, sound={bool(variant_data['sound_path'])}")
            else:
                print(f"❌ Пропущен вариант {i+1} для {chord_name}: нет изображения")

        print(f"🎯 Всего вариантов для {chord_name}: {len(variants_data)}")
        return variants_data

    def search_chords(self, query):
        """Поиск аккордов по запросу"""
        all_chords = self.chord_manager.get_available_chords()
        query = query.lower()

        return [chord for chord in all_chords if query in chord.lower()]

    def get_chord_description(self, chord_name):
        """Возвращает описание аккорда"""
        return self.chord_manager.get_chord_description(chord_name)

    def is_data_available(self):
        """Проверяет, доступны ли данные аккордов"""
        return self.chord_manager.is_data_loaded()