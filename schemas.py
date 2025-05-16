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

class FlashcardDeckBase(BaseModel):
    title: str
    description: Optional[str] = None
    subject: str

class FlashcardDeckCreate(FlashcardDeckBase):
    flashcards: List[FlashcardCreate] = []

class FlashcardDeck(FlashcardDeckBase):
    id: int
    flashcards: List[Flashcard] = []
    user_id: Optional[int] = None
    creator:  Optional[UserOut] = None
    class Config:
        orm_mode = True