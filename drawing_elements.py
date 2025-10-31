"""
Модуль для отрисовки элементов аккордов на изображениях
"""

from PIL import Image, ImageDraw, ImageFont
import math


def draw_chord_elements(draw, drawing_data, display_type, image_size):
    """
    Отрисовывает элементы аккорда на изображении
    """
    print(f"🎨 Начало отрисовки: {len(drawing_data['elements'])} элементов")

    try:
        if not drawing_data or 'elements' not in drawing_data:
            print("❌ Нет данных для отрисовки")
            return

        elements = drawing_data['elements']
        print(f"📋 Всего элементов: {len(elements)}")

        for i, element in enumerate(elements):
            if not isinstance(element, dict):
                print(f"⚠️ Элемент {i} не словарь: {type(element)}")
                continue

            element_type = element.get('type')
            element_data = element.get('data', {})

            print(f"🔍 Элемент {i}: {element_type}, данные: {list(element_data.keys())}")

            try:
                if element_type == 'fret':
                    print(f"  🎯 Отрисовка лада: {element_data.get('symbol', '')}")
                    draw_fret(draw, element_data)
                elif element_type == 'note':
                    print(f"  🎯 Отрисовка ноты: {element_data.get('display_text', '')}")
                    draw_note(draw, element_data, display_type, image_size)
                elif element_type == 'barre':
                    print(f"  🎯 Отрисовка баррэ")
                    draw_barre(draw, element_data)
                else:
                    print(f"⚠️ Неизвестный тип элемента: {element_type}")

            except Exception as e:
                print(f"❌ Ошибка отрисовки элемента {element_type}: {e}")
                import traceback
                traceback.print_exc()

        print("✅ Отрисовка завершена")

    except Exception as e:
        print(f"❌ Критическая ошибка в draw_chord_elements: {e}")
        import traceback
        traceback.print_exc()


def draw_fret(draw, data):
    """Отрисовывает лад"""
    try:
        x = data.get('x', 0)
        y = data.get('y', 0)
        symbol = data.get('symbol', '')
        color = tuple(data.get('color', [0, 0, 0]))
        size = data.get('size', 60)

        print(f"    📍 Лад: {symbol} на ({x}, {y})")

        # Создаем шрифт
        try:
            font = ImageFont.truetype("arial.ttf", size // 2)
        except:
            try:
                font = ImageFont.truetype("times.ttf", size // 2)
            except:
                font = ImageFont.load_default()

        # Рисуем текст
        bbox = draw.textbbox((x, y), symbol, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = x - text_width // 2
        text_y = y - text_height // 2

        draw.text((text_x, text_y), symbol, fill=color, font=font)
        print(f"    ✅ Лад отрисован")

    except Exception as e:
        print(f"❌ Ошибка отрисовки лада: {e}")


def draw_note(draw, data, display_type, image_size):
    """Отрисовывает ноту/палец"""
    try:
        x = data.get('x', 0)
        y = data.get('y', 0)
        radius = data.get('radius', 52)
        display_text = data.get('display_text', 'symbol')

        # Получаем текст для отображения
        if display_text == 'finger':
            text = data.get('finger', '')
        elif display_text == 'note_name':
            text = data.get('note_name', '')
        else:
            text = data.get('symbol', '')

        print(f"    📍 Нота: {text} на ({x}, {y}), радиус: {radius}")

        # ПРОСТЫЕ ЦВЕТА
        fill_color = (255, 215, 0)  # Ярко-желтый
        outline_color = (0, 0, 0)   # Черный
        text_color = (0, 0, 0)      # Черный

        # Рисуем круг
        bbox = [x - radius, y - radius, x + radius, y + radius]
        print(f"    🔵 Круг: {bbox}")

        draw.ellipse(bbox, fill=fill_color, outline=outline_color, width=3)
        print(f"    ✅ Круг отрисован")

        # Рисуем текст
        if text:
            try:
                font_size = max(radius // 2, 20)
                print(f"    🔤 Текст: '{text}', размер шрифта: {font_size}")

                font = ImageFont.truetype("arial.ttf", font_size)
                bbox = draw.textbbox((x, y), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                text_x = x - text_width // 2
                text_y = y - text_height // 2

                draw.text((text_x, text_y), text, fill=text_color, font=font)
                print(f"    ✅ Текст отрисован")

            except Exception as font_error:
                print(f"    ⚠️ Ошибка шрифта: {font_error}")
                font = ImageFont.load_default()
                bbox = draw.textbbox((x, y), text, font=font)
                text_x = x - (bbox[2] - bbox[0]) // 2
                text_y = y - (bbox[3] - bbox[1]) // 2
                draw.text((text_x, text_y), text, fill=text_color, font=font)
                print(f"    ✅ Текст отрисован (запасной шрифт)")

    except Exception as e:
        print(f"❌ Ошибка отрисовки ноты: {e}")
        import traceback
        traceback.print_exc()


def draw_barre(draw, data):
    """Отрисовывает баррэ"""
    try:
        x = data.get('x', 0)
        y = data.get('y', 0)
        width = data.get('width', 100)
        height = data.get('height', 320)
        radius = data.get('radius', 50)

        print(f"    📍 Баррэ: ({x}, {y}), размер: {width}x{height}")

        # ПРОСТОЙ ЦВЕТ
        fill_color = (189, 183, 107)  # Цвет баррэ
        outline_color = (0, 0, 0)     # Черный контур

        # Рисуем закругленный прямоугольник
        bbox = [x - width//2, y - height//2, x + width//2, y + height//2]
        print(f"    🟦 Прямоугольник: {bbox}")

        draw.rounded_rectangle(bbox, radius=radius, fill=fill_color, outline=outline_color, width=3)
        print(f"    ✅ Баррэ отрисован")

    except Exception as e:
        print(f"❌ Ошибка отрисовки баррэ: {e}")
        import traceback
        traceback.print_exc()