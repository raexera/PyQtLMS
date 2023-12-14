from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()


class Book(Base):
    __tablename__ = "book"
    ISBN = Column(String(20), primary_key=True)
    title = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    year_published = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)


class DatabaseHandler:
    def __init__(self, host, user, password, database):
        try:
            self.engine = create_engine(
                f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
            )
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        except SQLAlchemyError as err:
            print(f"Database Error: {err}")
            raise

    def insert_book(self, isbn, title, author, year, price):
        new_book = Book(
            ISBN=isbn, title=title, author=author, year_published=year, price=price
        )
        self.session.add(new_book)
        self.session.commit()

    def load_all_books(self):
        return self.session.query(Book).all()

    def load_book_by_isbn(self, isbn):
        return self.session.query(Book).filter(Book.ISBN == isbn).first()

    def update_book(self, isbn, title, author, year, price):
        book = self.session.query(Book).filter(Book.ISBN == isbn).first()
        if book:
            book.title = title
            book.author = author
            book.year_published = year
            book.price = price
            self.session.commit()

    def delete_book(self, isbn):
        book = self.session.query(Book).filter(Book.ISBN == isbn).first()
        if book:
            self.session.delete(book)
            self.session.commit()

    def is_isbn_duplicate(self, isbn):
        return self.session.query(Book).filter(Book.ISBN == isbn).count() > 0
