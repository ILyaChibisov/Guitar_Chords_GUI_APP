class DarkTheme:
    """Темная тема приложения"""

    MAIN_STYLESHEET = """
    /* ОСНОВНОЙ ФОН ВСЕГО ПРИЛОЖЕНИЯ */
    QMainWindow, QWidget, QDialog {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 #2c3e50, stop: 1 #34495e);
        color: #ecf0f1;
        font-family: 'Segoe UI', Arial, sans-serif;
    }

    /* ФОН ДЛЯ ВСЕХ ФРЕЙМОВ И КОНТЕЙНЕРОВ */
    QFrame, QScrollArea, QGroupBox {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 #2c3e50, stop: 1 #34495e);
        color: #ecf0f1;
        border: none;
    }

    QLineEdit {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 12px 20px;
        color: white;
        font-size: 14px;
        selection-background-color: #3498db;
    }

    QLineEdit:focus {
        border: 2px solid #3498db;
        background: rgba(255, 255, 255, 0.15);
    }

    QListWidget {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 10px;
        color: white;
        font-size: 13px;
        outline: none;
    }

    QListWidget::item {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 12px;
        margin: 2px;
    }

    QListWidget::item:selected {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #3498db, stop: 1 #2980b9);
    }

    QListWidget::item:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    QTextBrowser {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        color: white;
        font-size: 13px;
        line-height: 1.4;
    }

    QScrollBar:vertical {
        background: rgba(255, 255, 255, 0.1);
        width: 12px;
        border-radius: 6px;
    }

    QScrollBar:horizontal {
        background: rgba(255, 255, 255, 0.1);
        height: 12px;
        border-radius: 6px;
    }

    QScrollBar::handle:vertical {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 6px;
        min-height: 20px;
    }

    QScrollBar::handle:horizontal {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 6px;
        min-width: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background: rgba(255, 255, 255, 0.5);
    }

    QScrollBar::handle:horizontal:hover {
        background: rgba(255, 255, 255, 0.5);
    }
    """

    # Стили для кнопок
    MODERN_BUTTON_STYLE = """
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #667eea, stop: 1 #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 11px;
        }
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #5a6fd8, stop: 1 #6a4190);
        }
        QPushButton:pressed {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #4c5bc6, stop: 1 #58357e);
        }
    """

    MENU_BUTTON_STYLE = """
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #3498db, stop: 1 #2980b9);
            color: white;
            border: none;
            border-radius: 20px;
            font-weight: bold;
            font-size: 12px;
            padding: 0px 20px;
            margin: 0px 5px;
        }
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #5dade2, stop: 1 #3498db);
        }
        QPushButton:pressed {
            background: #2471a3;
        }
    """

    CHORD_BUTTON_STYLE = """
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #3498db, stop: 1 #2980b9);
            color: white;
            border: 2px solid #2471a3;
            border-radius: 15px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 11px;
            margin: 2px;
        }
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #5dade2, stop: 1 #3498db);
            border: 2px solid #2e86c1;
        }
        QPushButton:pressed {
            background: #2471a3;
        }
    """

    SOUND_BUTTON_STYLE = """
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #2980b9, stop: 1 #1c5a85);
            color: white;
            border: none;
            border-radius: 22px;
            font-weight: bold;
            font-size: 14px;
            padding: 0px 25px;
        }
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #3498db, stop: 1 #2980b9);
        }
        QPushButton:pressed {
            background: #1c5a85;
        }
    """

    PAGINATION_BUTTON_STYLE = """
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #5a6fd8, stop: 1 #6a4190);
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: bold;
            font-size: 14px;
            min-width: 35px;
            min-height: 40px;
        }
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #667eea, stop: 1 #764ba2);
        }
        QPushButton:pressed {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #4c5bc6, stop: 1 #58357e);
        }
        QPushButton:disabled {
            background: #34495e;
            color: #7f8c8d;
        }
    """

    CHORD_IMAGE_LABEL_STYLE = """
        QLabel {
            background: rgba(255, 255, 255, 0.05);
            border: 2px dashed rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 15px;
            min-width: 200px;
            min-height: 300px;
        }
        QLabel:hover {
            border: 2px dashed rgba(255, 255, 255, 0.4);
        }
    """

    SONG_TITLE_STYLE = """
        QLabel {
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 5px 0px;
            text-align: center;
            background: transparent;
            border: none;
        }
    """

    CHORD_TITLE_STYLE = """
        QLabel {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #4CAF50, stop: 1 #45a049);
            color: white;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            padding: 8px 15px;
            border-radius: 20px;
            margin: 5px;
        }
    """