from pydantic import BaseModel
from typing import Optional


class BookBase(BaseModel):
    title: str
    author: str
    image_url: str
    description: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    rating: Optional[float] = None


class BookCreate(BookBase):
    pass


class BookRead(BookBase):
    id: int

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    book_id: int
    user_name: str
    comment: str


class CommentRead(CommentCreate):
    id: int

    class Config:
        from_attributes = True
