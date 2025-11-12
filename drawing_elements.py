from PyQt5.QtGui import QPainter, QFont, QPen, QBrush, QColor, QLinearGradient, QRadialGradient, QFontMetrics
from PyQt5.QtCore import Qt


class DrawingElements:

    @staticmethod
    def get_color_from_data(color_data):
        """Получение QColor из данных цвета"""
        if isinstance(color_data, list) and len(color_data) >= 3:
            return QColor(color_data[0], color_data[1], color_data[2])
        return QColor(0, 0, 0)

    @staticmethod
    def get_brush_from_style(style_name, x=0, y=0, radius=0, width=0, height=0):
        """Получение кисти на основе стиля с поддержкой градиентов"""
        if style_name == "wood":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(210, 180, 140))
            gradient.setColorAt(0.5, QColor(160, 120, 80))
            gradient.setColorAt(1, QColor(210, 180, 140))
            return QBrush(gradient)
        elif style_name == "metal":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(200, 200, 200))
            gradient.setColorAt(0.5, QColor(100, 100, 100))
            gradient.setColorAt(1, QColor(200, 200, 200))
            return QBrush(gradient)
        elif style_name == "rubber":
            gradient = QRadialGradient(x + width / 2, y + height / 2, max(width, height))
            gradient.setColorAt(0, QColor(80, 80, 80))
            gradient.setColorAt(1, QColor(40, 40, 40))
            return QBrush(gradient)
        elif style_name == "gradient":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(189, 183, 107))
            lighter = QColor(189, 183, 107).lighter(150)
            gradient.setColorAt(1, QColor(lighter.red(), lighter.green(), lighter.blue()))
            return QBrush(gradient)
        elif style_name == "striped":
            return QBrush(QColor(189, 183, 107))

        # ОРАНЖЕВЫЕ СТИЛИ ДЛЯ БАРЕ
        elif style_name == "orange_gradient":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(255, 200, 100))
            gradient.setColorAt(0.5, QColor(255, 140, 0))
            gradient.setColorAt(1, QColor(255, 100, 0))
            return QBrush(gradient)
        elif style_name == "orange_metal":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(255, 220, 150))
            gradient.setColorAt(0.3, QColor(255, 180, 80))
            gradient.setColorAt(0.7, QColor(255, 140, 40))
            gradient.setColorAt(1, QColor(255, 120, 20))
            return QBrush(gradient)
        elif style_name == "orange_glow":
            gradient = QRadialGradient(x + width / 2, y + height / 2, max(width, height) * 0.8)
            gradient.setColorAt(0, QColor(255, 230, 180))
            gradient.setColorAt(0.5, QColor(255, 180, 80))
            gradient.setColorAt(1, QColor(255, 140, 0))
            return QBrush(gradient)
        elif style_name == "dark_orange":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(255, 150, 50))
            gradient.setColorAt(0.5, QColor(255, 120, 0))
            gradient.setColorAt(1, QColor(220, 100, 0))
            return QBrush(gradient)
        elif style_name == "orange_wood":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(255, 200, 150))
            gradient.setColorAt(0.3, QColor(255, 170, 100))
            gradient.setColorAt(0.7, QColor(255, 140, 60))
            gradient.setColorAt(1, QColor(255, 120, 40))
            return QBrush(gradient)
        elif style_name == "bright_orange":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(255, 230, 100))
            gradient.setColorAt(0.5, QColor(255, 200, 0))
            gradient.setColorAt(1, QColor(255, 160, 0))
            return QBrush(gradient)
        elif style_name == "orange_red":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(255, 180, 100))
            gradient.setColorAt(0.5, QColor(255, 120, 0))
            gradient.setColorAt(1, QColor(255, 80, 0))
            return QBrush(gradient)
        elif style_name == "orange_yellow":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(255, 240, 150))
            gradient.setColorAt(0.5, QColor(255, 200, 50))
            gradient.setColorAt(1, QColor(255, 180, 0))
            return QBrush(gradient)
        elif style_name == "orange_brown":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(255, 190, 130))
            gradient.setColorAt(0.5, QColor(255, 150, 80))
            gradient.setColorAt(1, QColor(210, 120, 60))
            return QBrush(gradient)
        elif style_name == "orange_pastel":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(255, 220, 180))
            gradient.setColorAt(0.5, QColor(255, 190, 140))
            gradient.setColorAt(1, QColor(255, 170, 120))
            return QBrush(gradient)

        # СТИЛИ ДЛЯ НОТ
        elif style_name == "default":
            return QBrush(QColor(255, 0, 0))
        elif style_name == "blue_gradient":
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(100, 150, 255))
            gradient.setColorAt(1, QColor(50, 100, 200))
            return QBrush(gradient)
        elif style_name == "red_3d":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 150, 150))
            gradient.setColorAt(0.7, QColor(220, 50, 50))
            gradient.setColorAt(1, QColor(180, 0, 0))
            return QBrush(gradient)
        elif style_name == "green_3d":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 255, 180))
            gradient.setColorAt(0.7, QColor(80, 200, 80))
            gradient.setColorAt(1, QColor(40, 160, 40))
            return QBrush(gradient)

        return QBrush(QColor(255, 0, 0))

    @staticmethod
    def draw_fret(painter, fret_data):
        """Рисование лада с ИСПРАВЛЕННЫМ центрированием текста"""
        try:
            x = fret_data.get('x', 0)
            y = fret_data.get('y', 0)
            size = fret_data.get('size', 60)
            symbol = fret_data.get('symbol', 'I')
            color = DrawingElements.get_color_from_data(fret_data.get('color', [0, 0, 0]))
            style = fret_data.get('style', 'default')

            # Применяем стили текста
            if style == 'gradient_text':
                gradient = QLinearGradient(x - size, y - size, x + size, y + size)
                gradient.setColorAt(0, QColor(255, 100, 100))
                gradient.setColorAt(0.5, color)
                gradient.setColorAt(1, QColor(100, 100, 255))
                painter.setPen(QPen(gradient, 2))
            elif style == 'shadow':
                shadow_color = QColor(0, 0, 0, 100)
                painter.setPen(QPen(shadow_color, 3))
            elif style == 'glow':
                glow_color = QColor(255, 255, 255, 80)
                painter.setPen(QPen(glow_color, 4))
            elif style == 'outline':
                outline_color = QColor(255, 255, 255)
                painter.setPen(QPen(outline_color, 4))
            else:
                painter.setPen(QPen(color, 2))

            # Настраиваем шрифт
            font = QFont("Arial", size, QFont.Bold)
            painter.setFont(font)

            # ИДЕАЛЬНОЕ ЦЕНТРИРОВАНИЕ ТЕКСТА
            font_metrics = QFontMetrics(font)
            text_width = font_metrics.horizontalAdvance(symbol)
            text_height = font_metrics.height()

            text_x = x - text_width // 2
            text_y = y + text_height // 3

            painter.drawText(text_x, text_y, symbol)

        except Exception as e:
            print(f"❌ Ошибка рисования лада: {e}")

    @staticmethod
    def draw_note(painter, note_data):
        """Рисование ноты/пальца с поддержкой обводки - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            x = note_data.get('x', 0)
            y = note_data.get('y', 0)
            radius = note_data.get('radius', 15)
            style = note_data.get('style', 'red_3d')
            text_color = DrawingElements.get_color_from_data(note_data.get('text_color', [255, 255, 255]))

            # Определяем отображаемый текст
            display_text = note_data.get('display_text', 'finger')
            if display_text == 'note_name':
                symbol = note_data.get('note_name', '')
            elif display_text == 'symbol':
                symbol = note_data.get('symbol', '')
            else:  # finger
                symbol = note_data.get('finger', '1')

            # Параметры обводки
            outline_width = note_data.get('outline_width', 2)
            outline_color_data = note_data.get('outline_color', [0, 0, 0])
            outline_color = DrawingElements.get_color_from_data(outline_color_data)

            # РИСУЕМ ОБВОДКУ ЕСЛИ НУЖНО
            if outline_width > 0:
                painter.setPen(QPen(outline_color, outline_width))
                painter.setBrush(QBrush(outline_color))
                painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

            # Рисуем основную фигуру
            brush = DrawingElements.get_brush_from_style(style, x, y, radius)
            painter.setPen(Qt.NoPen)
            painter.setBrush(brush)

            inner_radius = max(1, radius - outline_width // 2)
            painter.drawEllipse(x - inner_radius, y - inner_radius, inner_radius * 2, inner_radius * 2)

            # Рисуем текст внутри круга
            if symbol:
                painter.setPen(QPen(text_color))

                # Настраиваем шрифт
                font_size = max(10, radius)
                font = QFont("Arial", font_size, QFont.Bold)
                painter.setFont(font)

                # Идеальное центрирование текста
                font_metrics = QFontMetrics(font)
                text_width = font_metrics.horizontalAdvance(symbol)
                text_height = font_metrics.height()

                # Центрируем по горизонтали и вертикали
                text_x = x - text_width // 2
                text_y = y + text_height // 4

                painter.drawText(text_x, text_y, symbol)

        except Exception as e:
            print(f"❌ Ошибка рисования ноты: {e}")

    @staticmethod
    def draw_barre(painter, barre_data):
        """Рисование баре с поддержкой обводки - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            x = barre_data.get('x', 0)
            y = barre_data.get('y', 0)
            width = barre_data.get('width', 100)
            height = barre_data.get('height', 20)
            radius = barre_data.get('radius', 10)
            style = barre_data.get('style', 'orange_gradient')

            # Параметры обводки
            outline_width = barre_data.get('outline_width', 2)
            outline_color_data = barre_data.get('outline_color', [0, 0, 0])
            outline_color = DrawingElements.get_color_from_data(outline_color_data)

            # РИСУЕМ ОБВОДКУ ЕСЛИ НУЖНО
            if outline_width > 0:
                painter.setPen(QPen(outline_color, outline_width))
                painter.setBrush(QBrush(outline_color))
                if radius > 0:
                    painter.drawRoundedRect(x, y, width, height, radius, radius)
                else:
                    painter.drawRect(x, y, width, height)

            # Рисуем основную фигуру
            brush = DrawingElements.get_brush_from_style(style, x, y, 0, width, height)
            painter.setPen(Qt.NoPen)
            painter.setBrush(brush)

            # Рисуем закругленный прямоугольник для баре
            inner_x = x + outline_width // 2
            inner_y = y + outline_width // 2
            inner_width = max(1, width - outline_width)
            inner_height = max(1, height - outline_width)

            if radius > 0:
                painter.drawRoundedRect(inner_x, inner_y, inner_width, inner_height, radius, radius)
            else:
                painter.drawRect(inner_x, inner_y, inner_width, inner_height)

        except Exception as e:
            print(f"❌ Ошибка рисования баре: {e}")