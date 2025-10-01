import sys
import os
from PyQt5.QtWidgets import QApplication
from core.app import GuitarApp


def main():
    # Добавляем путь к проекту в PYTHONPATH
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Создаем и запускаем приложение
    window = GuitarApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()