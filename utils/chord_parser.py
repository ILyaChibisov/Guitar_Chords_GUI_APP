import re
import html


class ChordParser:
    """Утилиты для парсинга и обработки аккордов"""

    @staticmethod
    def extract_chords_from_text(text):
        """Извлекает аккорды из текста"""
        # Регулярное выражение для поиска аккордов
        chord_pattern = r'[A-G][#b]?(?:m|maj|min|dim|aug|sus)?[0-9]*(?:\/[A-G][#b]?)?'
        return re.findall(chord_pattern, text)

    @staticmethod
    def create_chord_links(text, chords_list):
        """Создает HTML-ссылки для аккордов"""
        chord_links_dict = {}
        for chord in set(chords_list):
            safe_chord = html.escape(chord)
            link_html = f'<a href="{safe_chord}" style="color: #3498db; font-weight: bold; text-decoration: none; background: rgba(52, 152, 219, 0.1); padding: 2px 6px; border-radius: 4px;">{safe_chord}</a>'
            chord_links_dict[chord] = link_html

        full_text_raw = text
        for chord in sorted(set(chords_list), key=len, reverse=True):
            if not chord:
                continue
            safe_chord = html.escape(chord)
            link_html = chord_links_dict[chord]
            pattern = r'(?<![a-zA-Z0-9#\-/])' + re.escape(chord) + r'(?![a-zA-Z0-9#\-/])'
            full_text_raw = re.sub(pattern, link_html, full_text_raw)

        return full_text_raw