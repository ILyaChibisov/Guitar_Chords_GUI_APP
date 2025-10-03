from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap
from config.styles import DarkTheme


class ClickableLabel(QLabel):
    """Кликабельная метка с сигналом"""

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
        self.setStyleSheet(DarkTheme.CHORD_IMAGE_LABEL_STYLE)


class AdaptiveChordLabel(ClickableLabel):
    """Адаптивная метка для изображения аккорда, подстраивающаяся под размеры"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(150, 200)  # Минимальный размер
        self._original_pixmap = None
        self.setStyleSheet(DarkTheme.CHORD_IMAGE_LABEL_STYLE)

    def setChordPixmap(self, pixmap):
        """Устанавливает изображение аккорда и сохраняет оригинал"""
        self._original_pixmap = pixmap
        self.updatePixmap()

    def updatePixmap(self):
        """Обновляет изображение с учетом текущего размера"""
        if self._original_pixmap and not self._original_pixmap.isNull():
            # Вычисляем доступный размер с учетом отступов
            available_size = self.size() - QSize(20, 20)  # Учитываем padding
            scaled_pixmap = self._original_pixmap.scaled(
                available_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        else:
            self.clear()

    def resizeEvent(self, event):
        """Обработчик изменения размера"""
        self.updatePixmap()
        super().resizeEvent(event)