from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os

from gui.widgets.buttons import SoundButtonLarge, ModernButton, ChordVariantButton

class ChordViewerWindow(QWidget):
    def __init__(self, chord_name, image_path, mp3_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Аккорд {chord_name}")
        self.setFixedSize(450, 550)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2c3e50, stop: 1 #34495e);
                color: #ecf0f1;
            }
        """)

        self.mp3_path = mp3_path
        self.player = QMediaPlayer()

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок с названием аккорда по центру (зеленый цвет)
        chord_title = QLabel(chord_name)
        chord_title.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 22px;
                font-weight: bold;
                text-align: center;
                padding: 10px;
            }
        """)
        chord_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(chord_title)

        # Изображение аккорда
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(300, 300)
        self.image_label.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                padding: 20px;
            }
        """)

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        layout.addWidget(self.image_label)

        # Кнопки вариантов аппликатуры
        self.variants_layout = QHBoxLayout()
        self.variants_layout.setAlignment(Qt.AlignCenter)
        self.variants_layout.setSpacing(10)

        variants_container = QWidget()
        variants_container.setLayout(self.variants_layout)
        layout.addWidget(variants_container)

        # Кнопка слушать (под кнопками вариантов)
        self.sound_button = SoundButtonLarge()
        self.sound_button.setText("🔈 Слушать")
        self.sound_button.clicked.connect(self.play_chord_sound)
        layout.addWidget(self.sound_button, 0, Qt.AlignCenter)

        close_btn = ModernButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        layout.addStretch()

    def play_chord_sound(self):
        if self.mp3_path and os.path.exists(self.mp3_path):
            url = QUrl.fromLocalFile(self.mp3_path)
            self.player.setMedia(QMediaContent(url))
            self.player.play()

    def add_variant_buttons(self, variants_data):
        """Добавляет кнопки вариантов аппликатуры"""
        for idx, (img_path, mp3_path) in enumerate(variants_data):
            btn = ChordVariantButton(str(idx + 1))

            def make_handler(variant_img_path, variant_mp3_path, button):
                def handler():
                    pixmap = QPixmap(variant_img_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.image_label.setPixmap(scaled_pixmap)
                    self.mp3_path = variant_mp3_path

                    # Сброс выделения других кнопок и установка текущей
                    for i in range(self.variants_layout.count()):
                        other_btn = self.variants_layout.itemAt(i).widget()
                        if other_btn:
                            other_btn.setChecked(False)
                            other_btn.update_style()
                    button.setChecked(True)
                    button.update_style()

                return handler

            handler = make_handler(img_path, mp3_path, btn)
            btn.clicked.connect(handler)
            self.variants_layout.addWidget(btn)

            # Активируем первый вариант
            if idx == 0:
                btn.setChecked(True)
                btn.update_style()