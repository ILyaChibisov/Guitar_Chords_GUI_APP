#!/usr/bin/env python3
"""
Автономный запускатель конвертера аккордов
"""

import os
import sys
from pathlib import Path


def main():
    """Основная функция запуска"""
    print("🎸 Запуск оптимизированного конвертера аккордов")
    print("=" * 50)

    # Добавляем текущую директорию в путь
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    try:
        # Прямой импорт модуля
        from tools.chord_converter import main as converter_main

        # Запускаем конвертер
        converter_main()

    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Убедитесь, что файл tools/chord_converter.py существует")
        print("2. Установите Pillow: pip install Pillow")
        print("3. Проверьте структуру проекта")

    except Exception as e:
        print(f"❌ Ошибка запуска конвертера: {e}")
        import traceback
        traceback.print_exc()

    input("\n🎯 Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()