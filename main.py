# main.py
import sys
import os
import traceback

from core.app import GuitarApp


def main():
    # Добавляем путь к проекту в PYTHONPATH
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    try:
        # Создаем и запускаем приложение
        app = GuitarApp()
        app.show()

        print("🎸 GuitarChords Pro успешно запущен!")

        return app.exec_()

    except Exception as e:
        print(f"❌ Критическая ошибка при запуске: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    main()