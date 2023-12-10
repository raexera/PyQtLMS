import os
import sys
import configparser
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QHeaderView,
    QDialog,
    QFormLayout,
)
from PyQt5.QtCore import Qt


class DatabaseHandler:
    def __init__(self, host, user, password, database):
        try:
            self.connection = mysql.connector.connect(
                host=host, user=user, passwd=password
            )
            if not self.connection.is_connected():
                raise mysql.connector.Error("Unable to connect to database.")

            self.cursor = self.connection.cursor()

            self.cursor.execute(f"SHOW DATABASES LIKE '{database}'")
            if not self.cursor.fetchone():
                self.cursor.execute(f"CREATE DATABASE {database}")

            self.cursor.execute(f"USE {database}")

            self.cursor.execute("SHOW TABLES LIKE 'book'")
            if not self.cursor.fetchone():
                self.cursor.execute(
                    """
                        CREATE TABLE book (
                            ISBN VARCHAR(20) PRIMARY KEY,
                            title TEXT NOT NULL,
                            author VARCHAR(100) NOT NULL,
                            year_published INT NOT NULL,
                            price INT NOT NULL
                        )
                        """
                )
                self.connection.commit()
        except mysql.connector.Error as err:
            self.handle_db_error(err)
            raise

    def handle_db_error(self, err):
        print(f"Database Error: {err}")

    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.handle_db_error(err)

    def fetch_data(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            self.handle_db_error(err)
            return []


class DbSetupDialog(QDialog):
    def __init__(self, config_path):
        super().__init__()

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


class BookManagementSystem(QMainWindow):
    def __init__(self, db_handler):
        super().__init__()
        self.db_handler = db_handler
        self.setup_base_window()

    def setup_base_window(self):
        self.setWindowTitle("Library Management System")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.banner_label = QLabel("Library Management System")
        self.banner_label.setAlignment(Qt.AlignCenter)
        self.banner_label.setStyleSheet("font-size: 32px; color: #4a90e2;")

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.setup_database)
        self.main_layout.addWidget(self.banner_label)
        self.main_layout.addWidget(self.start_button)

        self.statusBar().showMessage("Created with ❤️ by @rxyhn")

        self.setStyleSheet(
            """
            *{
                background-color: #2e2e2e;
                color: #ffffff;
                font-size: 14px;
            }
            QMainWindow {
                background-color: #2e2e2e;
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
            QLineEdit {
                padding: 6px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #424242;
                color: #ffffff;
            }
            QTableWidget {
                border: none;
            }
            QLabel {
                color: #ffffff;
            }
        """
        )

    def clear_layout(self):
        for i in reversed(range(self.main_layout.count())):
            if widget := self.main_layout.itemAt(i).widget():
                widget.setParent(None)

    def create_button(self, text, clicked_handler):
        button = QPushButton(text)
        button.setMinimumSize(40, 20)
        button.setStyleSheet("padding: 4px 8px; color: #000;")
        button.clicked.connect(clicked_handler)
        return button

    def create_widget(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def create_line_edit(self, text, placeholder=True):
        line_edit = QLineEdit()
        if placeholder:
            line_edit.setPlaceholderText(text)
        else:
            line_edit.setText(text)

        return line_edit

    def create_scroll_area(self, widget):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_area.setWidget(widget)
        return scroll_area

    def show_main_page(self):
        self.clear_layout()

        if books := self.load_all_books():
            table = QTableWidget(len(books), 6)
            table.setHorizontalHeaderLabels(
                ["ISBN", "Title", "Author", "Year", "Price", "Actions"]
            )

            for row, book in enumerate(books):
                for col, value in enumerate(book):
                    item = QTableWidgetItem(str(value))
                    table.setItem(row, col, item)

                edit_button = self.create_button(
                    "Edit", lambda _, b=book: self.show_edit_book_page(b)
                )
                delete_button = self.create_button(
                    "Delete", lambda _, b=book: self.confirm_delete_book(b)
                )

                layout = QHBoxLayout()
                layout.addWidget(edit_button)
                layout.addWidget(delete_button)

                widget = self.create_widget(layout)

                table.setCellWidget(row, 5, widget)

            scroll_area = self.create_scroll_area(table)

            self.main_layout.addWidget(scroll_area, 1)

            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.horizontalHeader().setStretchLastSection(True)

            vertical_header = table.verticalHeader()
            vertical_header.setDefaultSectionSize(50)

        else:
            message_label = QLabel(
                "No books found. Click the button below to add a new book."
            )
            message_label.setAlignment(Qt.AlignCenter)
            message_label.setStyleSheet("font-size: 24px; color: #4a90e2;")
            self.main_layout.addWidget(message_label)
        add_book_button = QPushButton("Add New Book")
        add_book_button.clicked.connect(self.show_add_book_page)
        self.main_layout.addWidget(add_book_button)

    def show_add_book_page(self):
        self.clear_layout()

        add_book_label = QLabel("Add New Book")
        add_book_label.setStyleSheet("font-size: 24px; color: #4a90e2;")
        add_book_label.setAlignment(Qt.AlignCenter)

        self.isbn_input = self.create_line_edit("ISBN")
        self.title_input = self.create_line_edit("Title")
        self.author_input = self.create_line_edit("Author")
        self.year_input = self.create_line_edit("Year Published")
        self.price_input = self.create_line_edit("Price")

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.add_book)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.show_main_page)

        back_submit_layout = QHBoxLayout()
        back_submit_layout.addWidget(back_button)
        back_submit_layout.addWidget(submit_button)

        year_price_layout = QHBoxLayout()
        year_price_layout.addWidget(self.year_input)
        year_price_layout.addWidget(self.price_input)

        layout = QVBoxLayout()
        layout.addWidget(add_book_label)
        layout.addWidget(self.isbn_input)
        layout.addWidget(self.title_input)
        layout.addWidget(self.author_input)
        layout.addLayout(year_price_layout)
        layout.addLayout(back_submit_layout)

        widget = self.create_widget(layout)
        self.main_layout.addWidget(widget)

    def show_edit_book_page(self, book):
        self.clear_layout()

        edit_book_label = QLabel("Edit Book")
        edit_book_label.setStyleSheet("font-size: 24px; color: #4a90e2;")
        edit_book_label.setAlignment(Qt.AlignCenter)

        self.isbn_input = self.create_line_edit(book[0], placeholder=False)
        self.isbn_input.setReadOnly(True)
        self.title_input = self.create_line_edit(book[1], placeholder=False)
        self.author_input = self.create_line_edit(book[2], placeholder=False)
        self.year_input = self.create_line_edit(str(book[3]), placeholder=False)
        self.price_input = self.create_line_edit(str(book[4]), placeholder=False)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(lambda: self.edit_book(book[0]))

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.show_main_page)

        back_submit_layout = QHBoxLayout()
        back_submit_layout.addWidget(back_button)
        back_submit_layout.addWidget(submit_button)

        year_price_layout = QHBoxLayout()
        year_price_layout.addWidget(self.year_input)
        year_price_layout.addWidget(self.price_input)

        layout = QVBoxLayout()
        layout.addWidget(edit_book_label)
        layout.addWidget(self.isbn_input)
        layout.addWidget(self.title_input)
        layout.addWidget(self.author_input)
        layout.addLayout(year_price_layout)
        layout.addLayout(back_submit_layout)

        widget = self.create_widget(layout)
        self.main_layout.addWidget(widget)

    def add_book(self):
        isbn = self.isbn_input.text()
        title = self.title_input.text()
        author = self.author_input.text()
        year = self.year_input.text()
        price = self.price_input.text()

        if not isbn or not title or not author or not year or not price:
            self.show_error_dialog("All fields must be filled.")
            return

        try:
            year = int(year)
            price = int(price)
            if year < 1900 or year > 2024:
                raise ValueError("Year must be between 1900 and 2024.")
            if price <= 0:
                raise ValueError("Price must be greater than 0.")
        except ValueError as e:
            self.show_error_dialog(str(e))
            return

        if self.is_isbn_duplicate(isbn):
            self.show_error_dialog("ISBN already exists.")
            return

        self.insert_book(isbn, title, author, year, price)
        self.show_success_dialog("Book added successfully.")
        self.show_main_page()

    def edit_book(self, isbn):
        title = self.title_input.text()
        author = self.author_input.text()
        year = self.year_input.text()
        price = self.price_input.text()

        current_values = self.load_book_by_isbn(isbn)
        if (
            title == current_values[1]
            and author == current_values[2]
            and year == str(current_values[3])
            and price == str(current_values[4])
        ):
            self.show_info_dialog("No changes made. Book remains the same.")
            self.show_main_page()
            return

        try:
            year = int(year)
            price = int(price)
            if year < 1900 or year > 2024:
                raise ValueError("Year must be between 1900 and 2024.")
            if price <= 0:
                raise ValueError("Price must be greater than 0.")
        except ValueError as e:
            self.show_error_dialog(str(e))
            return

        if not title or not author:
            self.show_error_dialog("Title and Author fields must be filled.")
            return

        self.update_book(isbn, title, author, year, price)

        self.show_success_dialog("Book updated successfully.")

        self.show_main_page()

    def confirm_delete_book(self, book):
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            f"Do you want to delete the book with ISBN: {book[0]}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if confirmation == QMessageBox.Yes:
            self.delete_book(book[0])

            self.show_success_dialog("Book deleted successfully.")

            self.show_main_page()

    def load_all_books(self):
        query = "SELECT * FROM book"
        return self.db_handler.fetch_data(query)

    def is_isbn_duplicate(self, isbn):
        query = "SELECT COUNT(*) FROM book WHERE ISBN = %s"
        count = self.db_handler.fetch_data(query, (isbn,))[0][0]
        return count > 0

    def insert_book(self, isbn, title, author, year, price):
        query = "INSERT INTO book (ISBN, title, author, year_published, price) VALUES (%s, %s, %s, %s, %s)"
        self.db_handler.execute_query(query, (isbn, title, author, year, price))

    def update_book(self, isbn, title, author, year, price):
        query = "UPDATE book SET title = %s, author = %s, year_published = %s, price = %s WHERE ISBN = %s"
        self.db_handler.execute_query(query, (title, author, year, price, isbn))

    def delete_book(self, isbn):
        query = "DELETE FROM book WHERE ISBN = %s"
        self.db_handler.execute_query(query, (isbn,))

    def load_book_by_isbn(self, isbn):
        query = "SELECT * FROM book WHERE ISBN = %s"
        return self.db_handler.fetch_data(query, (isbn,))[0]

    def show_success_dialog(self, message):
        QMessageBox.information(self, "Success", message, QMessageBox.Ok)

    def show_error_dialog(self, message):
        QMessageBox.critical(self, "Error", message, QMessageBox.Ok)

    def show_info_dialog(self, message):
        QMessageBox.information(self, "Information", message, QMessageBox.Ok)

    def setup_database(self):
        while True:
            config_path = self.get_config_path()
            db_setup_dialog = DbSetupDialog(config_path)

            if db_setup_dialog.exec_() != QDialog.Accepted:
                break
            username = db_setup_dialog.username_input.text()
            password = db_setup_dialog.password_input.text()
            host = db_setup_dialog.host_input.text()

            try:
                self.db_handler = DatabaseHandler(host, username, password, "PyQtLMS")
                self.show_main_page()
                break

            except mysql.connector.Error as err:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Unable to connect to the database. Please check your credentials and try again.",
                    QMessageBox.Ok,
                )

                retry = QMessageBox.question(
                    self,
                    "Error",
                    "Do you want to try again?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if retry == QMessageBox.No:
                    break

            except Exception as e:
                print(f"Unexpected Error: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    "An unexpected error occurred.",
                    QMessageBox.Ok,
                )
                break

    def handle_db_error(self, err):
        print(f"Database Error: {err}")
        QMessageBox.critical(self, "Error", f"Database Error: {err}", QMessageBox.Ok)

    def get_config_path(self):
        if sys.platform == "win32":
            return os.path.join(os.getenv("APPDATA"), "PyQtLMS", "db_connection.ini")
        elif sys.platform == "linux":
            return os.path.join(
                os.getenv("HOME"), ".config", "PyQtLMS", "db_connection.ini"
            )


def main():
    app = QApplication(sys.argv)
    db_handler = DatabaseHandler("localhost", "root", "root", "PyQtLMS")
    main_window = BookManagementSystem(db_handler)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
