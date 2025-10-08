from PyQt5.QtWidgets import QScrollArea, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve


class ScrollChordButtonsWidget(QScrollArea):
    """Прокручиваемая область для кнопок аккордов с анимацией"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Создаем внутренний виджет для кнопок
        self.scroll_widget = QWidget()
        self.chords_layout = QHBoxLayout(self.scroll_widget)
        self.chords_layout.setSpacing(8)
        self.chords_layout.setContentsMargins(15, 5, 15, 5)
        self.chords_layout.setAlignment(Qt.AlignCenter)

        # Настраиваем ScrollArea
        self.setWidget(self.scroll_widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFixedHeight(70)
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QWidget {
                background: transparent;
            }
        """)

        # Анимация для плавного перемещения
        self.animation = QPropertyAnimation(self.horizontalScrollBar(), b"value")
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(300)

    def scroll_to_center(self):
        """Плавная прокрутка к центру"""
        scrollbar = self.horizontalScrollBar()
        if scrollbar.maximum() > 0:
            target_value = (scrollbar.maximum() - scrollbar.minimum()) // 2
            self.animation.setStartValue(scrollbar.value())
            self.animation.setEndValue(target_value)
            self.animation.start()