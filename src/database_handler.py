import mysql.connector


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

    def load_all_books(self):
        query = "SELECT * FROM book"
        return self.fetch_data(query)

    def is_isbn_duplicate(self, isbn):
        query = "SELECT COUNT(*) FROM book WHERE ISBN = %s"
        count = self.fetch_data(query, (isbn,))[0][0]
        return count > 0

    def insert_book(self, isbn, title, author, year, price):
        query = "INSERT INTO book (ISBN, title, author, year_published, price) VALUES (%s, %s, %s, %s, %s)"
        self.execute_query(query, (isbn, title, author, year, price))

    def update_book(self, isbn, title, author, year, price):
        query = "UPDATE book SET title = %s, author = %s, year_published = %s, price = %s WHERE ISBN = %s"
        self.execute_query(query, (title, author, year, price, isbn))

    def delete_book(self, isbn):
        query = "DELETE FROM book WHERE ISBN = %s"
        self.execute_query(query, (isbn,))

    def load_book_by_isbn(self, isbn):
        query = "SELECT * FROM book WHERE ISBN = %s"
        return self.fetch_data(query, (isbn,))[0]
