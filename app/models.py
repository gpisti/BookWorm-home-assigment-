from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum

class ReadingStatus(str, enum.Enum):
    PLAN_TO_READ = "plan_to_read"
    READING = "reading"
    COMPLETED = "completed"
    DROPPED = "dropped"

class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)

    shelf_items = relationship("ShelfItem", back_populates="user")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    isbn = Column(String, unique=True, nullable=True)
    description = Column(Text, nullable=True)
    cover_url = Column(String, nullable=True)

    shelf_items = relationship("ShelfItem", back_populates="book")

class ShelfItem(Base):
    __tablename__ = "shelf_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    
    status = Column(Enum(ReadingStatus), default=ReadingStatus.PLAN_TO_READ)
    rating = Column(Integer, nullable=True)
    review = Column(Text, nullable=True)

    user = relationship("User", back_populates="shelf_items")
    book = relationship("Book", back_populates="shelf_items")