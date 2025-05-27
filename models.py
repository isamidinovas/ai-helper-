from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text,DateTime,ForeignKey, func
from database import Base  # база из database.py (покажу позже)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    flashcard_decks = relationship("FlashcardDeck", back_populates="creator")
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

class FlashcardDeck(Base):
    __tablename__ = "flashcard_decks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    subject = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    flashcards = relationship("Flashcard", back_populates="deck") 
    creator = relationship("User", back_populates="flashcard_decks")

   


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    answer = Column(String)
    deck_id = Column(Integer, ForeignKey("flashcard_decks.id"))

    deck = relationship("FlashcardDeck", back_populates="flashcards")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)


