from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum

class ReadingStatus(str, Enum):
    PLAN_TO_READ = "plan_to_read"
    READING = "reading"
    COMPLETED = "completed"
    DROPPED = "dropped"

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, example="Harry Potter")
    author: str = Field(..., min_length=1, example="J.K. Rowling")
    isbn: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int

    class Config:
        from_attributes = True 

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

class User(UserBase):
    id: int
    role: UserRole

    class Config:
        from_attributes = True

class ShelfItemBase(BaseModel):
    status: ReadingStatus = ReadingStatus.PLAN_TO_READ
    rating: Optional[int] = Field(None, ge=1, le=5)
    review: Optional[str] = None

class ShelfItemCreate(ShelfItemBase):
    book_id: int

class ShelfItemUpdate(BaseModel):
    status: Optional[ReadingStatus] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    review: Optional[str] = None

class ShelfItem(ShelfItemBase):
    id: int
    user_id: int
    book_id: int
    
    book: Optional[Book] = None 

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ISBNSearch(BaseModel):
    isbn: str