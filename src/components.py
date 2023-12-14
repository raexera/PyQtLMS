import os
import sys
import configparser
from PyQt5.QtWidgets import (
    QPushButton,
    QLineEdit,
    QDialog,
    QFormLayout,
    QMessageBox,
)
from PyQt5.QtCore import QSize
from .database import DatabaseHandler


class DbConnectionHandler:
    def __init__(self):
        self.db_handler = None

    def setup_database_connection(self, main_window):
        while True:
            config_path = self.get_config_path()
            db_setup_dialog = DbSetupDialog(config_path, main_window)

            if db_setup_dialog.exec_() != QDialog.Accepted:
                break

            username = db_setup_dialog.username_input.text()
            password = db_setup_dialog.password_input.text()
            host = db_setup_dialog.host_input.text()

            try:
                self.db_handler = DatabaseHandler(host, username, password, "PyQtLMS")
                return True
            except Exception as e:
                QMessageBox.critical(
                    main_window,
                    "Error",
                    f"Unable to connect to the database: {e}",
                    QMessageBox.Ok,
                )

                retry = QMessageBox.question(
                    main_window,
                    "Retry Connection",
                    "Do you want to try again?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if retry == QMessageBox.No:
                    return False

    def get_config_path(self):
        if sys.platform == "win32":
            return os.path.join(os.getenv("APPDATA"), "PyQtLMS", "db_connection.ini")
        elif sys.platform == "linux":
            return os.path.join(
                os.getenv("HOME"), ".config", "PyQtLMS", "db_connection.ini"
            )


class DbSetupDialog(QDialog):
    def __init__(self, config_path, parent=None):
        super().__init__(parent)

        self.config_path = config_path
        self.setup_layout()
        self.load_config()

    def setup_layout(self):
        self.setWindowTitle("Database Connection Setup")
        self.setMinimumSize(QSize(400, 200))
        layout = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.host_input = QLineEdit()

        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        layout.addRow("Host:", self.host_input)

        save_button = QPushButton("OK")
        save_button.clicked.connect(self.save_config)

        layout.addRow(save_button)

        self.setLayout(layout)

        self.setStyleSheet(
            """
            * {
                background-color: #2e2e2e;
                color: #ffffff;
                font-size: 16pt;
            }
            QDialog {
                border: 1px solid #555555;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #424242;
            }
            QPushButton {
                background-color: #4a90e2;
                color: #2e2e2e;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #357ae8;
            }
            """
        )

    def load_config(self):
        config = configparser.ConfigParser()

        if os.path.exists(self.config_path):
            config.read(self.config_path)
            self.username_input.setText(config.get("Database", "Username"))
            self.password_input.setText(config.get("Database", "Password"))
            self.host_input.setText(config.get("Database", "Host"))

    def save_config(self):
        config = configparser.ConfigParser()
        config.add_section("Database")
        config.set("Database", "Username", self.username_input.text())
        config.set("Database", "Password", self.password_input.text())
        config.set("Database", "Host", self.host_input.text())

        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        with open(self.config_path, "w") as config_file:
            config.write(config_file)

        self.accept()
