import mysql.connector


class DatabaseHandler:
    def __init__(self, host, user, password, database):
        try:
            self.connection = mysql.connector.connect(
                host=host, user=user, passwd=password
            )
            self.cursor = self.connection.cursor()

            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            self.cursor.execute(f"USE {database}")
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS book (
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
            self.show_error_dialog(f"Database Error: {err}")

    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.show_error_dialog(f"Database Error: {err}")

    def fetch_data(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            self.show_error_dialog(f"Database Error: {err}")
            return []
