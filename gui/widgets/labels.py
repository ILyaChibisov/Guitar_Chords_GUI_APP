from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, pyqtSignal


class ClickableLabel(QLabel):
    """Кликабельная метка"""

    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class ChordImageLabel(ClickableLabel):
    """Метка для изображения аккорда"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            ChordImageLabel {
                background: rgba(255, 255, 255, 0.05);
                border: 2px dashed rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                padding: 15px;
                min-width: 200px;
                min-height: 300px;
            }
            ChordImageLabel:hover {
                border: 2px dashed rgba(255, 255, 255, 0.4);
            }
        """)