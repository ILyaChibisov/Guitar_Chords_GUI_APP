from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from config.styles import DarkTheme


class ModernButton(QPushButton):
    """Современная кнопка с градиентом"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(DarkTheme.MODERN_BUTTON_STYLE)


class MenuButton(QPushButton):
    """Кнопка для главного меню"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(40)
        self.setStyleSheet(DarkTheme.MENU_BUTTON_STYLE)


class ChordButton(QPushButton):
    """Кнопка аккорда"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(DarkTheme.CHORD_BUTTON_STYLE)


class ChordVariantButton(QPushButton):
    """Кнопка варианта аккорда"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(35, 35)
        self.setCheckable(True)
        self.update_style()

    def update_style(self):
        if self.isChecked():
            self.setStyleSheet("""
                QPushButton {
                    background: #1B5E20;
                    color: white;
                    border: 2px solid #004D40;
                    border-radius: 17px;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #4CAF50, stop: 1 #45a049);
                    color: white;
                    border: 2px solid #388E3C;
                    border-radius: 17px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #43A047, stop: 1 #3d8b40);
                    border: 2px solid #2E7D32;
                }
                QPushButton:pressed {
                    background: #2E7D32;
                }
            """)


class SoundButtonLarge(QPushButton):
    """Большая кнопка воспроизведения звука"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(45)
        self.setStyleSheet(DarkTheme.SOUND_BUTTON_STYLE)