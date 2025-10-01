class DarkTheme:
    """Темная тема приложения"""

    MAIN_STYLESHEET = """
    QWidget {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 #2c3e50, stop: 1 #34495e);
        color: #ecf0f1;
        font-family: 'Segoe UI', Arial, sans-serif;
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