from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from src.models import engine, Base, Book, Comment
from sqlalchemy.orm import sessionmaker
from src.schemas import BookCreate, BookRead, CommentCreate, CommentRead


app = FastAPI(title="Books API")

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_model=dict)
def root():
    return {"message": "Books API працює!"}


@app.get("/books", response_model=List[BookRead])
def get_books(db: Session = Depends(get_db)):
    return db.query(Book).all()


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


@app.get("/comments", response_model=List[CommentRead])
def get_all_comments(db: Session = Depends(get_db)):
    return db.query(Comment).all()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
