from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from typing import List

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    

    class Config:
       from_attributes = True
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class CategoryBase(BaseModel):
    name: str

class CategoryOut(CategoryBase):
    id: int

    class Config:
        orm_mode = True

class FlashcardBase(BaseModel):
    question: str
    answer: str

class FlashcardCreate(FlashcardBase):
    pass

class Flashcard(FlashcardBase):
    id: int
    class Config:
        orm_mode = True

class DeckBase(BaseModel):
    title: str
    description: Optional[str] = None

class DeckCreate(DeckBase):
    flashcards: List[FlashcardCreate] = []

class Deck(BaseModel):
    id: int
    title: str
    description: Optional[str]
    flashcards: List[Flashcard] = []

    class Config:
        orm_mode = True
