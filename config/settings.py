import os


class AppSettings:
    # Основные настройки приложения
    APP_NAME = "🎸 GuitarChords Pro"
    APP_VERSION = "1.0.0"
    DEFAULT_WINDOW_SIZE = (1200, 900)
    MIN_WINDOW_SIZE = (1000, 700)

    # Пути к ресурсам
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_PATH = os.path.join(PROJECT_ROOT, "db_script", "database.py")

    # Настройки медиа
    SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg']
    SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav']

    # Размеры элементов UI
    CHORD_IMAGE_SIZE = (200, 300)
    LARGE_CHORD_IMAGE_SIZE = (300, 300)
    SCROLL_AREA_HEIGHT = 60


class DatabaseConfig:
    # Конфигурация базы данных
    TABLE_SONGS = "songs"
    TABLE_CHORDS = "chords"
    TABLE_CHORD_VARIANTS = "chord_variants"