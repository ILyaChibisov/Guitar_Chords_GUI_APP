from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os
import tempfile

from gui.widgets.buttons import SoundButtonLarge, ModernButton, ChordVariantButton
from drawing_elements import DrawingElements


class ChordViewerWindow(QDialog):
    def __init__(self, chord_name, image_path, mp3_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Аккорд {chord_name}")
        # Убираем фиксированный размер, чтобы окно подстраивалось под аккорд
        self.setMinimumSize(400, 500)  # Минимальный размер, но может увеличиваться
        self.setModal(True)

        self.chord_name = chord_name
        self.image_path = image_path
        self.mp3_path = mp3_path
        self.current_display_type = "fingers"
        self.current_variant = 1

        # Получаем конфигурационный менеджер из родительского окна
        self.config_manager = None
        if parent and hasattr(parent, 'config_manager'):
            self.config_manager = parent.config_manager
            print(f"✅ Конфигурационный менеджер получен из родителя")

        self.player = QMediaPlayer()

        self.setup_ui()
        self.load_chord_image()

        # Применяем стили
        self.apply_styles()

    def setup_ui(self):
        """Настройка интерфейса без рамок"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок с названием аккорда - БЕЗ РАМКИ
        chord_title = QLabel(f"Аккорд {self.chord_name}")
        chord_title.setObjectName("chord_title")
        chord_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(chord_title)

        # Описание аккорда - БЕЗ РАМКИ
        chord_description = QLabel(self.get_chord_description())
        chord_description.setObjectName("chord_description")
        chord_description.setAlignment(Qt.AlignCenter)
        chord_description.setWordWrap(True)
        layout.addWidget(chord_description)

        # Область изображения аккорда - БЕЗ РАМКИ
        self.image_label = QLabel()
        self.image_label.setObjectName("image_label")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(300, 300)  # Увеличил минимальный размер
        layout.addWidget(self.image_label, 1)  # Занимает всё доступное пространство

        # Панель управления отображением (пальцы/ноты)
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

        # Добавляем кнопки вариантов
        self.add_variant_buttons()

        layout.addWidget(self.variants_container)

        # Кнопка закрытия
        close_btn = ModernButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def apply_styles(self):
        """Применение стилей без рамок"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2c3e50, stop: 1 #34495e);
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            /* ЗАГОЛОВОК АККОРДА - БЕЗ РАМКИ */
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

            /* ОПИСАНИЕ АККОРДА - БЕЗ РАМКИ */
            #chord_description {
                color: #E0E0E0;
                font-size: 14px;
                text-align: center;
                padding: 5px 0px;
                background: transparent;
                border: none;
                margin: 0px;
            }

            /* ИЗОБРАЖЕНИЕ АККОРДА - БЕЗ РАМКИ */
            #image_label {
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }

            /* ПАНЕЛЬ УПРАВЛЕНИЯ - БЕЗ РАМКИ */
            #control_widget {
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }

            /* КОНТЕЙНЕР ВАРИАНТОВ - БЕЗ РАМКИ */
            #variants_container {
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }

            /* КНОПКИ УПРАВЛЕНИЯ */
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
        """)

    def get_chord_description(self):
        """Получение описания аккорда"""
        try:
            from const import CHORDS_TYPE_LIST, CHORDS_TYPE_NAME_LIST_DSR

            CHORDS_DATA = {}
            for chords_list, desc_list in zip(CHORDS_TYPE_LIST, CHORDS_TYPE_NAME_LIST_DSR):
                for chord, description in zip(chords_list, desc_list):
                    CHORDS_DATA[chord] = description

            names_to_try = [
                self.chord_name,
                self.chord_name.upper(),
                self.chord_name.upper().replace('M', 'm'),
                self.chord_name.upper().replace('М', 'm'),
            ]

            for name in names_to_try:
                if name in CHORDS_DATA:
                    return CHORDS_DATA[name]

        except ImportError:
            pass

        return f"Гитарный аккорд {self.chord_name}"

    def load_chord_image(self):
        """Загрузка изображения аккорда с увеличенным размером"""
        try:
            if self.config_manager:
                print(f"🎯 Генерация аккорда из конфигурации: {self.chord_name}")
                self.generate_chord_from_config()
            elif self.image_path and os.path.exists(self.image_path):
                self.load_chord_from_file()
            else:
                self.show_error_image("Изображение не найдено")

        except Exception as e:
            print(f"❌ Ошибка загрузки изображения: {e}")
            self.show_error_image("Ошибка отображения")

    def generate_chord_from_config(self):
        """Генерация аккорда из конфигурации с увеличенным размером"""
        try:
            variant_key = f"{self.chord_name}v{self.current_variant}" if self.current_variant > 1 else self.chord_name
            chord_config = self.config_manager.get_chord_config(variant_key)

            if not chord_config:
                print(f"❌ Конфигурация не найдена для: {variant_key}")
                self.show_error_image("Аккорд не найден")
                return

            if self.current_display_type == "fingers":
                elements = chord_config['elements_fingers']
                print(f"👆 Используем элементы пальцев: {len(elements)}")
            else:
                elements = chord_config['elements_notes']
                print(f"🎵 Используем элементы нот: {len(elements)}")

            if not elements:
                print(f"❌ Нет элементов для аккорда {variant_key}")
                self.show_error_image("Нет данных аккорда")
                return

            elements = self.apply_outline_settings(elements)

            base_image_path = self.config_manager.get_base_image_path()
            if not base_image_path or not os.path.exists(base_image_path):
                print(f"❌ Базовое изображение не найдено: {base_image_path}")
                self.show_error_image("Базовое изображение не найдено")
                return

            original_pixmap = QPixmap(base_image_path)
            if original_pixmap.isNull():
                print(f"❌ Не удалось загрузить базовое изображение: {base_image_path}")
                self.show_error_image("Ошибка загрузки изображения")
                return

            crop_rect = chord_config.get('crop_rect')
            if not crop_rect:
                print(f"❌ Нет области обрезки для аккорда {variant_key}")
                self.show_error_image("Нет области обрезки")
                return

            crop_x, crop_y, crop_width, crop_height = crop_rect

            # Проверяем границы
            crop_x = max(0, min(crop_x, original_pixmap.width() - 1))
            crop_y = max(0, min(crop_y, original_pixmap.height() - 1))
            crop_width = max(1, min(crop_width, original_pixmap.width() - crop_x))
            crop_height = max(1, min(crop_height, original_pixmap.height() - crop_y))

            print(f"🎯 Оригинальное изображение: {original_pixmap.width()}x{original_pixmap.height()}")
            print(f"🎯 Область обрезки: ({crop_x}, {crop_y}, {crop_width}, {crop_height})")

            # Создаем новое изображение размером с область обрезки
            result_pixmap = QPixmap(crop_width, crop_height)
            result_pixmap.fill(Qt.transparent)

            painter = QPainter(result_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.setRenderHint(QPainter.TextAntialiasing)

            # Копируем область из оригинального изображения
            painter.drawPixmap(0, 0, original_pixmap, crop_x, crop_y, crop_width, crop_height)

            # Рисуем элементы
            self.draw_elements_on_canvas(painter, elements, (crop_x, crop_y, crop_width, crop_height))
            painter.end()

            # УВЕЛИЧИВАЕМ РАЗМЕР ДЛЯ БОЛЬШОГО ОКНА - 60% вместо 30%
            display_width = int(crop_width * 0.3)
            display_height = int(crop_height * 0.3)

            print(f"📏 Увеличенный масштаб (60%): {crop_width}x{crop_height} -> {display_width}x{display_height}")

            scaled_pixmap = result_pixmap.scaled(
                display_width,
                display_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.image_label.setPixmap(scaled_pixmap)
            print(f"✅ Изображение установлено: {scaled_pixmap.width()}x{scaled_pixmap.height()}")

            # Подгоняем размер окна под изображение
            self.adjustSize()

        except Exception as e:
            print(f"❌ Ошибка генерации аккорда: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_image("Ошибка генерации")

    def load_chord_from_file(self):
        """Загрузка аккорда из файла с увеличенным размером"""
        original_pixmap = QPixmap(self.image_path)
        if original_pixmap.isNull():
            self.show_error_image("Ошибка загрузки изображения")
            return

        print(f"📏 Оригинальный размер: {original_pixmap.width()}x{original_pixmap.height()}")

        # УВЕЛИЧИВАЕМ РАЗМЕР - 60% вместо 30%
        display_width = int(original_pixmap.width() * 0.3)
        display_height = int(original_pixmap.height() * 0.3)

        print(f"📏 Увеличенный масштаб: {display_width}x{display_height}")

        scaled_pixmap = original_pixmap.scaled(
            display_width,
            display_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        print(f"✅ Изображение установлено: {scaled_pixmap.width()}x{scaled_pixmap.height()}")

        # Подгоняем размер окна под изображение
        self.adjustSize()

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

    # Остальные методы остаются без изменений...
    def add_variant_buttons(self):
        """Добавление кнопок вариантов аккорда"""
        for i in reversed(range(self.variants_layout.count())):
            widget = self.variants_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        variants_count = 3
        if self.config_manager:
            variants_count = self.config_manager.get_chord_variants_count(self.chord_name)
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

    def play_chord_sound(self):
        """Воспроизведение звука аккорда"""
        try:
            if self.mp3_path and os.path.exists(self.mp3_path):
                url = QUrl.fromLocalFile(self.mp3_path)
                self.player.setMedia(QMediaContent(url))
                self.player.play()
                print(f"🔊 Воспроизведение звука для {self.chord_name}")
            else:
                print(f"❌ Звуковой файл не найден: {self.mp3_path}")

        except Exception as e:
            print(f"❌ Ошибка воспроизведения звука: {e}")

    def draw_elements_on_canvas(self, painter, elements, crop_rect):
        """Рисование элементов на canvas"""
        try:
            if not DrawingElements:
                print("❌ DrawingElements не доступен")
                return

            for element in elements:
                if element['type'] == 'fret':
                    self.draw_fret_on_canvas(painter, element['data'], crop_rect)
                elif element['type'] == 'note':
                    self.draw_note_on_canvas(painter, element['data'], crop_rect)
                elif element['type'] == 'barre':
                    self.draw_barre_on_canvas(painter, element['data'], crop_rect)

        except Exception as e:
            print(f"❌ Ошибка рисования элементов: {e}")

    def draw_fret_on_canvas(self, painter, fret_data, crop_rect):
        """Рисование лада на canvas"""
        try:
            adapted_data = self.adapt_coordinates(fret_data, crop_rect)
            DrawingElements.draw_fret(painter, adapted_data)
        except Exception as e:
            print(f"❌ Ошибка рисования лада: {e}")

    def draw_note_on_canvas(self, painter, note_data, crop_rect):
        """Рисование ноты на canvas"""
        try:
            adapted_data = self.adapt_coordinates(note_data, crop_rect)
            DrawingElements.draw_note(painter, adapted_data)
        except Exception as e:
            print(f"❌ Ошибка рисования ноты: {e}")

    def draw_barre_on_canvas(self, painter, barre_data, crop_rect):
        """Рисование баре на canvas"""
        try:
            adapted_data = self.adapt_coordinates(barre_data, crop_rect)
            DrawingElements.draw_barre(painter, adapted_data)
        except Exception as e:
            print(f"❌ Ошибка рисования баре: {e}")

    def adapt_coordinates(self, element_data, crop_rect):
        """Адаптация координат элементов к canvas"""
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

        if adapted_data.get('type') == 'barre':
            barre_width = adapted_data.get('width', 100)
            barre_height = adapted_data.get('height', 20)

            if 'x' in adapted_data:
                adapted_data['x'] = adapted_data['x'] - (barre_width // 2)
            if 'y' in adapted_data:
                adapted_data['y'] = adapted_data['y'] - (barre_height // 2)

        return adapted_data

    def apply_outline_settings(self, elements):
        """Применение настроек обводки к элементам"""
        modified_elements = []
        for element in elements:
            if element['type'] == 'barre':
                modified_element = element.copy()
                modified_element['data'] = element['data'].copy()
                modified_element['data']['outline_width'] = 4
                modified_element['data']['outline_color'] = [0, 0, 0]
                modified_elements.append(modified_element)
            elif element['type'] == 'note':
                modified_element = element.copy()
                modified_element['data'] = element['data'].copy()
                modified_element['data']['outline_width'] = 6
                modified_element['data']['outline_color'] = [0, 0, 0]
                modified_elements.append(modified_element)
            else:
                modified_elements.append(element)

        return modified_elements