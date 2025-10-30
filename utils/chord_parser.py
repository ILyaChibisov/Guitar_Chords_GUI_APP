import re
import html


class ChordParser:
    """Утилиты для парсинга и обработки аккордов"""

    @staticmethod
    def extract_chords_from_text(text):
        """Извлекает аккорды из текста"""
        chord_pattern = r'[A-G][#b]?(?:m|maj|min|dim|aug|sus)?[0-9]*(?:\/[A-G][#b]?)?'
        return re.findall(chord_pattern, text)

    @staticmethod
    def ultra_simple_replace(text, chords_list):
        """Ультра-простой метод замены - гарантирует отсутствие дублирования HTML"""
        if not text.strip():
            return ""

        # Удаляем пустые строки
        lines = [line for line in text.split('\n') if line.strip()]
        if not lines:
            return ""

        if not chords_list:
            # Просто возвращаем экранированный текст без пустых строк
            return '<br>'.join(html.escape(line) for line in lines)

        # Получаем полный список всех возможных аккордов из const
        try:
            from const import CHORDS_TYPE_LIST
            all_chords_set = set()
            for chord_group in CHORDS_TYPE_LIST:
                all_chords_set.update(chord_group)

            # Фильтруем только те аккорды, которые есть в таблице
            valid_chords = [chord for chord in chords_list if chord in all_chords_set]

        except ImportError:
            valid_chords = chords_list

        # Сортируем аккорды по длине в обратном порядке
        sorted_chords = sorted(valid_chords, key=len, reverse=True)

        processed_lines = []
        for line in lines:
            # Создаем список для частей строки
            parts = []
            current_pos = 0

            # Находим все позиции аккордов
            chord_positions = []
            for chord in sorted_chords:
                start = 0
                while start < len(line):
                    pos = line.find(chord, start)
                    if pos == -1:
                        break

                    # Проверяем, что это отдельный аккорд
                    is_valid = True

                    # Проверяем символ перед аккордом
                    if pos > 0:
                        prev_char = line[pos - 1]
                        if prev_char.isalnum() and prev_char not in ' \t\n\r([{-':
                            is_valid = False

                    # Проверяем символ после аккорда
                    end_pos = pos + len(chord)
                    if end_pos < len(line):
                        next_char = line[end_pos]
                        if next_char.isalnum() and next_char not in ' \t\n\r)]},':
                            is_valid = False

                    if is_valid:
                        chord_positions.append((pos, chord))

                    start = pos + len(chord)

            # Сортируем позиции
            chord_positions.sort()

            # Убираем пересекающиеся аккорды
            filtered_positions = []
            last_end = -1
            for pos, chord in chord_positions:
                chord_end = pos + len(chord)
                if pos >= last_end:
                    filtered_positions.append((pos, chord))
                    last_end = chord_end

            # Если нет аккордов, просто экранируем строку
            if not filtered_positions:
                processed_lines.append(html.escape(line))
                continue

            # Собираем строку из частей
            last_pos = 0
            for pos, chord in filtered_positions:
                # Добавляем текст до аккорда
                if pos > last_pos:
                    text_before = line[last_pos:pos]
                    parts.append(html.escape(text_before))

                # Добавляем аккорд как ссылку
                safe_chord = html.escape(chord)
                chord_html = f'<a href="{safe_chord}" style="color: #3498db; font-weight: bold; text-decoration: none; background: rgba(52, 152, 219, 0.1); padding: 2px 6px; border-radius: 4px;">{safe_chord}</a>'
                parts.append(chord_html)

                last_pos = pos + len(chord)

            # Добавляем оставшийся текст
            if last_pos < len(line):
                text_after = line[last_pos:]
                parts.append(html.escape(text_after))

            processed_lines.append(''.join(parts))

        return '<br>'.join(processed_lines)

    @staticmethod
    def direct_text_processing(text, chords_list):
        """Прямая обработка текста - максимально простой и надежный подход"""
        if not text.strip():
            return ""

        lines = [line for line in text.split('\n') if line.strip()]
        if not lines:
            return ""

        if not chords_list:
            return '<br>'.join(html.escape(line) for line in lines)

        # Получаем все аккорды из таблицы
        try:
            from const import CHORDS_TYPE_LIST
            all_chords = []
            for chord_group in CHORDS_TYPE_LIST:
                all_chords.extend(chord_group)

            # Используем только те аккорды, которые есть в таблице
            chords_to_use = [chord for chord in chords_list if chord in all_chords]
        except ImportError:
            chords_to_use = chords_list

        # Сортируем по длине (длинные сначала)
        sorted_chords = sorted(chords_to_use, key=len, reverse=True)

        processed_lines = []
        for line in lines:
            # Разбиваем строку на слова и пробелы
            segments = re.split(r'(\s+)', line)
            processed_segments = []

            for segment in segments:
                # Если сегмент не пробелы и содержит буквы/цифры
                if segment.strip() and not segment.isspace():
                    # Проверяем, является ли сегмент аккордом
                    is_chord = False
                    for chord in sorted_chords:
                        if segment == chord:
                            # Это аккорд - заменяем на ссылку
                            safe_chord = html.escape(chord)
                            chord_html = f'<a href="{safe_chord}" style="color: #3498db; font-weight: bold; text-decoration: none; background: rgba(52, 152, 219, 0.1); padding: 2px 6px; border-radius: 4px;">{safe_chord}</a>'
                            processed_segments.append(chord_html)
                            is_chord = True
                            break

                    if not is_chord:
                        # Это не аккорд - просто экранируем
                        processed_segments.append(html.escape(segment))
                else:
                    # Пробелы оставляем как есть
                    processed_segments.append(segment)

            processed_lines.append(''.join(processed_segments))

        return '<br>'.join(processed_lines)

    @staticmethod
    def word_by_word_processing(text, chords_list):
        """Обработка слово-за-словом - самый надежный метод"""
        if not text.strip():
            return ""

        lines = [line for line in text.split('\n') if line.strip()]
        if not lines:
            return ""

        if not chords_list:
            return '<br>'.join(html.escape(line) for line in lines)

        # Получаем все аккорды из таблицы
        try:
            from const import CHORDS_TYPE_LIST
            chord_set = set()
            for chord_group in CHORDS_TYPE_LIST:
                chord_set.update(chord_group)

            valid_chords = [chord for chord in chords_list if chord in chord_set]
        except ImportError:
            valid_chords = chords_list

        processed_lines = []
        for line in lines:
            # Разбиваем строку на слова, сохраняя пробелы
            words_and_spaces = re.split(r'(\S+)', line)
            processed_parts = []

            for part in words_and_spaces:
                if not part.strip():  # Пробелы
                    processed_parts.append(part)
                else:  # Слово
                    # Проверяем, является ли слово аккордом
                    if part in valid_chords:
                        safe_chord = html.escape(part)
                        chord_html = f'<a href="{safe_chord}" style="color: #3498db; font-weight: bold; text-decoration: none; background: rgba(52, 152, 219, 0.1); padding: 2px 6px; border-radius: 4px;">{safe_chord}</a>'
                        processed_parts.append(chord_html)
                    else:
                        processed_parts.append(html.escape(part))

            processed_lines.append(''.join(processed_parts))

        return '<br>'.join(processed_lines)
