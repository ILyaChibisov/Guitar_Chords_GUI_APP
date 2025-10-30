#!/usr/bin/env python3
"""
Модуль для отрисовки элементов гитарных аккордов
"""

from PIL import Image, ImageDraw, ImageFont
import math


class DrawingElements:
    """Класс для отрисовки элементов аккордов на изображении"""

    @staticmethod
    def draw_note(draw, data):
        """Рисует ноту (круг с цифрой/буквой)"""
        x = data['x']
        y = data['y']
        radius = data.get('radius', 15)
        text = data.get('text', '')
        fill_color = tuple(data.get('fill_color', [255, 255, 255]))
        outline_color = tuple(data.get('outline_color', [0, 0, 0]))
        outline_width = data.get('outline_width', 2)
        text_color = tuple(data.get('text_color', [0, 0, 0]))

        # Рисуем внешний круг (обводка)
        if outline_width > 0:
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius],
                fill=outline_color,
                outline=outline_color
            )

        # Рисуем внутренний круг
        inner_radius = radius - outline_width
        if inner_radius > 0:
            draw.ellipse(
                [x - inner_radius, y - inner_radius, x + inner_radius, y + inner_radius],
                fill=fill_color,
                outline=fill_color
            )

        # Рисуем текст
        if text:
            try:
                # Пробуем разные шрифты
                font_sizes = [12, 14, 16, 18]
                font = None

                for size in font_sizes:
                    try:
                        font = ImageFont.truetype("arial.ttf", size)
                        break
                    except:
                        try:
                            font = ImageFont.truetype("DejaVuSans.ttf", size)
                            break
                        except:
                            continue

                if font is None:
                    # Используем стандартный шрифт
                    font = ImageFont.load_default()

                # Получаем размеры текста
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # Вычисляем позицию для центрирования
                text_x = x - text_width // 2
                text_y = y - text_height // 2

                # Рисуем текст
                draw.text((text_x, text_y), text, fill=text_color, font=font)

            except Exception as e:
                print(f"⚠️ Ошибка отрисовки текста '{text}': {e}")
                # Рисуем простой круг без текста
                pass

    @staticmethod
    def draw_barre(draw, data):
        """Рисует барре (прямоугольник)"""
        x = data['x']
        y = data['y']
        width = data.get('width', 100)
        height = data.get('height', 20)
        fill_color = tuple(data.get('fill_color', [100, 100, 100, 200]))
        outline_color = tuple(data.get('outline_color', [0, 0, 0]))
        outline_width = data.get('outline_width', 2)
        corner_radius = data.get('corner_radius', 5)

        # Рисуем закругленный прямоугольник
        DrawingElements._draw_rounded_rectangle(
            draw,
            [x, y, x + width, y + height],
            fill_color,
            outline_color,
            outline_width,
            corner_radius
        )

    @staticmethod
    def draw_fret(draw, data):
        """Рисует обозначение лада (римские/арабские цифры)"""
        x = data['x']
        y = data['y']
        text = data.get('text', '')
        text_color = tuple(data.get('text_color', [0, 0, 0]))
        background_color = tuple(data.get('background_color', [255, 255, 255, 200]))
        padding = data.get('padding', 5)

        if not text:
            return

        try:
            # Пробуем разные шрифты
            font_sizes = [10, 12, 14]
            font = None

            for size in font_sizes:
                try:
                    font = ImageFont.truetype("arial.ttf", size)
                    break
                except:
                    try:
                        font = ImageFont.truetype("DejaVuSans.ttf", size)
                        break
                    except:
                        continue

            if font is None:
                font = ImageFont.load_default()

            # Получаем размеры текста
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Рисуем фон
            bg_rect = [
                x - padding,
                y - padding,
                x + text_width + padding,
                y + text_height + padding
            ]

            draw.rectangle(bg_rect, fill=background_color)

            # Рисуем текст
            draw.text((x, y), text, fill=text_color, font=font)

        except Exception as e:
            print(f"⚠️ Ошибка отрисовки лада '{text}': {e}")

    @staticmethod
    def _draw_rounded_rectangle(draw, coordinates, fill, outline, width=1, radius=0):
        """Рисует закругленный прямоугольник"""
        x1, y1, x2, y2 = coordinates

        if radius == 0:
            # Простой прямоугольник
            if fill:
                draw.rectangle(coordinates, fill=fill)
            if outline and width > 0:
                draw.rectangle(coordinates, outline=outline, width=width)
            return

        # Закругленные углы
        if fill:
            # Основной прямоугольник
            draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
            draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

            # Углы
            draw.pieslice([x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=fill)
            draw.pieslice([x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=fill)
            draw.pieslice([x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=fill)
            draw.pieslice([x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=fill)

        # Обводка
        if outline and width > 0:
            # Вертикальные линии
            draw.line([(x1 + radius, y1), (x1 + radius, y2 - radius)], fill=outline, width=width)
            draw.line([(x2 - radius, y1), (x2 - radius, y2 - radius)], fill=outline, width=width)

            # Горизонтальные линии
            draw.line([(x1 + radius, y1), (x2 - radius, y1)], fill=outline, width=width)
            draw.line([(x1 + radius, y2), (x2 - radius, y2)], fill=outline, width=width)

            # Угловые дуги
            draw.arc([x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=outline, width=width)
            draw.arc([x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=outline, width=width)
            draw.arc([x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=outline, width=width)
            draw.arc([x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=outline, width=width)

    @staticmethod
    def draw_string_number(draw, data):
        """Рисует номер струны"""
        x = data['x']
        y = data['y']
        number = data.get('number', '')
        text_color = tuple(data.get('text_color', [0, 0, 0]))

        if not number:
            return

        try:
            font_sizes = [10, 12]
            font = None

            for size in font_sizes:
                try:
                    font = ImageFont.truetype("arial.ttf", size)
                    break
                except:
                    try:
                        font = ImageFont.truetype("DejaVuSans.ttf", size)
                        break
                    except:
                        continue

            if font is None:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), str(number), font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            text_x = x - text_width // 2
            text_y = y - text_height // 2

            draw.text((text_x, text_y), str(number), fill=text_color, font=font)

        except Exception as e:
            print(f"⚠️ Ошибка отрисовки номера струны '{number}': {e}")

    @staticmethod
    def draw_fingering(draw, data):
        """Рисует обозначение пальцев (T, 1, 2, 3, 4)"""
        x = data['x']
        y = data['y']
        finger = data.get('finger', '')
        text_color = tuple(data.get('text_color', [0, 0, 0]))
        background_color = tuple(data.get('background_color', [255, 255, 255]))

        if not finger:
            return

        try:
            font_sizes = [10, 12]
            font = None

            for size in font_sizes:
                try:
                    font = ImageFont.truetype("arial.ttf", size)
                    break
                except:
                    try:
                        font = ImageFont.truetype("DejaVuSans.ttf", size)
                        break
                    except:
                        continue

            if font is None:
                font = ImageFont.load_default()

            # Рисуем круг
            radius = 10
            draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                         fill=background_color, outline=text_color, width=1)

            # Рисуем текст
            bbox = draw.textbbox((0, 0), finger, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            text_x = x - text_width // 2
            text_y = y - text_height // 2

            draw.text((text_x, text_y), finger, fill=text_color, font=font)

        except Exception as e:
            print(f"⚠️ Ошибка отрисовки пальца '{finger}': {e}")


def draw_chord_elements(draw, drawing_data, display_type="fingers", image_size=None):
    """
    Основная функция для отрисовки всех элементов аккорда

    Args:
        draw: ImageDraw объект
        drawing_data: словарь с данными для отрисовки
        display_type: "fingers" (пальцы) или "notes" (ноты)
        image_size: размер изображения (width, height)
    """
    if not drawing_data:
        return

    elements = drawing_data.get('elements', [])

    for element in elements:
        element_type = element.get('type')
        data = element.get('data', {})

        try:
            if element_type == 'note':
                DrawingElements.draw_note(draw, data)
            elif element_type == 'barre':
                DrawingElements.draw_barre(draw, data)
            elif element_type == 'fret':
                DrawingElements.draw_fret(draw, data)
            elif element_type == 'string_number':
                DrawingElements.draw_string_number(draw, data)
            elif element_type == 'fingering':
                if display_type == "fingers":
                    DrawingElements.draw_fingering(draw, data)
            # Добавьте другие типы элементов по необходимости

        except Exception as e:
            print(f"⚠️ Ошибка отрисовки элемента {element_type}: {e}")
            continue


# Упрощенная версия для обратной совместимости
def draw_elements_simple(draw, elements, crop_rect=None):
    """
    Упрощенная функция для отрисовки (совместимость со старым кодом)
    """
    for element in elements:
        element_type = element.get('type')
        data = element.get('data', {})

        # Адаптируем координаты если нужно
        if crop_rect and 'x' in data and 'y' in data:
            crop_x, crop_y, _, _ = crop_rect
            data = data.copy()
            data['x'] = data['x'] - crop_x
            data['y'] = data['y'] - crop_y

        try:
            if element_type == 'note':
                DrawingElements.draw_note(draw, data)
            elif element_type == 'barre':
                DrawingElements.draw_barre(draw, data)
            elif element_type == 'fret':
                DrawingElements.draw_fret(draw, data)

        except Exception as e:
            print(f"⚠️ Ошибка отрисовки элемента {element_type}: {e}")