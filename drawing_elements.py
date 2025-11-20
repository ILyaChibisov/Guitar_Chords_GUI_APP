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

        # СТИЛИ ДЛЯ НОТ (50+ вариантов)
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
        elif style_name == "purple_3d":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 200, 255))
            gradient.setColorAt(0.7, QColor(180, 100, 230))
            gradient.setColorAt(1, QColor(140, 60, 200))
            return QBrush(gradient)
        elif style_name == "gold_3d":
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 230, 100))
            gradient.setColorAt(0.5, QColor(255, 200, 50))
            gradient.setColorAt(1, QColor(230, 170, 30))
            return QBrush(gradient)
        elif style_name == "glass":
            return QBrush(QColor(255, 255, 255, 180))
        elif style_name == "metal_note":
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(220, 220, 220))
            gradient.setColorAt(0.5, QColor(180, 180, 180))
            gradient.setColorAt(1, QColor(150, 150, 150))
            return QBrush(gradient)
        elif style_name == "fire":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 255, 150))
            gradient.setColorAt(0.5, QColor(255, 200, 50))
            gradient.setColorAt(1, QColor(255, 100, 0))
            return QBrush(gradient)
        elif style_name == "ice":
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(200, 230, 255))
            gradient.setColorAt(0.5, QColor(150, 200, 255))
            gradient.setColorAt(1, QColor(100, 170, 255))
            return QBrush(gradient)
        elif style_name == "soft_pink":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 200, 220))
            gradient.setColorAt(0.7, QColor(255, 150, 180))
            gradient.setColorAt(1, QColor(230, 100, 150))
            return QBrush(gradient)
        elif style_name == "mint_green":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 255, 180))
            gradient.setColorAt(0.7, QColor(120, 230, 120))
            gradient.setColorAt(1, QColor(80, 200, 80))
            return QBrush(gradient)
        elif style_name == "lavender":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(220, 200, 255))
            gradient.setColorAt(0.7, QColor(180, 160, 240))
            gradient.setColorAt(1, QColor(140, 120, 220))
            return QBrush(gradient)
        elif style_name == "peach":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 200, 150))
            gradient.setColorAt(0.7, QColor(255, 160, 100))
            gradient.setColorAt(1, QColor(230, 120, 80))
            return QBrush(gradient)
        elif style_name == "sky_blue":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(150, 200, 255))
            gradient.setColorAt(0.7, QColor(100, 160, 240))
            gradient.setColorAt(1, QColor(70, 130, 220))
            return QBrush(gradient)
        elif style_name == "lemon_yellow":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 255, 150))
            gradient.setColorAt(0.7, QColor(255, 230, 80))
            gradient.setColorAt(1, QColor(240, 200, 40))
            return QBrush(gradient)
        elif style_name == "coral":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 180, 150))
            gradient.setColorAt(0.7, QColor(255, 140, 100))
            gradient.setColorAt(1, QColor(230, 100, 70))
            return QBrush(gradient)
        elif style_name == "aqua_marine":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(150, 255, 220))
            gradient.setColorAt(0.7, QColor(100, 230, 190))
            gradient.setColorAt(1, QColor(70, 200, 160))
            return QBrush(gradient)
        elif style_name == "rose_quartz":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 200, 210))
            gradient.setColorAt(0.7, QColor(240, 160, 180))
            gradient.setColorAt(1, QColor(220, 120, 150))
            return QBrush(gradient)
        elif style_name == "seafoam":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 255, 200))
            gradient.setColorAt(0.7, QColor(140, 230, 170))
            gradient.setColorAt(1, QColor(100, 200, 140))
            return QBrush(gradient)
        elif style_name == "buttercup":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 230, 120))
            gradient.setColorAt(0.7, QColor(255, 200, 60))
            gradient.setColorAt(1, QColor(240, 170, 30))
            return QBrush(gradient)
        elif style_name == "lilac":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(220, 180, 255))
            gradient.setColorAt(0.7, QColor(190, 140, 240))
            gradient.setColorAt(1, QColor(160, 100, 220))
            return QBrush(gradient)
        elif style_name == "honey":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 220, 120))
            gradient.setColorAt(0.7, QColor(255, 180, 60))
            gradient.setColorAt(1, QColor(230, 150, 30))
            return QBrush(gradient)
        elif style_name == "turquoise":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(100, 240, 220))
            gradient.setColorAt(0.7, QColor(70, 200, 190))
            gradient.setColorAt(1, QColor(50, 170, 160))
            return QBrush(gradient)
        elif style_name == "apricot":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 200, 140))
            gradient.setColorAt(0.7, QColor(255, 160, 100))
            gradient.setColorAt(1, QColor(230, 120, 70))
            return QBrush(gradient)
        elif style_name == "periwinkle":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(200, 200, 255))
            gradient.setColorAt(0.7, QColor(160, 160, 240))
            gradient.setColorAt(1, QColor(120, 120, 220))
            return QBrush(gradient)
        elif style_name == "sage":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 220, 160))
            gradient.setColorAt(0.7, QColor(140, 190, 120))
            gradient.setColorAt(1, QColor(100, 160, 90))
            return QBrush(gradient)
        elif style_name == "melon":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 180, 140))
            gradient.setColorAt(0.7, QColor(255, 140, 100))
            gradient.setColorAt(1, QColor(230, 100, 70))
            return QBrush(gradient)
        elif style_name == "powder_blue":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 200, 255))
            gradient.setColorAt(0.7, QColor(140, 170, 240))
            gradient.setColorAt(1, QColor(100, 140, 220))
            return QBrush(gradient)
        elif style_name == "pistachio":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 255, 160))
            gradient.setColorAt(0.7, QColor(140, 230, 120))
            gradient.setColorAt(1, QColor(100, 200, 90))
            return QBrush(gradient)
        elif style_name == "blush":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 180, 190))
            gradient.setColorAt(0.7, QColor(240, 140, 160))
            gradient.setColorAt(1, QColor(220, 100, 130))
            return QBrush(gradient)
        elif style_name == "mauve":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(220, 180, 210))
            gradient.setColorAt(0.7, QColor(190, 140, 180))
            gradient.setColorAt(1, QColor(160, 100, 150))
            return QBrush(gradient)
        elif style_name == "cream":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 240, 200))
            gradient.setColorAt(0.7, QColor(255, 220, 160))
            gradient.setColorAt(1, QColor(240, 190, 120))
            return QBrush(gradient)
        elif style_name == "teal":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(0, 200, 200))
            gradient.setColorAt(0.7, QColor(0, 160, 160))
            gradient.setColorAt(1, QColor(0, 120, 120))
            return QBrush(gradient)
        elif style_name == "salmon":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 160, 140))
            gradient.setColorAt(0.7, QColor(255, 120, 100))
            gradient.setColorAt(1, QColor(230, 80, 70))
            return QBrush(gradient)
        elif style_name == "orchid":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 160, 220))
            gradient.setColorAt(0.7, QColor(200, 120, 200))
            gradient.setColorAt(1, QColor(170, 80, 170))
            return QBrush(gradient)
        elif style_name == "mint_blue":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(160, 220, 255))
            gradient.setColorAt(0.7, QColor(120, 190, 240))
            gradient.setColorAt(1, QColor(80, 160, 220))
            return QBrush(gradient)
        elif style_name == "pear":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(200, 255, 150))
            gradient.setColorAt(0.7, QColor(160, 230, 100))
            gradient.setColorAt(1, QColor(120, 200, 70))
            return QBrush(gradient)
        elif style_name == "rose_gold":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 200, 160))
            gradient.setColorAt(0.7, QColor(240, 160, 120))
            gradient.setColorAt(1, QColor(220, 120, 80))
            return QBrush(gradient)
        elif style_name == "lavender_gray":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(220, 200, 220))
            gradient.setColorAt(0.7, QColor(190, 170, 190))
            gradient.setColorAt(1, QColor(160, 140, 160))
            return QBrush(gradient)
        elif style_name == "honeydew":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(200, 255, 200))
            gradient.setColorAt(0.7, QColor(160, 230, 160))
            gradient.setColorAt(1, QColor(120, 200, 120))
            return QBrush(gradient)
        elif style_name == "peach_puff":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 200, 160))
            gradient.setColorAt(0.7, QColor(255, 160, 120))
            gradient.setColorAt(1, QColor(230, 120, 80))
            return QBrush(gradient)
        elif style_name == "azure":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 200, 255))
            gradient.setColorAt(0.7, QColor(140, 170, 240))
            gradient.setColorAt(1, QColor(100, 140, 220))
            return QBrush(gradient)
        elif style_name == "pale_green":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 255, 180))
            gradient.setColorAt(0.7, QColor(140, 230, 140))
            gradient.setColorAt(1, QColor(100, 200, 100))
            return QBrush(gradient)
        elif style_name == "light_coral":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 160, 160))
            gradient.setColorAt(0.7, QColor(240, 120, 120))
            gradient.setColorAt(1, QColor(220, 80, 80))
            return QBrush(gradient)
        elif style_name == "thistle":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(220, 180, 220))
            gradient.setColorAt(0.7, QColor(190, 140, 190))
            gradient.setColorAt(1, QColor(160, 100, 160))
            return QBrush(gradient)
        elif style_name == "wheat":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 220, 160))
            gradient.setColorAt(0.7, QColor(240, 190, 120))
            gradient.setColorAt(1, QColor(220, 160, 80))
            return QBrush(gradient)
        elif style_name == "light_cyan":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 255, 255))
            gradient.setColorAt(0.7, QColor(140, 230, 230))
            gradient.setColorAt(1, QColor(100, 200, 200))
            return QBrush(gradient)
        elif style_name == "pale_turquoise":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(160, 240, 240))
            gradient.setColorAt(0.7, QColor(120, 220, 220))
            gradient.setColorAt(1, QColor(80, 190, 190))
            return QBrush(gradient)
        elif style_name == "light_pink":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 180, 200))
            gradient.setColorAt(0.7, QColor(240, 140, 170))
            gradient.setColorAt(1, QColor(220, 100, 140))
            return QBrush(gradient)
        elif style_name == "light_salmon":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 160, 140))
            gradient.setColorAt(0.7, QColor(255, 120, 100))
            gradient.setColorAt(1, QColor(230, 80, 70))
            return QBrush(gradient)
        elif style_name == "light_skyblue":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(160, 200, 255))
            gradient.setColorAt(0.7, QColor(120, 170, 240))
            gradient.setColorAt(1, QColor(80, 140, 220))
            return QBrush(gradient)
        elif style_name == "light_green":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(160, 255, 160))
            gradient.setColorAt(0.7, QColor(120, 230, 120))
            gradient.setColorAt(1, QColor(80, 200, 80))
            return QBrush(gradient)
        elif style_name == "plum":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(220, 160, 220))
            gradient.setColorAt(0.7, QColor(190, 120, 190))
            gradient.setColorAt(1, QColor(160, 80, 160))
            return QBrush(gradient)
        elif style_name == "bisque":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 220, 180))
            gradient.setColorAt(0.7, QColor(255, 190, 140))
            gradient.setColorAt(1, QColor(240, 160, 100))
            return QBrush(gradient)

        return QBrush(QColor(255, 0, 0))  # Красный по умолчанию

    @staticmethod
    def draw_fret(painter, fret_data):
        """Рисование лада с ИСПРАВЛЕННЫМ центрированием текста"""
        try:
            x = fret_data.get('x', 0)
            y = fret_data.get('y', 0)
            size = fret_data.get('size', 20)
            symbol = fret_data.get('symbol', 'I')
            color = DrawingElements.get_color_from_data(fret_data.get('color', [0, 0, 0]))
            style = fret_data.get('style', 'default')
            font_family = fret_data.get('font_family', 'Arial')

            # Настраиваем шрифт
            font = QFont(font_family, size, QFont.Bold)
            painter.setFont(font)

            # ИДЕАЛЬНОЕ ЦЕНТРИРОВАНИЕ ТЕКСТА
            font_metrics = QFontMetrics(font)
            text_width = font_metrics.horizontalAdvance(symbol)
            text_height = font_metrics.height()

            text_x = x - text_width // 2
            text_y = y + text_height // 4

            # Применяем стили
            if style == 'shadow':
                # Рисуем тень
                shadow_color = QColor(0, 0, 0, 150)
                painter.setPen(QPen(shadow_color, 1))
                painter.drawText(text_x + 1, text_y + 1, symbol)
            elif style == 'outline':
                # Рисуем обводку
                outline_color = QColor(255, 255, 255)
                painter.setPen(QPen(outline_color, 3))
                painter.drawText(text_x, text_y, symbol)
            elif style == 'metallic':
                gradient = QLinearGradient(x - size, y - size, x + size, y + size)
                gradient.setColorAt(0, QColor(255, 255, 255))
                gradient.setColorAt(0.3, QColor(200, 200, 200))
                gradient.setColorAt(0.7, QColor(100, 100, 100))
                gradient.setColorAt(1, QColor(150, 150, 150))
                painter.setPen(QPen(gradient, 2))
            elif style == 'gold_embossed':
                gradient = QLinearGradient(x - size, y - size, x + size, y + size)
                gradient.setColorAt(0, QColor(255, 215, 0))
                gradient.setColorAt(0.5, QColor(218, 165, 32))
                gradient.setColorAt(1, QColor(184, 134, 11))
                painter.setPen(QPen(gradient, 3))
            elif style == 'silver_embossed':
                gradient = QLinearGradient(x - size, y - size, x + size, y + size)
                gradient.setColorAt(0, QColor(255, 255, 255))
                gradient.setColorAt(0.5, QColor(192, 192, 192))
                gradient.setColorAt(1, QColor(150, 150, 150))
                painter.setPen(QPen(gradient, 3))
            elif style == 'neon':
                neon_color = QColor(color)
                neon_color.setAlpha(200)
                painter.setPen(QPen(neon_color, 2))
            elif style == 'stamped':
                stamp_color = QColor(color)
                stamp_color.setAlpha(180)
                painter.setPen(QPen(stamp_color, 2))
            else:
                painter.setPen(QPen(color, 2))

            # Основной текст
            painter.drawText(text_x, text_y, symbol)

        except Exception as e:
            print(f"❌ Ошибка рисования лада: {e}")

    @staticmethod
    def draw_note(painter, note_data):
        """Рисование ноты/пальца с поддержкой обводки"""
        try:
            x = note_data.get('x', 0)
            y = note_data.get('y', 0)
            radius = note_data.get('radius', 12)
            style = note_data.get('style', 'red_3d')
            text_color = DrawingElements.get_color_from_data(note_data.get('text_color', [255, 255, 255]))
            font_style = note_data.get('font_style', 'normal')
            decoration = note_data.get('decoration', 'none')

            # Параметры обводки
            outline_width = note_data.get('outline_width', 2)
            outline_color_data = note_data.get('outline_color', [0, 0, 0])
            outline_color = DrawingElements.get_color_from_data(outline_color_data)

            # Определяем отображаемый текст
            display_text = note_data.get('display_text', 'finger')
            if display_text == 'note_name':
                symbol = note_data.get('note_name', '')
            elif display_text == 'symbol':
                symbol = note_data.get('symbol', '')
            else:  # finger
                symbol = note_data.get('finger', '1')

            # РИСУЕМ ОБВОДКУ
            if outline_width > 0:
                painter.setPen(QPen(outline_color, outline_width))
                painter.setBrush(QBrush(outline_color))
                painter.drawEllipse(x - radius - outline_width // 2, y - radius - outline_width // 2,
                                    (radius + outline_width) * 2, (radius + outline_width) * 2)

            # Рисуем основную фигуру
            brush = DrawingElements.get_brush_from_style(style, x, y, radius)
            painter.setPen(Qt.NoPen)
            painter.setBrush(brush)
            painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

            # Применяем дополнительное оформление
            if decoration == 'double_border':
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(x - radius + 2, y - radius + 2, (radius - 2) * 2, (radius - 2) * 2)
            elif decoration == 'glow':
                painter.setPen(QPen(QColor(255, 255, 255, 100), 4))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(x - radius - 2, y - radius - 2, (radius + 2) * 2, (radius + 2) * 2)
            elif decoration == 'shadow':
                painter.setPen(QPen(QColor(0, 0, 0, 80), 3))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(x - radius + 2, y - radius + 2, (radius - 2) * 2, (radius - 2) * 2)
            elif decoration == 'sparkle':
                sparkle_color = QColor(255, 255, 255, 200)
                painter.setBrush(sparkle_color)
                painter.setPen(Qt.NoPen)
                sparkle_radius = max(2, radius // 8)
                positions = [
                    (x - radius + sparkle_radius, y - radius + sparkle_radius),
                    (x + radius - sparkle_radius, y - radius + sparkle_radius),
                    (x - radius + sparkle_radius, y + radius - sparkle_radius),
                    (x + radius - sparkle_radius, y + radius - sparkle_radius)
                ]
                for pos_x, pos_y in positions:
                    painter.drawEllipse(pos_x, pos_y, sparkle_radius * 2, sparkle_radius * 2)
            elif decoration == 'dotted_border':
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                pen = painter.pen()
                pen.setStyle(Qt.DashLine)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(x - radius + 1, y - radius + 1, (radius - 1) * 2, (radius - 1) * 2)

            # Рисуем текст внутри круга
            if symbol:
                painter.setPen(QPen(text_color))

                # Настраиваем шрифт
                font_size = max(8, radius - 2)
                font = QFont("Arial", font_size)

                if font_style == 'bold':
                    font.setWeight(QFont.Bold)
                elif font_style == 'light':
                    font.setWeight(QFont.Light)
                elif font_style == 'italic':
                    font.setItalic(True)
                elif font_style == 'bold_italic':
                    font.setWeight(QFont.Bold)
                    font.setItalic(True)

                painter.setFont(font)

                # Идеальное центрирование текста
                font_metrics = QFontMetrics(font)
                text_width = font_metrics.horizontalAdvance(symbol)
                text_height = font_metrics.height()

                text_x = x - text_width // 2
                text_y = y + text_height // 4

                painter.drawText(text_x, text_y, symbol)

        except Exception as e:
            print(f"❌ Ошибка рисования ноты: {e}")

    @staticmethod
    def draw_barre(painter, barre_data):
        """Рисование баре с правильным позиционированием"""
        try:
            x = barre_data.get('x', 0)
            y = barre_data.get('y', 0)
            width = barre_data.get('width', 100)
            height = barre_data.get('height', 15)
            radius = barre_data.get('radius', 7)
            style = barre_data.get('style', 'orange_gradient')
            decoration = barre_data.get('decoration', 'none')

            print(f"🎸 ОТРИСОВКА БАРЕ:")
            print(f"   Позиция: ({x}, {y})")
            print(f"   Размер: {width}x{height}")
            print(f"   Стиль: {style}")

            # Параметры обводки
            outline_width = barre_data.get('outline_width', 2)
            outline_color_data = barre_data.get('outline_color', [0, 0, 0])
            outline_color = DrawingElements.get_color_from_data(outline_color_data)

            # 🔥 ИСПРАВЛЕНИЕ 1: ОБВОДКА БЕЗ СМЕЩЕНИЯ!
            # РИСУЕМ ОБВОДКУ (только контур) - ТЕ ЖЕ КООРДИНАТЫ!
            if outline_width > 0:
                painter.setPen(QPen(outline_color, outline_width))
                painter.setBrush(Qt.NoBrush)  # Важно: без заливки для обводки!
                painter.drawRoundedRect(x, y, width, height, radius, radius)
                print(f"   🖌️ Обводка: ширина {outline_width}px")

            # 🔥 ИСПРАВЛЕНИЕ 2: ОСНОВНАЯ ФИГУРА - ТЕ ЖЕ КООРДИНАТЫ!
            # Рисуем основную фигуру (заливку)
            brush = DrawingElements.get_brush_from_style(style, x, y, 0, width, height)
            painter.setPen(Qt.NoPen)
            painter.setBrush(brush)
            painter.drawRoundedRect(x, y, width, height, radius, radius)
            print(f"   🎨 Основная фигура")

            # 🔥 ИСПРАВЛЕНИЕ 3: ДЕКОРАЦИИ - МИНИМАЛЬНЫЕ СМЕЩЕНИЯ
            # Применяем декорации (с небольшими корректировками)
            if decoration == 'shadow':
                shadow_color = QColor(0, 0, 0, 80)
                painter.setPen(QPen(shadow_color, 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawRoundedRect(x + 1, y + 1, width, height, radius, radius)
                print(f"   🌑 Тень")
            elif decoration == 'glow':
                glow_color = QColor(255, 255, 255, 60)
                painter.setPen(QPen(glow_color, 3))
                painter.setBrush(Qt.NoBrush)
                painter.drawRoundedRect(x, y, width, height, radius, radius)
                print(f"   ✨ Свечение")
            elif decoration == 'double_border':
                border_color = QColor(255, 255, 255)
                painter.setPen(QPen(border_color, 1))
                painter.setBrush(Qt.NoBrush)
                painter.drawRoundedRect(x + 1, y + 1, width - 2, height - 2, radius, radius)
                print(f"   🎭 Двойная обводка")
            elif decoration == 'stripes' and style == 'striped':
                stripe_color = QColor(189, 183, 107).darker(120)
                stripe_color.setAlpha(180)
                painter.setPen(QPen(stripe_color, 1))
                stripe_spacing = height // 4
                for i in range(1, 4):
                    stripe_y = y + i * stripe_spacing
                    painter.drawLine(x + 2, stripe_y, x + width - 2, stripe_y)
                print(f"   📏 Полосы")

            print(f"✅ Баре отрисовано успешно в позиции ({x}, {y})")

        except Exception as e:
            print(f"❌ Ошибка рисования баре: {e}")
            import traceback
            traceback.print_exc()

    @staticmethod
    def draw_open_string(painter, open_string_data):
        """Рисование открытой струны (кружок)"""
        try:
            x = open_string_data.get('x', 0)
            y = open_string_data.get('y', 0)
            radius = open_string_data.get('radius', 8)

            # Для открытых струн используем прозрачную заливку и обводку
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        except Exception as e:
            print(f"❌ Ошибка рисования открытой струны: {e}")

    @staticmethod
    def draw_muted_string(painter, muted_string_data):
        """Рисование заглушенной струны (крестик)"""
        try:
            x = muted_string_data.get('x', 0)
            y = muted_string_data.get('y', 0)
            size = muted_string_data.get('size', 10)

            painter.setPen(QPen(QColor(0, 0, 0), 3))
            # Рисуем крестик
            painter.drawLine(x - size, y - size, x + size, y + size)
            painter.drawLine(x + size, y - size, x - size, y + size)

        except Exception as e:
            print(f"❌ Ошибка рисования заглушенной струны: {e}")