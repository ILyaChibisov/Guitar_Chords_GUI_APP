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

        # Пробуем разные варианты написания
        names_to_try = [
            chord_name.upper(),
            chord_name.upper().replace('M', '').replace('М', ''),
            chord_name.upper().replace('M', 'm').replace('М', 'm'),
        ]

        for name in names_to_try:
            if name in CHORDS_DATA:
                return CHORDS_DATA[name]

        return None

    @classmethod
    def get_all_chords(cls):
        """Возвращает список всех доступных аккордов"""
        from .chords_data import CHORDS_DATA
        return list(CHORDS_DATA.keys())

    @classmethod
    def get_chords_by_folder(cls, folder_num):
        """Возвращает аккорды из указанной папки"""
        from .chords_data import CHORDS_DATA
        folder_name = f"folder_{folder_num}"
        return [chord for chord, data in CHORDS_DATA.items()
                if data.get("folder") == folder_name]

    @classmethod
    def get_chord_description(cls, chord_name):
        """Возвращает описание аккорда"""
        chord_data = cls.get_chord_data(chord_name)
        return chord_data.get("description", "") if chord_data else ""

    @classmethod
    def is_data_available(cls):
        """Проверяет, доступны ли данные аккордов"""
        from .chords_data import CHORDS_DATA
        return len(CHORDS_DATA) > 0