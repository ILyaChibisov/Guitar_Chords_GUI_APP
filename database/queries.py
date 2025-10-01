import database.db_scripts as db


class SongQueries:
    """Класс для запросов к песням"""

    @staticmethod
    def search_songs(query):
        """Поиск песен по запросу"""
        return db.select_search_text(query)

    @staticmethod
    def get_song_info(title):
        """Получение информации о песне"""
        return db.select_chord_song_info(title)


class ChordQueries:
    """Класс для запросов к аккордам"""

    @staticmethod
    def get_chord_info(chord_name):
        """Получение информации об аккорде"""
        return db.select_chord_info(chord_name)

    @staticmethod
    def get_chord_variants(chord_id):
        """Получение вариантов аккорда"""
        return db.select_chord_variants(chord_id)