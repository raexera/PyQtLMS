from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Book(Base):
    __tablename__ = "book"
    ISBN = Column(String(20), primary_key=True)
    title = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    year_published = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
