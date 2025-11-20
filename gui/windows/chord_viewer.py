from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os
import tempfile

from gui.widgets.buttons import ModernButton, ChordVariantButton
from drawing_elements import DrawingElements


class ChordViewerWindow(QDialog):
    def __init__(self, chord_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Аккорд {chord_name}")
        self.setMinimumSize(600, 700)  # Увеличил для больших аккордов
        self.setModal(True)

        self.chord_name = chord_name
        self.parent = parent
        self.current_display_type = "fingers"
        self.current_variant = 1

        self.player = QMediaPlayer()

        self.setup_ui()
        self.load_chord_data()
        self.apply_styles()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок с названием аккорда
        chord_title = QLabel(f"Аккорд {self.chord_name}")
        chord_title.setObjectName("chord_title")
        chord_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(chord_title)

        # Описание аккорда
        chord_description = QLabel(self.get_chord_description())
        chord_description.setObjectName("chord_description")
        chord_description.setAlignment(Qt.AlignCenter)
        chord_description.setWordWrap(True)
        layout.addWidget(chord_description)

        # Область изображения аккорда
        self.image_label = QLabel()
        self.image_label.setObjectName("image_label")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(500, 400)  # Увеличил для больших аккордов
        layout.addWidget(self.image_label, 1)

        # Панель управления отображением
        control_widget = QWidget()
        control_widget.setObjectName("control_widget")
        control_layout = QHBoxLayout(control_widget)
        control_layout.setAlignment(Qt.AlignCenter)
        control_layout.setSpacing(15)

        # Кнопка переключения ноты/пальцы
        self.display_toggle_btn = QPushButton("🎵 Ноты")
        self.display_toggle_btn.setObjectName("display_toggle_btn")
        self.display_toggle_btn.setCheckable(True)
        self.display_toggle_btn.setChecked(False)
        self.display_toggle_btn.setFixedSize(120, 35)
        self.display_toggle_btn.clicked.connect(self.toggle_display_type)

        # Кнопка звука
        self.sound_btn = QPushButton("🔊 Слушать")
        self.sound_btn.setObjectName("sound_btn")
        self.sound_btn.setFixedSize(120, 35)
        self.sound_btn.clicked.connect(self.play_chord_sound)

        control_layout.addWidget(self.display_toggle_btn)
        control_layout.addWidget(self.sound_btn)
        layout.addWidget(control_widget)

        # Кнопки вариантов аппликатуры
        self.variants_container = QWidget()
        self.variants_container.setObjectName("variants_container")
        self.variants_layout = QHBoxLayout(self.variants_container)
        self.variants_layout.setAlignment(Qt.AlignCenter)
        self.variants_layout.setSpacing(8)

        layout.addWidget(self.variants_container)

        # Кнопка закрытия
        close_btn = ModernButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def apply_styles(self):
        """Применение стилей"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2c3e50, stop: 1 #34495e);
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            #chord_title {
                color: white;
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                padding: 10px 0px;
                background: transparent;
                border: none;
                margin: 0px;
            }

            #chord_description {
                color: #E0E0E0;
                font-size: 14px;
                text-align: center;
                padding: 5px 0px;
                background: transparent;
                border: none;
                margin: 0px;
            }

            #image_label {
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }

            #control_widget {
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }

            #variants_container {
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }

            #display_toggle_btn {
                background: rgba(52, 152, 219, 0.7);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
            }
            #display_toggle_btn:checked {
                background: rgba(231, 76, 60, 0.7);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            #display_toggle_btn:hover {
                background: rgba(52, 152, 219, 0.9);
            }
            #display_toggle_btn:checked:hover {
                background: rgba(231, 76, 60, 0.9);
            }

            #sound_btn {
                background: rgba(46, 204, 113, 0.7);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
            }
            #sound_btn:hover {
                background: rgba(46, 204, 113, 0.9);
            }
            #sound_btn:disabled {
                background: rgba(149, 165, 166, 0.7);
                color: rgba(127, 140, 141, 0.7);
            }
        """)

    def get_chord_description(self):
        """Получение описания аккорда"""
        try:
            if self.parent and hasattr(self.parent, 'get_chord_description'):
                return self.parent.get_chord_description(self.chord_name)
        except:
            pass

        return f"Гитарный аккорд {self.chord_name}"

    def load_chord_data(self):
        """Загрузка данных аккорда и создание кнопок вариантов"""
        try:
            self.add_variant_buttons()
            self.load_chord_image()
        except Exception as e:
            print(f"❌ Ошибка загрузки данных аккорда: {e}")
            self.show_error_image("Ошибка загрузки")

    def load_chord_image(self):
        """Загрузка изображения аккорда в ОРИГИНАЛЬНОМ РАЗМЕРЕ"""
        try:
            print(f"🎯 Генерация аккорда в оригинальном размере: {self.chord_name}, вариант {self.current_variant}")
            self.generate_chord_original_size()
        except Exception as e:
            print(f"❌ Ошибка загрузки изображения: {e}")
            self.show_error_image("Ошибка отображения")

    def generate_chord_original_size(self):
        """Генерация аккорда в ОРИГИНАЛЬНОМ РАЗМЕРЕ без масштабирования"""
        try:
            from core.chord_manager import ChordManager

            # Получаем конфигурацию для конкретного варианта
            variant_key = f"{self.chord_name}v{self.current_variant}" if self.current_variant > 1 else self.chord_name
            chord_config = ChordManager.get_chord_config(variant_key)

            if not chord_config:
                print(f"❌ Конфигурация не найдена для: {variant_key}")
                self.show_error_image("Аккорд не найден")
                return

            # Получаем элементы для текущего типа отображения
            if self.current_display_type == "fingers":
                elements_data = chord_config.get('drawing_elements_fingers', {})
                print(f"👆 Используем элементы ПАЛЬЦЕВ")
            else:
                elements_data = chord_config.get('drawing_elements_notes', {})
                print(f"🎵 Используем элементы НОТ")

            # Объединяем все элементы в один список для отрисовки
            all_elements = []
            for element_type, elements_list in elements_data.items():
                all_elements.extend(elements_list)
                print(f"   {element_type}: {len(elements_list)} элементов")

            if not all_elements:
                print(f"❌ Нет элементов для аккорда {variant_key}")
                self.show_error_image("Нет данных аккорда")
                return

            # Применяем обводку
            elements = self.apply_outline_settings(all_elements)

            # Загружаем базовое изображение
            base_image_path = ChordManager.get_template_image_path()
            if not base_image_path or not os.path.exists(base_image_path):
                print(f"❌ Базовое изображение не найдено: {base_image_path}")
                self.show_error_image("Базовое изображение не найдено")
                return

            original_pixmap = QPixmap(base_image_path)
            if original_pixmap.isNull():
                print(f"❌ Не удалось загрузить базовое изображение")
                self.show_error_image("Ошибка загрузки изображения")
                return

            # Получаем область обрезки
            crop_rect = chord_config.get('crop_rect')
            if not crop_rect:
                print(f"❌ Нет области обрезки для аккорда {variant_key}")
                self.show_error_image("Нет области обрезки")
                return

            # Преобразуем crop_rect в кортеж
            if isinstance(crop_rect, dict):
                crop_x = crop_rect.get('x', 0)
                crop_y = crop_rect.get('y', 0)
                crop_width = crop_rect.get('width', 0)
                crop_height = crop_rect.get('height', 0)
            elif isinstance(crop_rect, (list, tuple)) and len(crop_rect) == 4:
                crop_x, crop_y, crop_width, crop_height = crop_rect
            else:
                print(f"❌ Неверный формат crop_rect: {type(crop_rect)}")
                self.show_error_image("Ошибка формата данных")
                return

            # Проверяем границы
            crop_x = max(0, min(crop_x, original_pixmap.width() - 1))
            crop_y = max(0, min(crop_y, original_pixmap.height() - 1))
            crop_width = max(1, min(crop_width, original_pixmap.width() - crop_x))
            crop_height = max(1, min(crop_height, original_pixmap.height() - crop_y))

            print(f"🎯 ОРИГИНАЛЬНЫЕ ДАННЫЕ:")
            print(f"   Базовое изображение: {original_pixmap.width()}x{original_pixmap.height()}")
            print(f"   Область обрезки: ({crop_x}, {crop_y}, {crop_width}, {crop_height})")

            # Создаем новое изображение размером с область обрезки
            result_pixmap = QPixmap(crop_width, crop_height)
            result_pixmap.fill(Qt.transparent)

            painter = QPainter(result_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.setRenderHint(QPainter.TextAntialiasing)

            # Копируем область из оригинального изображения
            painter.drawPixmap(0, 0, original_pixmap, crop_x, crop_y, crop_width, crop_height)

            # Рисуем элементы в ПРАВИЛЬНОМ ПОРЯДКЕ
            self.draw_elements_on_canvas_ordered(painter, elements, (crop_x, crop_y, crop_width, crop_height))
            painter.end()

            print(f"✅ Сгенерирован аккорд в ОРИГИНАЛЬНОМ РАЗМЕРЕ: {result_pixmap.width()}x{result_pixmap.height()}")

            # Устанавливаем изображение БЕЗ масштабирования
            self.image_label.setPixmap(result_pixmap)

            # Подгоняем размер окна под оригинальное изображение
            self.adjustSize()

            # Проверяем доступность звука
            self.check_sound_availability()

        except Exception as e:
            print(f"❌ Ошибка генерации аккорда в оригинальном размере: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_image("Ошибка генерации")

    def draw_elements_on_canvas_ordered(self, painter, elements, crop_rect):
        """Рисование элементов в ПРАВИЛЬНОМ ПОРЯДКЕ (баре под нотами)"""
        try:
            # 1. Сначала рисуем лады
            for element in elements:
                if element['type'] == 'fret':
                    self.draw_element_on_canvas(painter, element, crop_rect)

            # 2. Затем рисуем баре
            for element in elements:
                if element['type'] == 'barre':
                    self.draw_element_on_canvas(painter, element, crop_rect)

            # 3. Затем рисуем ноты (поверх баре)
            for element in elements:
                if element['type'] == 'note':
                    self.draw_element_on_canvas(painter, element, crop_rect)

            # 4. Наконец рисуем открытые ноты
            for element in elements:
                if element['type'] == 'open_note':
                    self.draw_element_on_canvas(painter, element, crop_rect)

        except Exception as e:
            print(f"❌ Ошибка рисования элементов: {e}")

    def draw_element_on_canvas(self, painter, element, crop_rect):
        """Рисование одного элемента на canvas"""
        try:
            adapted_data = self.adapt_coordinates(element['data'], crop_rect)

            if element['type'] == 'fret':
                DrawingElements.draw_fret(painter, adapted_data)
            elif element['type'] == 'note':
                DrawingElements.draw_note(painter, adapted_data)
            elif element['type'] == 'barre':
                DrawingElements.draw_barre(painter, adapted_data)
            elif element['type'] == 'open_note':
                DrawingElements.draw_note(painter, adapted_data)

        except Exception as e:
            print(f"❌ Ошибка рисования элемента {element['type']}: {e}")

    def adapt_coordinates(self, element_data, crop_rect):
        """Адаптация координат для canvas"""
        if not crop_rect:
            return element_data.copy()

        adapted_data = element_data.copy()
        crop_x, crop_y, crop_width, crop_height = crop_rect

        original_x = element_data.get('x', 0)
        original_y = element_data.get('y', 0)

        if 'x' in adapted_data:
            adapted_data['x'] = original_x - crop_x
        if 'y' in adapted_data:
            adapted_data['y'] = original_y - crop_y

        adapted_data['x'] = int(round(adapted_data.get('x', 0)))
        adapted_data['y'] = int(round(adapted_data.get('y', 0)))

        # Для баре - преобразуем центр в левый верхний угол
        if (adapted_data.get('width') and adapted_data.get('height') and
                adapted_data.get('width') > 50 and adapted_data.get('height') > 50):
            barre_width = adapted_data.get('width', 100)
            barre_height = adapted_data.get('height', 20)
            adapted_data['x'] = adapted_data['x'] - (barre_width // 2)
            adapted_data['y'] = adapted_data['y'] - (barre_height // 2)

        return adapted_data

    def apply_outline_settings(self, elements):
        """Применение настроек обводки к элементам"""
        modified_elements = []
        for element in elements:
            modified_element = element.copy()
            modified_element['data'] = element['data'].copy()

            if element['type'] == 'barre':
                modified_element['data']['outline_width'] = 2
                modified_element['data']['outline_color'] = [0, 0, 0]
            elif element['type'] == 'note':
                modified_element['data']['outline_width'] = 2
                modified_element['data']['outline_color'] = [0, 0, 0]

            modified_elements.append(modified_element)

        return modified_elements

    def show_error_image(self, message):
        """Показ сообщения об ошибке"""
        pixmap = QPixmap(200, 200)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.red, 4))
        painter.drawLine(10, 10, 190, 190)
        painter.drawLine(190, 10, 10, 190)
        painter.end()
        self.image_label.setPixmap(pixmap)

    def add_variant_buttons(self):
        """Добавление кнопок вариантов аккорда"""
        for i in reversed(range(self.variants_layout.count())):
            widget = self.variants_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        try:
            from core.chord_manager import ChordManager

            variants = ChordManager.get_chord_variants(self.chord_name)
            variants_count = len(variants) if variants else 1

            print(f"🎯 Для аккорда {self.chord_name} найдено {variants_count} вариантов")

            for variant_num in range(1, variants_count + 1):
                btn = ChordVariantButton(str(variant_num))
                btn.setProperty('variant_num', variant_num)

                def make_handler(v_num):
                    def handler():
                        self.current_variant = v_num
                        print(f"🔄 Переключение на вариант {v_num}")
                        self.refresh_chord_display()

                        for i in range(self.variants_layout.count()):
                            other_btn = self.variants_layout.itemAt(i).widget()
                            if other_btn and other_btn.property('variant_num') != v_num:
                                other_btn.setChecked(False)
                                other_btn.update_style()

                    return handler

                handler = make_handler(variant_num)
                btn.clicked.connect(handler)
                self.variants_layout.addWidget(btn)

            if self.variants_layout.count() > 0:
                first_btn = self.variants_layout.itemAt(0).widget()
                if first_btn:
                    first_btn.setChecked(True)
                    first_btn.update_style()
                    self.current_variant = 1

        except Exception as e:
            print(f"❌ Ошибка загрузки вариантов: {e}")
            for variant_num in range(1, 4):
                btn = ChordVariantButton(str(variant_num))
                btn.setProperty('variant_num', variant_num)

                def make_handler(v_num):
                    def handler():
                        self.current_variant = v_num
                        self.refresh_chord_display()
                        for i in range(self.variants_layout.count()):
                            other_btn = self.variants_layout.itemAt(i).widget()
                            if other_btn and other_btn.property('variant_num') != v_num:
                                other_btn.setChecked(False)
                                other_btn.update_style()

                    return handler

                handler = make_handler(variant_num)
                btn.clicked.connect(handler)
                self.variants_layout.addWidget(btn)

            if self.variants_layout.count() > 0:
                first_btn = self.variants_layout.itemAt(0).widget()
                if first_btn:
                    first_btn.setChecked(True)
                    first_btn.update_style()

    def toggle_display_type(self):
        """Переключение между нотами и пальцами"""
        if self.display_toggle_btn.isChecked():
            self.current_display_type = "notes"
            self.display_toggle_btn.setText("👆 Пальцы")
        else:
            self.current_display_type = "fingers"
            self.display_toggle_btn.setText("🎵 Ноты")

        print(f"🔄 Переключение на тип отображения: {self.current_display_type}")
        self.refresh_chord_display()

    def refresh_chord_display(self):
        """Обновление отображения аккорда"""
        print(f"🔄 Обновление: {self.chord_name}, вариант {self.current_variant}, тип {self.current_display_type}")
        self.load_chord_image()

    def check_sound_availability(self):
        """Проверка доступности звука"""
        try:
            from core.chord_manager import ChordManager
            has_sound = ChordManager.has_sound(self.chord_name, self.current_variant)
            self.sound_btn.setEnabled(has_sound)

            if not has_sound:
                self.sound_btn.setText("🔇 Нет звука")
            else:
                self.sound_btn.setText("🔊 Слушать")

        except Exception as e:
            print(f"❌ Ошибка проверки звука: {e}")
            self.sound_btn.setEnabled(False)
            self.sound_btn.setText("🔇 Ошибка")

    def play_chord_sound(self):
        """Воспроизведение звука аккорда"""
        try:
            from core.chord_manager import ChordSoundPlayer

            self.sound_btn.setText("▶️ Играет...")
            self.sound_btn.setEnabled(False)

            success = ChordSoundPlayer.play_chord_sound(
                self.player,
                self.chord_name,
                self.current_variant
            )

            if not success:
                self.sound_btn.setText("❌ Ошибка")

            from PyQt5.QtCore import QTimer
            QTimer.singleShot(2000, self.restore_sound_button)

        except Exception as e:
            print(f"❌ Ошибка воспроизведения звука: {e}")
            self.sound_btn.setText("❌ Ошибка")
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(2000, self.restore_sound_button)

    def restore_sound_button(self):
        """Восстановление кнопки звука"""
        self.check_sound_availability()

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        try:
            if self.player.state() == QMediaPlayer.PlayingState:
                self.player.stop()
        except:
            pass

        event.accept()