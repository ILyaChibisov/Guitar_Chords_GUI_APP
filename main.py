import sys
import os
from core.app import GuitarApp


def main():
    # Добавляем путь к проекту в PYTHONPATH
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    # Создаем и запускаем приложение
    app = GuitarApp()
    app.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()