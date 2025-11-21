# config/settings_chord_viewer.py
from PyQt5.QtGui import QColor


class ChordViewerSettings:
    """Настройки для окна просмотра аккордов"""

    # 🔧 НАСТРОЙКИ ОБВОДКИ И РАЗМЕРОВ
    OUTLINE_NOTE_WIDTH = 2  # Толщина обводки нот
    OUTLINE_BARRE_WIDTH = 2  # Толщина обводки баре
    OUTLINE_FRET_WIDTH = 1  # Толщина обводки ладов
    OUTLINE_OPEN_NOTE_WIDTH = 2  # Толщина обводки открытых струн

    OUTLINE_COLOR = [0, 0, 0]  # Цвет обводки [R, G, B]

    # 📏 НАСТРОЙКИ МАСШТАБИРОВАНИЯ
    SCALE_FACTOR = 0.5  # Масштаб рисунка (0.5 = 50% от оригинала)
    MIN_NOTE_RADIUS = 8  # Минимальный радиус ноты после масштабирования

    # 🎨 ЦВЕТА ТЕКСТА ДЛЯ РАЗМЕТКИ
    FRET_TEXT_COLOR = [0, 0, 0]  # Цвет текста ладов [R, G, B]
    NOTE_TEXT_COLOR = [255, 255, 255]  # Цвет текста нот [R, G, B]

    # 🔧 АДАПТИВНЫЙ ТЕКСТ
    ADAPTIVE_TEXT_ENABLED = True  # Включить автоподбор размера для длинных символов
    LONG_SYMBOL_RADIUS_REDUCTION = 2  # На сколько уменьшать радиус для длинных символов (C#, Bb и т.д.)

    # 🎭 СТИЛИ ОКНА
    WINDOW_STYLES = """
        QDialog {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #2c3e50, stop: 1 #34495e);
            color: #ecf0f1;
            font-family: 'Segoe UI', Arial, sans-serif;
        }

        #chord_title {
            color: white;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            padding: 10px 0px;
            background: transparent;
            border: none;
            margin: 0px;
        }

        #chord_description {
            color: #E0E0E0;
            font-size: 14px;
            text-align: center;
            padding: 5px 0px;
            background: transparent;
            border: none;
            margin: 0px;
        }

        #image_label {
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }

        #control_widget {
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }

        #variants_container {
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }

        #display_toggle_btn {
            background: rgba(52, 152, 219, 0.7);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            color: white;
            font-size: 12px;
            font-weight: bold;
            padding: 5px;
        }
        #display_toggle_btn:checked {
            background: rgba(231, 76, 60, 0.7);
            border: 2px solid rgba(255, 255, 255, 0.5);
        }
        #display_toggle_btn:hover {
            background: rgba(52, 152, 219, 0.9);
        }
        #display_toggle_btn:checked:hover {
            background: rgba(231, 76, 60, 0.9);
        }

        #sound_btn {
            background: rgba(46, 204, 113, 0.7);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            color: white;
            font-size: 12px;
            font-weight: bold;
            padding: 5px;
        }
        #sound_btn:hover {
            background: rgba(46, 204, 113, 0.9);
        }
        #sound_btn:disabled {
            background: rgba(149, 165, 166, 0.7);
            color: rgba(127, 140, 141, 0.7);
        }
    """

    # 🎯 НАСТРОЙКИ РАЗМЕРОВ ОКНА
    WINDOW_MIN_SIZE = (500, 600)  # Минимальный размер окна
    IMAGE_LABEL_MIN_SIZE = (400, 300)  # Минимальный размер области изображения

    # 🔊 НАСТРОЙКИ ЗВУКА
    SOUND_BUTTON_RESTORE_DELAY = 2000  # Задержка восстановления кнопки звука (мс)

    @classmethod
    def get_outline_color_qcolor(cls):
        """Получить QColor для обводки"""
        return QColor(*cls.OUTLINE_COLOR)

    @classmethod
    def get_fret_text_color_qcolor(cls):
        """Получить QColor для текста ладов"""
        return QColor(*cls.FRET_TEXT_COLOR)

    @classmethod
    def get_note_text_color_qcolor(cls):
        """Получить QColor для текста нот"""
        return QColor(*cls.NOTE_TEXT_COLOR)

    @classmethod
    def update_setting(cls, setting_name, value):
        """Обновить настройку по имени"""
        if hasattr(cls, setting_name):
            setattr(cls, setting_name, value)
            print(f"✅ Настройка {setting_name} обновлена: {value}")
        else:
            print(f"❌ Настройка {setting_name} не найдена")

    @classmethod
    def get_all_settings(cls):
        """Получить все настройки в виде словаря"""
        return {key: value for key, value in cls.__dict__.items()
                if not key.startswith('_') and not callable(value)}