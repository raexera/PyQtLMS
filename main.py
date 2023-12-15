import sys
from PyQt5.QtWidgets import QApplication
from src.app import BookManagementSystem

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = BookManagementSystem()
    main_window.show()
    sys.exit(app.exec_())
