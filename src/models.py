from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from src.config import settings

Base = declarative_base()
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    author = Column(String(50))
    image_url = Column(String(300))
    description = Column(String(200), nullable=True)
    genre = Column(String(20), nullable=True)
    year = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)

    comments = relationship("Comment", back_populates="book", cascade="all, delete")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    user_name = Column(String(30))
    comment = Column(Text)

    book = relationship("Book", back_populates="comments")

# Створюємо таблиці
Base.metadata.create_all(bind=engine)
