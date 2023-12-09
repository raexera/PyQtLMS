# main.py
import sys
from PyQt5.QtWidgets import QApplication
from src.database import DatabaseHandler
from src.ui import BookManagementSystem


def main():
    app = QApplication(sys.argv)
    db_handler = DatabaseHandler("localhost", "root", "root", "LMS")
    main_window = BookManagementSystem(db_handler)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
