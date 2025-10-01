from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt


class ModernButton(QPushButton):
    """Современная кнопка с градиентом"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
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
        """)


class MenuButton(QPushButton):
    """Кнопка для главного меню"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(40)
        self.setStyleSheet("""
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
        """)


class ChordButton(QPushButton):
    """Кнопка аккорда"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
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
        """)


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
        self.setStyleSheet("""
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
        """)