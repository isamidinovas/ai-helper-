from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
import crud
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
from datetime import timedelta
from models import Category, Flashcard, User
# main.py
from fastapi import FastAPI
from crud import get_current_user, update_flashcard
models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)

origins = [
    "http://localhost:3000",  # React dev сервер
    # "https://yourdomain.com",  # если есть прод
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # Разрешённые origin'ы
    allow_credentials=True,
    allow_methods=["*"],                # Разрешить все методы (GET, POST и т.д.)
    allow_headers=["*"],                # Разрешить все заголовки
)
# Функция для подключения к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
# Роут регистрации
@app.post("/auth/register", response_model=schemas.UserOut,   status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    return crud.create_user(db=db, user=user)

@app.post("/auth/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.login_user(db, user.email, user.password)
    access_token_expires = timedelta(minutes=30)
    access_token = crud.create_access_token(data={"sub": db_user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
@app.post("/logout")
def logout():
    return {"message": "Successfully logged out. Please delete your token on the client side."}


@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/categories/", response_model=List[schemas.CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories

@app.post("/flashcards/", response_model=schemas.Deck)
def create_deck(deck: schemas.DeckCreate, db: Session = Depends(get_db)):
    # Вытаскиваем flashcards отдельно
    flashcards_data = deck.flashcards
    db_deck = models.Deck(title=deck.title, description=deck.description)
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)

    # Добавляем flashcards вручную
    for card_data in flashcards_data:
        db_card = models.Flashcard(
            question=card_data.question,
            answer=card_data.answer,
            deck_id=db_deck.id
        )
        db.add(db_card)

    db.commit()
    db.refresh(db_deck)
    return db_deck

@app.post("/flashcards/{deck_id}/deck", response_model=schemas.Flashcard)
def create_card(deck_id: int, flashcard: schemas.FlashcardCreate, db: Session = Depends(get_db)):
    db_card = models.Flashcard(**flashcard.dict(), deck_id=deck_id)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card
@app.get("/flashcards/", response_model=List[schemas.Deck])
def get_all_decks(db: Session = Depends(get_db)):
    return db.query(models.Deck).all()
@app.get("/flashcards/{deck_id}", response_model=schemas.Deck)
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck


@app.put("/flashcards/edit/{card_id}", response_model=schemas.Flashcard)
def update_flashcard_route(card_id: int, flashcard: schemas.FlashcardCreate, db: Session = Depends(get_db)):
    updated = update_flashcard(db, card_id, flashcard)
    if not updated:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return updated