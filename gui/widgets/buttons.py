from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
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


class PaginationButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(45, 45)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2c3e50, stop: 1 #34495e);
                color: white;
                border: 2px solid #1c2833;
                border-radius: 22px;
                font-weight: bold;
                font-size: 16px;
                margin: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
                border: 2px solid #2471a3;
                font-size: 18px;
            }
            QPushButton:pressed {
                background: #2471a3;
                border: 2px solid #1c5a85;
            }
            QPushButton:disabled {
                background: #34495e;
                color: #7f8c8d;
                border: 2px solid #2c3e50;
            }
        """)

# TODO проверить другие варианты:

# ==================== ВАРИАНТЫ СТРЕЛОК С ОБРАМЛЕНИЕМ ====================

class PaginationButtonGlass(QPushButton):
    """ВАРИАНТ 1: Стеклянный эффект с градиентом"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(50, 50)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(52, 152, 219, 0.8),
                    stop: 0.5 rgba(41, 128, 185, 0.9),
                    stop: 1 rgba(52, 152, 219, 0.8));
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 25px;
                font-weight: bold;
                font-size: 18px;
                margin: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(93, 173, 226, 0.9),
                    stop: 0.5 rgba(52, 152, 219, 1),
                    stop: 1 rgba(93, 173, 226, 0.9));
                border: 2px solid rgba(255, 255, 255, 0.5);
                font-size: 20px;
            }
            QPushButton:pressed {
                background: rgba(36, 113, 163, 0.9);
                border: 2px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton:disabled {
                background: rgba(52, 73, 94, 0.5);
                color: rgba(127, 140, 141, 0.7);
                border: 2px solid rgba(44, 62, 80, 0.5);
            }
        """)


class PaginationButtonNeon(QPushButton):
    """ВАРИАНТ 2: Неоновое свечение"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(50, 50)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #9b59b6, stop: 1 #8e44ad);
                color: white;
                border: 2px solid #9b59b6;
                border-radius: 25px;
                font-weight: bold;
                font-size: 18px;
                margin: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #a569bd, stop: 1 #9b59b6);
                border: 2px solid #e74c3c;
                box-shadow: 0 0 10px rgba(231, 76, 60, 0.7);
                font-size: 20px;
            }
            QPushButton:pressed {
                background: #7d3c98;
                border: 2px solid #c0392b;
                box-shadow: 0 0 15px rgba(231, 76, 60, 0.9);
            }
            QPushButton:disabled {
                background: rgba(52, 73, 94, 0.5);
                color: rgba(127, 140, 141, 0.7);
                border: 2px solid rgba(44, 62, 80, 0.5);
                box-shadow: none;
            }
        """)


class PaginationButtonMetallic(QPushButton):
    """ВАРИАНТ 3: Металлический хром"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(50, 50)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #bdc3c7, stop: 0.4 #95a5a6, stop: 0.6 #7f8c8d, stop: 1 #95a5a6);
                color: #2c3e50;
                border: 3px solid #7f8c8d;
                border-radius: 25px;
                font-weight: bold;
                font-size: 18px;
                margin: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ecf0f1, stop: 0.4 #bdc3c7, stop: 0.6 #95a5a6, stop: 1 #bdc3c7);
                border: 3px solid #3498db;
                font-size: 20px;
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #95a5a6, stop: 0.4 #7f8c8d, stop: 0.6 #95a5a6, stop: 1 #7f8c8d);
                border: 3px solid #2980b9;
            }
            QPushButton:disabled {
                background: rgba(189, 195, 199, 0.3);
                color: rgba(44, 62, 80, 0.5);
                border: 3px solid rgba(127, 140, 141, 0.3);
            }
        """)


class PaginationButtonGradientBorder(QPushButton):
    """ВАРИАНТ 4: Градиентная рамка"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(52, 52)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2c3e50, stop: 1 #34495e);
                color: white;
                border: 3px solid qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #e74c3c, stop: 0.5 #3498db, stop: 1 #2ecc71);
                border-radius: 26px;
                font-weight: bold;
                font-size: 18px;
                margin: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #34495e, stop: 1 #2c3e50);
                border: 3px solid qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f39c12, stop: 0.5 #9b59b6, stop: 1 #1abc9c);
                font-size: 20px;
            }
            QPushButton:pressed {
                background: #2c3e50;
                border: 3px solid qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #d35400, stop: 0.5 #2980b9, stop: 1 #16a085);
            }
            QPushButton:disabled {
                background: rgba(44, 62, 80, 0.5);
                color: rgba(255, 255, 255, 0.5);
                border: 3px solid rgba(127, 140, 141, 0.3);
            }
        """)


class PaginationButtonShadow(QPushButton):
    """ВАРИАНТ 5: Объемная тень"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(50, 50)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #27ae60, stop: 1 #229954);
                color: white;
                border: none;
                border-radius: 25px;
                font-weight: bold;
                font-size: 18px;
                margin: 2px;

                /* Объемная тень */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3),
                            inset 0 1px 0 rgba(255, 255, 255, 0.2),
                            inset 0 -1px 0 rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #58d68d, stop: 1 #27ae60);
                font-size: 20px;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3),
                            inset 0 -1px 0 rgba(0, 0, 0, 0.3);
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: #1e8449;
                font-size: 18px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3),
                            inset 0 1px 0 rgba(255, 255, 255, 0.1),
                            inset 0 -1px 0 rgba(0, 0, 0, 0.4);
                transform: translateY(1px);
            }
            QPushButton:disabled {
                background: rgba(39, 174, 96, 0.3);
                color: rgba(255, 255, 255, 0.5);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }
        """)


class PaginationButtonOutline(QPushButton):
    """ВАРИАНТ 6: Контурный стиль"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(50, 50)
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #3498db;
                border: 3px solid #3498db;
                border-radius: 25px;
                font-weight: bold;
                font-size: 18px;
                margin: 2px;
            }
            QPushButton:hover {
                background: rgba(52, 152, 219, 0.1);
                color: #2980b9;
                border: 3px solid #2980b9;
                font-size: 20px;
            }
            QPushButton:pressed {
                background: rgba(52, 152, 219, 0.2);
                color: #2471a3;
                border: 3px solid #2471a3;
            }
            QPushButton:disabled {
                background: transparent;
                color: rgba(52, 152, 219, 0.3);
                border: 3px solid rgba(52, 152, 219, 0.3);
            }
        """)


class PaginationButtonGlow(QPushButton):
    """ВАРИАНТ 7: Светящийся эффект"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(50, 50)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e67e22, stop: 1 #d35400);
                color: white;
                border: 2px solid #e67e22;
                border-radius: 25px;
                font-weight: bold;
                font-size: 18px;
                margin: 2px;

                /* Свечение */
                box-shadow: 0 0 5px rgba(230, 126, 34, 0.5),
                            inset 0 0 10px rgba(255, 255, 255, 0.1);
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f39c12, stop: 1 #e67e22);
                border: 2px solid #f39c12;
                font-size: 20px;
                box-shadow: 0 0 15px rgba(243, 156, 18, 0.8),
                            inset 0 0 15px rgba(255, 255, 255, 0.2);
            }
            QPushButton:pressed {
                background: #d35400;
                border: 2px solid #d35400;
                box-shadow: 0 0 20px rgba(211, 84, 0, 0.9),
                            inset 0 0 5px rgba(255, 255, 255, 0.1);
            }
            QPushButton:disabled {
                background: rgba(230, 126, 34, 0.3);
                color: rgba(255, 255, 255, 0.5);
                border: 2px solid rgba(230, 126, 34, 0.3);
                box-shadow: none;
            }
        """)


class PaginationButtonModern3D(QPushButton):
    """ВАРИАНТ 8: 3D эффект"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(50, 50)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 0.1 #2980b9, stop: 0.9 #2471a3, stop: 1 #2980b9);
                color: white;
                border: none;
                border-radius: 25px;
                font-weight: bold;
                font-size: 18px;
                margin: 2px;

                /* 3D эффект */
                border-bottom: 4px solid #1c5a85;
                border-right: 2px solid #1c5a85;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5dade2, stop: 0.1 #3498db, stop: 0.9 #2980b9, stop: 1 #3498db);
                font-size: 20px;
                border-bottom: 3px solid #1c5a85;
                border-right: 1px solid #1c5a85;
                transform: translateY(1px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2471a3, stop: 0.1 #1c5a85, stop: 0.9 #2471a3, stop: 1 #1c5a85);
                font-size: 18px;
                border-bottom: 1px solid #1c5a85;
                border-right: 0px solid #1c5a85;
                transform: translateY(3px);
            }
            QPushButton:disabled {
                background: rgba(52, 152, 219, 0.3);
                color: rgba(255, 255, 255, 0.5);
                border-bottom: 4px solid rgba(28, 90, 133, 0.3);
                border-right: 2px solid rgba(28, 90, 133, 0.3);
            }
        """)

