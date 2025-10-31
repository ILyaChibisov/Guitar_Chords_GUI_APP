"""
Класс для работы с данными аккордов
"""

import base64

class ChordData:
    """Класс для работы с данными аккордов"""

    @classmethod
    def get_chord_data(cls, chord_name):
        """Возвращает данные аккорда по имени"""
        from data.chords_data import CHORDS_DATA

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
        """Возвращает список всех доступных аккордов"""
        from data.chords_data import CHORDS_DATA
        chords_dict = CHORDS_DATA.get('chords', {})
        return list(chords_dict.keys())

    @classmethod
    def get_chords_by_folder(cls, folder_num):
        """Возвращает аккорды из указанной папки"""
        from data.chords_data import CHORDS_DATA
        chords_dict = CHORDS_DATA.get('chords', {})
        folder_name = f'group_{folder_num}'
        return [chord for chord, data in chords_dict.items()
                if data.get('folder') == folder_name]

    @classmethod
    def get_chord_description(cls, chord_name):
        """Возвращает описание аккорда"""
        chord_data = cls.get_chord_data(chord_name)
        if chord_data:
            return chord_data.get('description', f'Аккорд {chord_name}')
        return f'Аккорд {chord_name}'

    @classmethod
    def is_data_available(cls):
        """Проверяет, доступны ли данные аккордов"""
        from data.chords_data import CHORDS_DATA
        chords_dict = CHORDS_DATA.get('chords', {})
        return len(chords_dict) > 0

    @classmethod
    def get_template_image(cls):
        """Получить шаблон изображения"""
        from data.chords_data import CHORDS_DATA
        return CHORDS_DATA.get('template_image')

    @classmethod
    def get_display_types(cls):
        """Получить доступные типы отображения"""
        return ["fingers", "notes"]

    @classmethod
    def get_original_json_config(cls):
        """Получить оригинальную JSON конфигурацию"""
        from data.chords_data import CHORDS_DATA
        return CHORDS_DATA.get('original_json_config', {})

    @classmethod
    def get_stats(cls):
        """Получить статистику данных"""
        from data.chords_data import CHORDS_DATA
        chords_dict = CHORDS_DATA.get('chords', {})
        metadata = CHORDS_DATA.get('metadata', {})

        return {
            'total_chords': len(chords_dict),
            'template_size_kb': metadata.get('template_size', 0) / 1024,
            'has_template': bool(CHORDS_DATA.get('template_image')),
            'has_json_config': bool(CHORDS_DATA.get('original_json_config')),
            'converter_version': metadata.get('converter_version', 'unknown')
        }

    @classmethod
    def get_chord_variants(cls, chord_name):
        """Получить варианты аккорда"""
        chord_data = cls.get_chord_data(chord_name)
        if chord_data:
            return chord_data.get('variants', [])
        return []

    @classmethod
    def get_chord_type(cls, chord_name):
        """Получить тип аккорда (major, minor, etc.)"""
        chord_data = cls.get_chord_data(chord_name)
        if chord_data:
            return chord_data.get('type', 'major')
        return 'major'

    @classmethod
    def get_chord_folder(cls, chord_name):
        """Получить папку аккорда"""
        chord_data = cls.get_chord_data(chord_name)
        if chord_data:
            return chord_data.get('folder', 'unknown')
        return 'unknown'

    @classmethod
    def get_metadata(cls):
        """Получить метаданные"""
        from data.chords_data import CHORDS_DATA
        return CHORDS_DATA.get('metadata', {})