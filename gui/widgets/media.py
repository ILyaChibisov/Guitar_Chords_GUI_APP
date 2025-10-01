from PyQt5.QtWidgets import QScrollArea, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt


class ScrollChordButtonsWidget(QScrollArea):
    """Прокручиваемая область для кнопок аккордов"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Создаем внутренний виджет для кнопок
        self.scroll_widget = QWidget()
        self.chords_layout = QHBoxLayout(self.scroll_widget)
        self.chords_layout.setSpacing(5)
        self.chords_layout.setContentsMargins(5, 5, 5, 5)
        self.chords_layout.setAlignment(Qt.AlignCenter)

        # Настраиваем ScrollArea
        self.setWidget(self.scroll_widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)