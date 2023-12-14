from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QHeaderView,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, QSize
from .components import DbConnectionHandler


class BookManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_connection_handler = DbConnectionHandler()
        self.setup_base_window()

    def setup_base_window(self):
        self.setWindowTitle("Library Management System")
        self.setMinimumSize(QSize(900, 600))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.banner_label = QLabel("Library Management System")
        self.banner_label.setAlignment(Qt.AlignCenter)
        self.banner_label.setStyleSheet("font-size: 32pt; color: #4a90e2;")

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.setup_database_connection)
        self.main_layout.addWidget(self.banner_label)
        self.main_layout.addWidget(self.start_button)

        self.setStyleSheet(
            """
            *{
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
            QTableWidget,
            QTableWidget::item {
                border: 1px solid #555555;
            }
            QHeaderView::section {
                background-color: #2e2e2e;
                color: #ffffff;
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

        status_message = QLabel(
            'Created with <span style="color: #4a90e2;">❤️</span> by <span style="color: #4a90e2;">@rxyhn</span>'
        )
        status_message.setAlignment(Qt.AlignCenter)
        status_message.setStyleSheet(
            "color: #ffffff; font-size: 14pt; padding: 8px; border-top: 1px solid #555555;"
        )
        self.statusBar().addWidget(status_message, 1)

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

    def resizeEvent(self, event):
        self.adjustFontSizes()
        super().resizeEvent(event)

    def adjustFontSizes(self):
        base_font_size = max(8, self.width() // 100)
        font = QApplication.font()
        font.setPointSize(base_font_size)
        QApplication.setFont(font)

    def show_main_page(self):
        self.clear_layout()

        if books := self.db_handler.load_all_books():
            table = QTableWidget(len(books), 6)
            table.setHorizontalHeaderLabels(
                ["ISBN", "Title", "Author", "Year", "Price", "Actions"]
            )

            for row, book in enumerate(books):
                table.setItem(row, 0, QTableWidgetItem(book.ISBN))
                table.setItem(row, 1, QTableWidgetItem(book.title))
                table.setItem(row, 2, QTableWidgetItem(book.author))
                table.setItem(row, 3, QTableWidgetItem(str(book.year_published)))
                table.setItem(row, 4, QTableWidgetItem(str(book.price)))

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
            message_label.setStyleSheet("font-size: 24pt; color: #4a90e2;")
            self.main_layout.addWidget(message_label)
        add_book_button = QPushButton("Add New Book")
        add_book_button.clicked.connect(self.show_add_book_page)
        self.main_layout.addWidget(add_book_button)

    def show_add_book_page(self):
        self.clear_layout()

        add_book_label = QLabel("Add New Book")
        add_book_label.setStyleSheet("font-size: 24pt; color: #4a90e2;")
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
        edit_book_label.setStyleSheet("font-size: 24pt; color: #4a90e2;")
        edit_book_label.setAlignment(Qt.AlignCenter)

        self.isbn_input = self.create_line_edit(book.ISBN, placeholder=False)
        self.isbn_input.setReadOnly(True)
        self.title_input = self.create_line_edit(book.title, placeholder=False)
        self.author_input = self.create_line_edit(book.author, placeholder=False)
        self.year_input = self.create_line_edit(
            str(book.year_published), placeholder=False
        )
        self.price_input = self.create_line_edit(str(book.price), placeholder=False)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(lambda: self.edit_book(book.ISBN))

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

        if self.db_handler.is_isbn_duplicate(isbn):
            self.show_error_dialog("ISBN already exists.")
            return

        self.db_handler.insert_book(isbn, title, author, year, price)
        self.show_success_dialog("Book added successfully.")
        self.show_main_page()

    def edit_book(self, isbn):
        title = self.title_input.text()
        author = self.author_input.text()
        year = self.year_input.text()
        price = self.price_input.text()

        if current_book := self.db_handler.load_book_by_isbn(isbn):
            if (
                title == current_book.title
                and author == current_book.author
                and year == str(current_book.year_published)
                and price == str(current_book.price)
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

            self.db_handler.update_book(isbn, title, author, year, price)
            self.show_success_dialog("Book updated successfully.")
            self.show_main_page()

    def confirm_delete_book(self, book):
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            f"Do you want to delete the book with ISBN: {book.ISBN}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if confirmation == QMessageBox.Yes:
            self.db_handler.delete_book(book.ISBN)

            self.show_success_dialog("Book deleted successfully.")

            self.show_main_page()

    def show_success_dialog(self, message):
        QMessageBox.information(self, "Success", message, QMessageBox.Ok)

    def show_error_dialog(self, message):
        QMessageBox.critical(self, "Error", message, QMessageBox.Ok)

    def show_info_dialog(self, message):
        QMessageBox.information(self, "Information", message, QMessageBox.Ok)

    def setup_database_connection(self):
        if self.db_connection_handler.setup_database_connection(self):
            self.db_handler = self.db_connection_handler.db_handler
            self.show_main_page()
        else:
            self.close()
