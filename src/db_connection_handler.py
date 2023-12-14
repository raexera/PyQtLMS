import os
import sys
from PyQt5.QtWidgets import (
    QMessageBox,
    QDialog,
)
from .database_handler import DatabaseHandler
from .db_setup_dialog import DbSetupDialog


class DbConnectionHandler:
    def __init__(self):
        self.db_handler = None

    def setup_database_connection(self, main_window):
        while True:
            # Assume you have a dialog to get these details
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
