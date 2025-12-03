# tools/chord_converter.py
import os
import sys
import base64
import json
import pandas as pd
from pathlib import Path


class ResourceConverter:
    def __init__(self, source_dir="chords_config"):
        self.source_dir = Path(source_dir)
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

    def convert_excel_to_python(self):
        """Конвертирует Excel файл в Python модуль"""
        excel_path = self.source_dir / "chord_config.xlsx"
        if not excel_path.exists():
            print(f"❌ Excel файл не найден: {excel_path}")
            return False

        try:
            # Читаем все листы
            print("📊 Чтение Excel файла...")
            chords_df = pd.read_excel(excel_path, sheet_name='CHORDS')
            ram_df = pd.read_excel(excel_path, sheet_name='RAM')
            note_df = pd.read_excel(excel_path, sheet_name='NOTE')

            # Обрабатываем числовые колонки
            chords_data = self.process_chords_data(chords_df.to_dict('records'))
            ram_data = self.process_ram_data(ram_df.to_dict('records'))
            note_data = self.process_note_data(note_df.to_dict('records'))

            # Создаем Python файл
            output_file = self.data_dir / "chords_config.py"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('"""\nДанные аккордов из Excel\n"""\n\n')
                f.write('CHORDS_DATA = ')

                # Конвертируем в JSON строку и заменяем null на None
                json_str = json.dumps(chords_data, ensure_ascii=False, indent=2)
                json_str = json_str.replace(': null', ': None').replace(':null', ':None')
                f.write(json_str)

                f.write('\n\nRAM_DATA = ')
                json_str = json.dumps(ram_data, ensure_ascii=False, indent=2)
                json_str = json_str.replace(': null', ': None').replace(':null', ':None')
                f.write(json_str)

                f.write('\n\nNOTE_DATA = ')
                json_str = json.dumps(note_data, ensure_ascii=False, indent=2)
                json_str = json_str.replace(': null', ': None').replace(':null', ':None')
                f.write(json_str)

                f.write('\n')

            print(f"✅ Excel данные сохранены в: {output_file}")
            print(f"   - Аккордов: {len(chords_data)}")
            print(f"   - RAM записей: {len(ram_data)}")
            print(f"   - NOTE записей: {len(note_data)}")
            return True

        except Exception as e:
            print(f"❌ Ошибка конвертации Excel: {e}")
            return False

    def process_chords_data(self, chords_records):
        """Обрабатывает числовые данные в записях аккордов"""
        processed_data = []

        for record in chords_records:
            processed_record = {}

            for key, value in record.items():
                # Обрабатываем только колонки с числовыми данными
                if key in ['FNL', 'FN', 'FPOL', 'FPXL', 'FP1', 'FP2', 'FP3', 'FP4']:
                    processed_record[key] = self.process_number_field(value)
                else:
                    processed_record[key] = self.replace_nan_with_none(value)

            processed_data.append(processed_record)

        return processed_data

    def process_ram_data(self, ram_records):
        """Обрабатывает числовые данные в записях RAM"""
        processed_data = []

        for record in ram_records:
            processed_record = {}

            for key, value in record.items():
                # Обрабатываем колонку LAD
                if key == 'LAD':
                    processed_record[key] = self.process_number_field(value)
                else:
                    processed_record[key] = self.replace_nan_with_none(value)

            processed_data.append(processed_record)

        return processed_data

    def process_note_data(self, note_records):
        """Обрабатывает числовые данные в записях NOTE"""
        processed_data = []

        for record in note_records:
            processed_record = {}

            for key, value in record.items():
                # Обрабатываем только числовые колонки (кроме *_ELEM)
                if key in ['FNL', 'FN', 'FPXL', 'FPOL', 'FP1', 'FP2', 'FP3', 'FP4']:
                    processed_record[key] = self.process_single_number_field(value)
                else:
                    processed_record[key] = self.replace_nan_with_none(value)

            processed_data.append(processed_record)

        return processed_data

    def process_number_field(self, value):
        """Обрабатывает числовое поле: может быть None, одним числом или списком чисел"""
        if pd.isna(value):
            return None

        # Если значение - число (int или float)
        if isinstance(value, (int, float)):
            return int(value)  # Конвертируем в целое число

        # Если значение - строка
        if isinstance(value, str):
            # Удаляем пробелы и разбиваем по запятым
            parts = [part.strip() for part in value.split(',')]

            # Фильтруем пустые строки и конвертируем в числа
            numbers = []
            for part in parts:
                if part:  # Не пустая строка
                    try:
                        # Пробуем конвертировать в число
                        num = float(part)
                        numbers.append(int(num))  # Конвертируем в целое
                    except ValueError:
                        # Если не число, оставляем как есть
                        numbers.append(part)

            # Если только одно число, возвращаем его, иначе возвращаем список
            return numbers[0] if len(numbers) == 1 else numbers

        # Для любых других типов возвращаем как есть
        return value

    def process_single_number_field(self, value):
        """Обрабатывает одиночное числовое поле - конвертирует в целое число"""
        if pd.isna(value):
            return None

        # Если значение - число (int или float)
        if isinstance(value, (int, float)):
            return int(value)  # Конвертируем в целое число

        # Если значение - строка, пробуем преобразовать в число
        if isinstance(value, str) and value.strip():
            try:
                return int(float(value.strip()))
            except ValueError:
                return value  # Если не число, оставляем как есть

        return value

    def replace_nan_with_none(self, obj):
        """Рекурсивно заменяет NaN на None в структуре данных"""
        if isinstance(obj, dict):
            return {k: self.replace_nan_with_none(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.replace_nan_with_none(item) for item in obj]
        elif isinstance(obj, float) and pd.isna(obj):
            return None
        elif isinstance(obj, str) and obj.strip() == '':
            return None
        else:
            return obj

    def convert_json_to_python(self):
        """Конвертирует JSON шаблон в Python модуль"""
        json_path = self.source_dir / "template.json"
        if not json_path.exists():
            print(f"❌ JSON файл не найден: {json_path}")
            return False

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            output_file = self.data_dir / "template.py"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('"""\nJSON шаблоны аккордов\n"""\n\n')
                f.write('TEMPLATE_DATA = ')
                f.write(json.dumps(template_data, ensure_ascii=False, indent=2))
                f.write('\n')

            # Статистика шаблонов
            frets_count = len(template_data.get('frets', {}))
            notes_count = len(template_data.get('notes', {}))
            barres_count = len(template_data.get('barres', {}))
            crop_rects_count = len(template_data.get('crop_rects', {}))

            print(f"✅ JSON шаблоны сохранены в: {output_file}")
            print(f"   - Ладов: {frets_count}")
            print(f"   - Нот: {notes_count}")
            print(f"   - Баре: {barres_count}")
            print(f"   - Областей обрезки: {crop_rects_count}")
            return True

        except Exception as e:
            print(f"❌ Ошибка конвертации JSON: {e}")
            return False

    def convert_image_to_python(self):
        """Конвертирует изображение грифа в Python модуль"""
        image_path = self.source_dir / "img.png"
        if not image_path.exists():
            print(f"❌ Изображение не найдено: {image_path}")
            return False

        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()

            image_b64 = base64.b64encode(image_data).decode('utf-8')

            output_file = self.data_dir / "template_guitar.py"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('"""\nИзображение грифа гитары\n"""\n\n')
                f.write('GUITAR_IMAGE_DATA = """')
                f.write(image_b64)
                f.write('"""\n')

            print(f"✅ Изображение сохранено в: {output_file}")
            print(f"   - Размер: {len(image_data) / 1024:.1f} KB")
            return True

        except Exception as e:
            print(f"❌ Ошибка конвертации изображения: {e}")
            return False

    def convert_sounds_to_python(self):
        """Конвертирует звуки аккордов в Python модуль"""
        sounds_dir = self.source_dir / "sounds"
        if not sounds_dir.exists():
            print(f"❌ Папка со звуками не найдена: {sounds_dir}")
            return False

        sounds_data = {}
        total_sounds = 0
        total_size = 0

        try:
            # Рекурсивно ищем все MP3 файлы
            print("🔊 Поиск звуковых файлов...")
            for sound_file in sounds_dir.rglob("*.mp3"):
                chord_name = sound_file.parent.name
                if chord_name not in sounds_data:
                    sounds_data[chord_name] = {}

                with open(sound_file, 'rb') as f:
                    sound_bytes = f.read()

                sound_b64 = base64.b64encode(sound_bytes).decode('utf-8')
                sounds_data[chord_name][sound_file.stem] = sound_b64

                total_sounds += 1
                total_size += len(sound_bytes)

            # Создаем Python файл
            output_file = self.data_dir / "chord_sounds.py"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('"""\nЗвуки аккордов\n"""\n\n')
                f.write('SOUNDS_DATA = ')
                f.write(json.dumps(sounds_data, ensure_ascii=False, indent=2))
                f.write('\n')

            print(f"✅ Звуки сохранены в: {output_file}")
            print(f"   - Аккордов со звуками: {len(sounds_data)}")
            print(f"   - Всего звуковых файлов: {total_sounds}")
            print(f"   - Общий размер: {total_size / 1024 / 1024:.1f} MB")
            return True

        except Exception as e:
            print(f"❌ Ошибка конвертации звуков: {e}")
            return False

    def convert_all(self):
        """Запускает полную конвертацию"""
        print("🎸 Конвертация ресурсов в Python модули...")
        print("=" * 50)

        success = True
        success &= self.convert_excel_to_python()
        success &= self.convert_json_to_python()
        success &= self.convert_image_to_python()
        success &= self.convert_sounds_to_python()

        if success:
            print("\n✅ Все ресурсы успешно сконвертированы!")
            print("\n📁 Созданные файлы:")
            print("   - data/chords_config.py (Excel данные)")
            print("   - data/template.py (JSON шаблоны)")
            print("   - data/template_guitar.py (изображение грифа)")
            print("   - data/chord_sounds.py (звуки аккордов)")
        else:
            print("\n⚠️ Некоторые ресурсы не были сконвертированы")

        return success


def main():
    """Основная функция запуска конвертера"""
    converter = ResourceConverter()

    # Проверяем существование папки source
    if not Path("chords_config").exists():
        print("❌ Папка 'source' не найдена!")
        print("💡 Создайте папку 'source' и поместите в неё:")
        print("   - chord_config.xlsx")
        print("   - template.json")
        print("   - img.png")
        print("   - sounds/ (папка со звуками)")
        return

    success = converter.convert_all()

    if success:
        print("\n🎯 Теперь можно запускать приложение!")
    else:
        print("\n❌ Конвертация не удалась. Проверьте файлы в папке source/")


if __name__ == "__main__":
    main()