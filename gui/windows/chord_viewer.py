from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os
import tempfile

from gui.widgets.buttons import ModernButton, ChordVariantButton
from drawing_elements import DrawingElements
from config.settings_chord_viewer import ChordViewerSettings


class ChordViewerWindow(QDialog):
    def __init__(self, chord_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Аккорд {chord_name}")
        self.setMinimumSize(*ChordViewerSettings.WINDOW_MIN_SIZE)
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
        self.chord_description = QLabel(self.get_chord_description())
        self.chord_description.setObjectName("chord_description")
        self.chord_description.setAlignment(Qt.AlignCenter)
        self.chord_description.setWordWrap(True)
        layout.addWidget(self.chord_description)

        # Область изображения аккорда
        self.image_label = QLabel()
        self.image_label.setObjectName("image_label")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(*ChordViewerSettings.IMAGE_LABEL_MIN_SIZE)
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
        """Применение стилей из настроек"""
        self.setStyleSheet(ChordViewerSettings.WINDOW_STYLES)

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
        """Загрузка изображения аккорда"""
        try:
            print(f"🎯 Генерация аккорда: {self.chord_name}, вариант {self.current_variant}")
            self.generate_chord_with_settings()
        except Exception as e:
            print(f"❌ Ошибка загрузки изображения: {e}")
            self.show_error_image("Ошибка отображения")

    def generate_chord_with_settings(self):
        """Генерация аккорда с настройками из ChordViewerSettings"""
        try:
            from core.chord_manager import ChordManager

            # Получаем данные аккорда и находим нужный вариант
            chord_data = ChordManager.get_chord_data(self.chord_name)
            if not chord_data:
                print(f"❌ Аккорд {self.chord_name} не найден")
                self.show_error_image("Аккорд не найден")
                return

            # Получаем все варианты аккорда
            variants = chord_data.get('variants', [])
            if not variants:
                print(f"❌ Нет вариантов для аккорда {self.chord_name}")
                self.show_error_image("Нет вариантов")
                return

            # Проверяем что запрошенный вариант существует
            if self.current_variant > len(variants):
                print(f"❌ Вариант {self.current_variant} не существует для аккорда {self.chord_name}")
                self.current_variant = 1  # Возвращаемся к первому варианту

            # Получаем конкретный вариант
            variant_config = variants[self.current_variant - 1]

            print(f"✅ Загружен вариант {self.current_variant} для аккорда {self.chord_name}")

            # Получаем элементы для текущего типа отображения
            if self.current_display_type == "fingers":
                elements_data = variant_config.get('drawing_elements_fingers', {})
                print(f"👆 Используем элементы ПАЛЬЦЕВ")
            else:
                elements_data = variant_config.get('drawing_elements_notes', {})
                print(f"🎵 Используем элементы НОТ")

            # Объединяем все элементы в один список для отрисовки
            all_elements = []
            for element_type, elements_list in elements_data.items():
                all_elements.extend(elements_list)
                print(f"   {element_type}: {len(elements_list)} элементов")

            if not all_elements:
                print(f"❌ Нет элементов для аккорда {self.chord_name} вариант {self.current_variant}")
                self.show_error_image("Нет данных аккорда")
                return

            # Применяем обводку с настройками из ChordViewerSettings
            elements = self.apply_outline_with_settings(all_elements)

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
            crop_rect = variant_config.get('crop_rect')
            if not crop_rect:
                print(f"❌ Нет области обрезки для аккорда {self.chord_name} вариант {self.current_variant}")
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

            # 🔥 ИСПОЛЬЗУЕМ НАСТРОЙКИ МАСШТАБА ИЗ ChordViewerSettings
            scale_factor = ChordViewerSettings.SCALE_FACTOR
            scaled_width = int(crop_width * scale_factor)
            scaled_height = int(crop_height * scale_factor)

            print(
                f"📏 Масштабирование: {crop_width}x{crop_height} -> {scaled_width}x{scaled_height} (коэф: {scale_factor})")

            # Создаем новое изображение размером с масштабированную область обрезки
            result_pixmap = QPixmap(scaled_width, scaled_height)
            result_pixmap.fill(Qt.transparent)

            painter = QPainter(result_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.setRenderHint(QPainter.TextAntialiasing)

            # Масштабируем и копируем область из оригинального изображения
            scaled_pixmap = original_pixmap.copy(
                int(crop_x), int(crop_y), int(crop_width), int(crop_height)
            ).scaled(
                scaled_width, scaled_height,
                Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )

            painter.drawPixmap(0, 0, scaled_pixmap)

            # Рисуем элементы в правильном порядке с учетом масштабирования
            self.draw_elements_on_canvas_scaled(painter, elements, (crop_x, crop_y, crop_width, crop_height),
                                                scale_factor)
            painter.end()

            print(f"✅ Сгенерирован аккорд: {result_pixmap.width()}x{result_pixmap.height()}")

            # Устанавливаем изображение
            self.image_label.setPixmap(result_pixmap)

            # Подгоняем размер окна под изображение
            self.adjustSize()

            # Проверяем доступность звука
            self.check_sound_availability()

        except Exception as e:
            print(f"❌ Ошибка генерации аккорда: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_image("Ошибка генерации")

    def apply_outline_with_settings(self, elements):
        """Применение настроек обводки из ChordViewerSettings"""
        modified_elements = []
        for element in elements:
            modified_element = element.copy()
            modified_element['data'] = element['data'].copy()

            element_type = element['type']

            if element_type == 'barre':
                # 🔥 ИСПОЛЬЗУЕМ НАСТРОЙКИ ДЛЯ БАРЕ
                modified_element['data']['outline_width'] = ChordViewerSettings.OUTLINE_BARRE_WIDTH
                modified_element['data']['outline_color'] = ChordViewerSettings.OUTLINE_COLOR

            elif element_type == 'note':
                # 🔥 ИСПОЛЬЗУЕМ НАСТРОЙКИ ДЛЯ НОТ
                modified_element['data']['outline_width'] = ChordViewerSettings.OUTLINE_NOTE_WIDTH
                modified_element['data']['outline_color'] = ChordViewerSettings.OUTLINE_COLOR

                # 🔥 АДАПТИВНЫЙ ТЕКСТ ИЗ НАСТРОЕК
                if ChordViewerSettings.ADAPTIVE_TEXT_ENABLED:
                    symbol = modified_element['data'].get('finger') or modified_element['data'].get('note_name', '')
                    if symbol and len(symbol) > 1:
                        current_radius = modified_element['data'].get('radius', 12)
                        new_radius = max(ChordViewerSettings.MIN_NOTE_RADIUS,
                                         current_radius - ChordViewerSettings.LONG_SYMBOL_RADIUS_REDUCTION)
                        modified_element['data']['radius'] = new_radius
                        print(f"  🔧 Уменьшен радиус для '{symbol}': {current_radius} -> {new_radius}")

            elif element_type == 'fret':
                # 🔥 ИСПОЛЬЗУЕМ НАСТРОЙКИ ДЛЯ ЛАДОВ
                modified_element['data']['outline_width'] = ChordViewerSettings.OUTLINE_FRET_WIDTH
                modified_element['data']['outline_color'] = ChordViewerSettings.OUTLINE_COLOR
                # Устанавливаем цвет текста ладов из настроек
                modified_element['data']['color'] = ChordViewerSettings.FRET_TEXT_COLOR

            elif element_type == 'open_note':
                # 🔥 ИСПОЛЬЗУЕМ НАСТРОЙКИ ДЛЯ ОТКРЫТЫХ СТРУН
                modified_element['data']['outline_width'] = ChordViewerSettings.OUTLINE_OPEN_NOTE_WIDTH
                modified_element['data']['outline_color'] = ChordViewerSettings.OUTLINE_COLOR

            modified_elements.append(modified_element)

        return modified_elements

    def draw_elements_on_canvas_scaled(self, painter, elements, crop_rect, scale_factor):
        """Рисование элементов с учетом масштабирования"""
        try:
            # Группируем элементы по типам для правильного порядка отрисовки
            frets = [e for e in elements if e['type'] == 'fret']
            barres = [e for e in elements if e['type'] == 'barre']
            notes = [e for e in elements if e['type'] == 'note']
            open_notes = [e for e in elements if e['type'] == 'open_note']

            # 1. Лады (фон)
            for element in frets:
                self.draw_element_on_canvas_scaled(painter, element, crop_rect, scale_factor)

            # 2. Баре
            for element in barres:
                self.draw_element_on_canvas_scaled(painter, element, crop_rect, scale_factor)

            # 3. Зажатые ноты
            for element in notes:
                self.draw_element_on_canvas_scaled(painter, element, crop_rect, scale_factor)

            # 4. Открытые ноты (поверх всего)
            for element in open_notes:
                self.draw_element_on_canvas_scaled(painter, element, crop_rect, scale_factor)

        except Exception as e:
            print(f"❌ Ошибка рисования элементов: {e}")

    def draw_element_on_canvas_scaled(self, painter, element, crop_rect, scale_factor):
        """Рисование одного элемента с учетом масштабирования"""
        try:
            adapted_data = self.adapt_coordinates_scaled(element['data'], crop_rect, scale_factor)

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

    def adapt_coordinates_scaled(self, element_data, crop_rect, scale_factor):
        """Адаптация координат с учетом масштабирования"""
        if not crop_rect:
            return element_data.copy()

        adapted_data = element_data.copy()
        crop_x, crop_y, crop_width, crop_height = crop_rect

        original_x = element_data.get('x', 0)
        original_y = element_data.get('y', 0)

        # Адаптируем координаты с учетом crop и масштабирования
        if 'x' in adapted_data:
            adapted_data['x'] = (original_x - crop_x) * scale_factor
        if 'y' in adapted_data:
            adapted_data['y'] = (original_y - crop_y) * scale_factor

        adapted_data['x'] = int(round(adapted_data.get('x', 0)))
        adapted_data['y'] = int(round(adapted_data.get('y', 0)))

        # Масштабируем размеры элементов
        if 'width' in adapted_data:
            adapted_data['width'] = int(adapted_data['width'] * scale_factor)
        if 'height' in adapted_data:
            adapted_data['height'] = int(adapted_data['height'] * scale_factor)
        if 'radius' in adapted_data:
            # 🔥 ИСПОЛЬЗУЕМ МИНИМАЛЬНЫЙ РАДИУС ИЗ НАСТРОЕК
            adapted_data['radius'] = max(ChordViewerSettings.MIN_NOTE_RADIUS,
                                         int(adapted_data['radius'] * scale_factor))
        if 'size' in adapted_data:
            adapted_data['size'] = int(adapted_data['size'] * scale_factor)

        # Для баре - преобразуем центр в левый верхний угол
        if (adapted_data.get('width') and adapted_data.get('height') and
                adapted_data.get('width') > 25 and adapted_data.get('height') > 10):
            barre_width = adapted_data.get('width', 50)
            barre_height = adapted_data.get('height', 10)
            adapted_data['x'] = adapted_data['x'] - (barre_width // 2)
            adapted_data['y'] = adapted_data['y'] - (barre_height // 2)

        return adapted_data

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

            chord_data = ChordManager.get_chord_data(self.chord_name)
            if not chord_data:
                print(f"❌ Аккорд {self.chord_name} не найден")
                return

            variants = chord_data.get('variants', [])
            variants_count = len(variants)

            print(f"🎯 Для аккорда {self.chord_name} найдено {variants_count} вариантов")

            for variant_num in range(1, variants_count + 1):
                btn = ChordVariantButton(str(variant_num))
                btn.setProperty('variant_num', variant_num)

                def make_handler(v_num):
                    def handler():
                        self.current_variant = v_num
                        print(f"🔄 Переключение на вариант {v_num} для аккорда {self.chord_name}")
                        self.refresh_chord_display()

                        # Снимаем выделение с других кнопок
                        for i in range(self.variants_layout.count()):
                            other_btn = self.variants_layout.itemAt(i).widget()
                            if other_btn and other_btn.property('variant_num') != v_num:
                                other_btn.setChecked(False)
                                other_btn.update_style()

                    return handler

                handler = make_handler(variant_num)
                btn.clicked.connect(handler)
                self.variants_layout.addWidget(btn)

            # Активируем первый вариант
            if self.variants_layout.count() > 0:
                first_btn = self.variants_layout.itemAt(0).widget()
                if first_btn:
                    first_btn.setChecked(True)
                    first_btn.update_style()
                    self.current_variant = 1
                    print(f"✅ Активирован вариант 1 для аккорда {self.chord_name}")

        except Exception as e:
            print(f"❌ Ошибка загрузки вариантов: {e}")
            import traceback
            traceback.print_exc()

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
            QTimer.singleShot(ChordViewerSettings.SOUND_BUTTON_RESTORE_DELAY, self.restore_sound_button)

        except Exception as e:
            print(f"❌ Ошибка воспроизведения звука: {e}")
            self.sound_btn.setText("❌ Ошибка")
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(ChordViewerSettings.SOUND_BUTTON_RESTORE_DELAY, self.restore_sound_button)

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