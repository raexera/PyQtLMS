import sys
from PyQt5.QtWidgets import QApplication
from src.book_management_system import BookManagementSystem

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = BookManagementSystem()
    main_window.show()
    sys.exit(app.exec_())
