from sqlalchemy.orm import Session
from database import SessionLocal
from models import Flashcard, User
import models
from schemas import  FlashcardCreate, UserCreate
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from fastapi import HTTPException, Depends
import os
from dotenv import load_dotenv
from sqlalchemy.orm import joinedload
from models import Subject
from schemas import SubjectCreate
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv() 

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

REFRESH_TOKEN_EXPIRE_DAYS = 7
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def get_password_hash(password):
    return pwd_context.hash(password)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")

    user = db.query(User).filter(User.email == user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_flashcards(db: Session, deck_id: int):
    # Получаем флешкарты с автором
    flashcards = db.query(models.Flashcard).filter(models.Flashcard.deck_id == deck_id).options(joinedload(models.Flashcard.author)).all()
    return flashcards



def update_flashcard(db: Session, card_id: int, flashcard_data: FlashcardCreate):
    db_card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not db_card:
        return None

    db_card.question = flashcard_data.question
    db_card.answer = flashcard_data.answer
    db.commit()
    db.refresh(db_card)
    return db_card


def get_subjects(db: Session):
    return db.query(Subject).all()

def create_subject(db: Session, subject: SubjectCreate):
    db_subject = Subject(name=subject.name)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject