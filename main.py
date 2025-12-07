from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session

# --- DATABASE SETUP ---
DATABASE_URL = "sqlite:///./books.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# --- MODELS ---
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    author = Column(String(50))
    image_url = Column(String(300))
    description = Column(String(300), nullable=True)
    genre = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)

    comments = relationship("Comment", back_populates="book")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    user_name = Column(String(30))
    comment = Column(Text)

    book = relationship("Book", back_populates="comments")

Base.metadata.create_all(bind=engine)

# --- SCHEMAS ---
class BookBase(BaseModel):
    title: str
    author: str
    image_url: str
    description: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    rating: Optional[float] = None

class BookRead(BookBase):
    id: int
    class Config:
        orm_mode = True

class BookCreate(BookBase):
    pass

class CommentCreate(BaseModel):
    book_id: int
    user_name: str
    comment: str

class CommentRead(CommentCreate):
    id: int
    class Config:
        orm_mode = True

# --- FASTAPI APP ---
app = FastAPI(title="Books API")

# --- DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- INITIAL BOOKS ---
initial_books = [
    {"title": "Гаррі Поттер і філософський камінь", "author": "Дж. К. Ролінґ", "image_url": "https://example.com/hp1.jpg", "description": "Перша книга про Гаррі Поттера", "genre": "Фантастика", "year": 1997, "rating": 4.8},
    {"title": "Гаррі Поттер і таємна кімната", "author": "Дж. К. Ролінґ", "image_url": "https://example.com/hp2.jpg", "description": "Друга книга про Гаррі Поттера", "genre": "Фантастика", "year": 1998, "rating": 4.7},
    {"title": "Гаррі Поттер і в'язень Азкабану", "author": "Дж. К. Ролінґ", "image_url": "https://example.com/hp3.jpg", "description": "Третя книга про Гаррі Поттера", "genre": "Фантастика", "year": 1999, "rating": 4.8},
    {"title": "Гаррі Поттер і кубок вогню", "author": "Дж. К. Ролінґ", "image_url": "https://example.com/hp4.jpg", "description": "Четверта книга про Гаррі Поттера", "genre": "Фантастика", "year": 2000, "rating": 4.9},
    {"title": "Гаррі Поттер і Орден Фенікса", "author": "Дж. К. Ролінґ", "image_url": "https://example.com/hp5.jpg", "description": "П’ята книга про Гаррі Поттера", "genre": "Фантастика", "year": 2003, "rating": 4.7},
    {"title": "Гаррі Поттер і Напівкровний Принц", "author": "Дж. К. Ролінґ", "image_url": "https://example.com/hp6.jpg", "description": "Шоста книга про Гаррі Поттера", "genre": "Фантастика", "year": 2005, "rating": 4.8},
    {"title": "Гаррі Поттер і Смертельні Реліквії", "author": "Дж. К. Ролінґ", "image_url": "https://example.com/hp7.jpg", "description": "Сьома книга про Гаррі Поттера", "genre": "Фантастика", "year": 2007, "rating": 4.9},
    {"title": "Маленький принц", "author": "Антуан де Сент-Екзюпері", "image_url": "https://example.com/littleprince.jpg", "description": "Класична казка для дорослих і дітей", "genre": "Казка", "year": 1943, "rating": 4.7},
    {"title": "Тіні забутих предків", "author": "Михайло Коцюбинський", "image_url": "https://example.com/shadow.jpg", "description": "Українська класика", "genre": "Роман", "year": 1911, "rating": 4.5},
    {"title": "Пригоди Тома Сойєра", "author": "Марк Твен", "image_url": "https://example.com/tomsawyer.jpg", "description": "Весела класика для дітей", "genre": "Пригоди", "year": 1876, "rating": 4.6}
]

# --- STARTUP EVENT: populate DB ---
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    for book in initial_books:
        exists = db.query(Book).filter(Book.title == book["title"]).first()
        if not exists:
            db_book = Book(**book)
            db.add(db_book)
    db.commit()
    db.close()

# --- ROUTES ---
@app.get("/", response_model=List[BookRead])
def get_all_books(db: Session = Depends(get_db)):
    """Повертає всі книги без фільтрації"""
    return db.query(Book).all()

@app.get("/books", response_model=List[BookRead])
def get_books(title: Optional[str] = None, author: Optional[str] = None,
              genre: Optional[str] = None, sort_by: Optional[str] = Query(None, pattern="^(year|rating)$"),
              db: Session = Depends(get_db)):
    """Повертає книги з фільтром та сортуванням"""
    query = db.query(Book)
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if genre:
        query = query.filter(Book.genre.ilike(f"%{genre}%"))
    if sort_by:
        query = query.order_by(getattr(Book, sort_by).desc())
    return query.all()

@app.get("/books/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    return book

@app.post("/books", response_model=BookRead)
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.put("/books/{book_id}", response_model=BookRead)
def update_book(book_id: int, updated: BookCreate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    for key, value in updated.dict().items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    db.delete(book)
    db.commit()
    return {"message": "Книгу видалено"}

@app.post("/comments", response_model=CommentRead)
def add_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == comment.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не знайдена")
    db_comment = Comment(**comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/comments/{book_id}", response_model=List[CommentRead])
def get_comments(book_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.book_id == book_id).all()

# --- RUN SERVER ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
