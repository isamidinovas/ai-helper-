from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from typing import List

class Token(BaseModel):
    access_token: str
    refresh_token: str # Временно возвращаем refresh_token в теле для удобства дебага
    token_type: str = "bearer"
class TokenData(BaseModel):
    sub: Optional[str] = None # 'sub' будет содержать email пользователя
    token_type: Optional[str] = None # 'access' или 'refresh'
    jti: Optional[str] = None # JWT ID для Refresh Token

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    # flashcard_decks: List[] = []  

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
class FlashcardDeckUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    flashcards: Optional[List[FlashcardCreate]] = None

class SubjectCreate(BaseModel):
    name: str

class SubjectOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True