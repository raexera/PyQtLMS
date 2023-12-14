import os
import configparser
from PyQt5.QtWidgets import (
    QPushButton,
    QLineEdit,
    QDialog,
    QFormLayout,
)


class DbSetupDialog(QDialog):
    def __init__(self, config_path, parent=None):
        super().__init__(parent)

        self.config_path = config_path
        self.setup_layout()
        self.load_config()

    def setup_layout(self):
        self.setWindowTitle("Database Connection Setup")
        layout = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.host_input = QLineEdit()

        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        layout.addRow("Host:", self.host_input)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)

        layout.addRow(save_button)

        self.setLayout(layout)

        self.setStyleSheet(
            """
            * {
                background-color: #2e2e2e;
                color: #ffffff;
                font-size: 14px;
            }

            QDialog {
                border: 1px solid #555555;
            }

            QLineEdit {
                padding: 6px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #424242;
                color: #ffffff;
            }

            QPushButton {
                background-color: #4a90e2;
                color: #ffffff;
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
