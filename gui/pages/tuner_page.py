import sys
import numpy as np
import pyaudio
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QFont
from scipy import signal
import warnings

warnings.filterwarnings('ignore')


class AnimatedNoteLabel(QtWidgets.QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self._scale = 1.0
        self._opacity = 1.0

        self.scale_animation = QPropertyAnimation(self, b"scale")
        self.scale_animation.setDuration(500)
        self.scale_animation.setLoopCount(-1)

        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.opacity_animation.setDuration(1000)
        self.opacity_animation.setLoopCount(-1)

    def get_scale(self):
        return self._scale

    def set_scale(self, value):
        self._scale = value
        self.update()

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):
        self._opacity = value
        self.update()

    scale = pyqtProperty(float, get_scale, set_scale)
    opacity = pyqtProperty(float, get_opacity, set_opacity)

    def start_animations(self):
        self.scale_animation.setStartValue(0.8)
        self.scale_animation.setEndValue(1.2)
        self.scale_animation.start()

        self.opacity_animation.setStartValue(0.6)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()

    def stop_animations(self):
        self.scale_animation.stop()
        self.opacity_animation.stop()
        self._scale = 1.0
        self._opacity = 1.0
        self.update()


class TuningMeter(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 120)
        self._value = 0
        self._is_in_tune = False

    def set_value(self, value):
        self._value = max(-100, min(100, value))
        self._is_in_tune = abs(value) <= 5
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Фон
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(255, 50, 50))
        gradient.setColorAt(0.4, QColor(255, 255, 100))
        gradient.setColorAt(0.5, QColor(100, 255, 100))
        gradient.setColorAt(0.6, QColor(255, 255, 100))
        gradient.setColorAt(1, QColor(255, 50, 50))

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 30, self.width(), 40, 20, 20)

        # Центральная линия
        painter.setPen(Qt.white)
        painter.drawLine(self.width() // 2, 30, self.width() // 2, 70)

        # Ползунок
        x_pos = self.width() // 2 + (self._value * self.width() // 200)
        color = QColor(100, 255, 100) if self._is_in_tune else QColor(255, 100, 100)

        painter.setBrush(color)
        painter.setPen(Qt.black)
        painter.drawEllipse(x_pos - 10, 20, 20, 60)

        # Подписи
        painter.setPen(Qt.white)
        painter.drawText(10, 90, "-50")
        painter.drawText(self.width() // 2 - 10, 90, "0")
        painter.drawText(self.width() - 30, 90, "+50")


class SpectrumWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 200)
        self.spectrum_data = np.zeros(100)

    def update_spectrum(self, data):
        self.spectrum_data = data
        self.update()

    def paintEvent(self, event):
        if len(self.spectrum_data) == 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Фон
        painter.fillRect(self.rect(), QColor(30, 30, 40))

        # Отрисовка спектра
        width = self.width()
        height = self.height()
        bar_width = width / len(self.spectrum_data)

        painter.setPen(Qt.NoPen)
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(100, 200, 255))
        gradient.setColorAt(1, QColor(50, 100, 200))
        painter.setBrush(gradient)

        for i, value in enumerate(self.spectrum_data):
            bar_height = min(value * height * 2, height - 10)
            x = i * bar_width
            painter.drawRect(int(x), int(height - bar_height),
                             int(bar_width - 1), int(bar_height))


class UniversalGuitarTuner(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.tunings = {
            "Стандарт (6 струн)": ['E2', 'A2', 'D3', 'G3', 'B3', 'E4'],
            "Drop D": ['D2', 'A2', 'D3', 'G3', 'B3', 'E4'],
            "Полутон ниже": ['D#2', 'G#2', 'C#3', 'F#3', 'A#3', 'D#4'],
            "7-струнная": ['B1', 'E2', 'A2', 'D3', 'G3', 'B3', 'E4'],
            "Бас-гитара (4стр)": ['E1', 'A1', 'D2', 'G2'],
            "Бас-гитара (5стр)": ['B0', 'E1', 'A1', 'D2', 'G2'],
            "Укулеле сопрано": ['G4', 'C4', 'E4', 'A4'],
            "Укулеле баритон": ['D3', 'G3', 'B3', 'E4']
        }

        self.note_frequencies = {
            'C0': 16.35, 'C#0': 17.32, 'D0': 18.35, 'D#0': 19.45, 'E0': 20.60, 'F0': 21.83,
            'F#0': 23.12, 'G0': 24.50, 'G#0': 25.96, 'A0': 27.50, 'A#0': 29.14, 'B0': 30.87,
            'C1': 32.70, 'C#1': 34.65, 'D1': 36.71, 'D#1': 38.89, 'E1': 41.20, 'F1': 43.65,
            'F#1': 46.25, 'G1': 49.00, 'G#1': 51.91, 'A1': 55.00, 'A#1': 58.27, 'B1': 61.74,
            'C2': 65.41, 'C#2': 69.30, 'D2': 73.42, 'D#2': 77.78, 'E2': 82.41, 'F2': 87.31,
            'F#2': 92.50, 'G2': 98.00, 'G#2': 103.83, 'A2': 110.00, 'A#2': 116.54, 'B2': 123.47,
            'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56, 'E3': 164.81, 'F3': 174.61,
            'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00, 'A#3': 233.08, 'B3': 246.94,
            'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63, 'F4': 349.23,
            'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
            'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25, 'E5': 659.25, 'F5': 698.46,
            'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77
        }

        self.current_tuning = "Стандарт (6 струн)"
        self.init_ui()
        self.init_audio()

    def init_ui(self):
        self.setWindowTitle("🎸 Универсальный гитарный тюнер")
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
            }
            QLabel {
                color: white;
                font-family: Arial;
            }
            QComboBox, QPushButton {
                background: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 14px;
            }
            QComboBox:hover, QPushButton:hover {
                background: #2980b9;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #34495e;
                color: white;
                selection-background-color: #3498db;
            }
        """)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout()

        # Заголовок
        title = QtWidgets.QLabel("🎵 УНИВЕРСАЛЬНЫЙ ГИТАРНЫЙ ТЮНЕР")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #f39c12; margin: 20px;")
        layout.addWidget(title)

        # Выбор строя
        tuning_layout = QtWidgets.QHBoxLayout()
        tuning_layout.addWidget(QtWidgets.QLabel("Строй:"))
        self.tuning_combo = QtWidgets.QComboBox()
        self.tuning_combo.addItems(self.tunings.keys())
        self.tuning_combo.currentTextChanged.connect(self.change_tuning)
        tuning_layout.addWidget(self.tuning_combo)
        tuning_layout.addStretch()
        layout.addLayout(tuning_layout)

        # Отображение текущей ноты с анимацией
        self.note_display = AnimatedNoteLabel("--")
        self.note_display.setAlignment(Qt.AlignCenter)
        self.note_display.setStyleSheet("""
            font-size: 72px; 
            font-weight: bold; 
            color: #e74c3c;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 20px;
            margin: 20px;
        """)
        layout.addWidget(self.note_display)

        # Отображение частоты
        self.freq_display = QtWidgets.QLabel("0.0 Hz")
        self.freq_display.setAlignment(Qt.AlignCenter)
        self.freq_display.setStyleSheet("font-size: 24px; color: #ecf0f1; margin: 10px;")
        layout.addWidget(self.freq_display)

        # Индикатор точности
        self.tuning_meter = TuningMeter()
        layout.addWidget(self.tuning_meter)

        # Визуализация спектра
        self.spectrum_widget = SpectrumWidget()
        layout.addWidget(self.spectrum_widget)

        # Отображение струн текущего строя
        self.strings_display = QtWidgets.QWidget()
        self.strings_layout = QtWidgets.QHBoxLayout()
        self.strings_display.setLayout(self.strings_layout)
        layout.addWidget(self.strings_display)

        self.update_strings_display()

        central_widget.setLayout(layout)

    def update_strings_display(self):
        # Очищаем предыдущие отображения струн
        for i in reversed(range(self.strings_layout.count())):
            self.strings_layout.itemAt(i).widget().setParent(None)

        # Добавляем отображения для текущих струн
        strings = self.tunings[self.current_tuning]
        for i, note in enumerate(reversed(strings)):  # reversed для правильного порядка струн
            string_widget = QtWidgets.QWidget()
            string_layout = QtWidgets.QVBoxLayout()

            string_label = QtWidgets.QLabel(f"{len(strings) - i}")
            string_label.setAlignment(Qt.AlignCenter)
            string_label.setStyleSheet("""
                font-size: 16px; 
                color: #bdc3c7; 
                background: rgba(52, 73, 94, 0.8);
                border-radius: 10px;
                padding: 5px;
                margin: 2px;
            """)

            note_label = QtWidgets.QLabel(note)
            note_label.setAlignment(Qt.AlignCenter)
            note_label.setStyleSheet("""
                font-size: 18px; 
                font-weight: bold; 
                color: #ecf0f1;
                background: rgba(44, 62, 80, 0.9);
                border-radius: 15px;
                padding: 10px;
                margin: 2px;
            """)

            string_layout.addWidget(string_label)
            string_layout.addWidget(note_label)
            string_widget.setLayout(string_layout)
            self.strings_layout.addWidget(string_widget)

    def change_tuning(self, tuning_name):
        self.current_tuning = tuning_name
        self.update_strings_display()

    def init_audio(self):
        try:
            self.CHUNK = 2048
            self.RATE = 44100
            self.audio = pyaudio.PyAudio()

            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,
                stream_callback=self.audio_callback
            )
            self.stream.start_stream()

        except Exception as e:
            print(f"Ошибка инициализации аудио: {e}")

    def audio_callback(self, in_data, frame_count, time_info, status):
        if status:
            print(f"Audio status: {status}")

        # Обработка в отдельном потоке через QTimer
        QtCore.QTimer.singleShot(0, lambda: self.process_audio_data(in_data))
        return (in_data, pyaudio.paContinue)

    def process_audio_data(self, audio_data):
        try:
            data = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)

            # Применяем оконную функцию
            window = np.hanning(len(data))
            data = data * window

            # FFT анализ
            spectrum = np.fft.rfft(data)
            frequencies = np.fft.rfftfreq(len(data), 1.0 / self.RATE)
            magnitudes = np.abs(spectrum)

            # Находим основную частоту
            max_idx = np.argmax(magnitudes[10:]) + 10  # Игнорируем очень низкие частоты
            frequency = frequencies[max_idx]

            if 60 < frequency < 1200:  # Диапазон гитарных нот
                closest_note, target_freq, cents_diff = self.find_closest_note(frequency)

                # Обновляем UI в главном потоке
                self.freq_display.setText(f"{frequency:.1f} Hz")
                self.note_display.setText(closest_note)
                self.tuning_meter.set_value(cents_diff)

                # Анимация для точной настройки
                if abs(cents_diff) <= 5:
                    self.note_display.setStyleSheet("""
                        font-size: 72px; 
                        font-weight: bold; 
                        color: #2ecc71;
                        background: rgba(46, 204, 113, 0.2);
                        border-radius: 20px;
                        padding: 20px;
                        margin: 20px;
                    """)
                    self.note_display.start_animations()
                else:
                    self.note_display.setStyleSheet("""
                        font-size: 72px; 
                        font-weight: bold; 
                        color: #e74c3c;
                        background: rgba(231, 76, 60, 0.2);
                        border-radius: 20px;
                        padding: 20px;
                        margin: 20px;
                    """)
                    self.note_display.stop_animations()

                # Обновляем спектр
                spectrum_vis = magnitudes[:100] / np.max(magnitudes[:100]) if np.max(
                    magnitudes[:100]) > 0 else magnitudes[:100]
                self.spectrum_widget.update_spectrum(spectrum_vis)

        except Exception as e:
            print(f"Ошибка обработки аудио: {e}")

    def find_closest_note(self, frequency):
        closest_note = None
        min_diff = float('inf')
        target_freq = 0

        for note, freq in self.note_frequencies.items():
            diff = abs(frequency - freq)
            if diff < min_diff:
                min_diff = diff
                closest_note = note
                target_freq = freq

        # Вычисляем разницу в центах
        cents_diff = 1200 * np.log2(frequency / target_freq) if target_freq > 0 else 0
        return closest_note, target_freq, cents_diff

    def closeEvent(self, event):
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Устанавливаем стиль приложения
    app.setStyle('Fusion')

    tuner = UniversalGuitarTuner()
    tuner.show()

    sys.exit(app.exec_())