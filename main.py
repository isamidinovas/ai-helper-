from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
import crud
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
from datetime import timedelta
from models import Category,  User
from sqlalchemy.orm import joinedload

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




# @app.post("/decks/", response_model=schemas.FlashcardDeck, status_code=201)
# async def create_deck(deck: schemas.FlashcardDeckCreate, db: Session = Depends(get_db)):
    
#     db_deck = models.FlashcardDeck(**deck.model_dump(exclude={"flashcards"}))
#     db.add(db_deck)
#     db.commit()
#     db.refresh(db_deck)
#     for flashcard_data in deck.flashcards:
#         db_flashcard = models.Flashcard(deck_id=db_deck.id, **flashcard_data.model_dump())
#         db.add(db_flashcard)
#     db.commit()
#     db.refresh(db_deck)
#     return db_deck
@app.post("/decks/", response_model=schemas.FlashcardDeck, status_code=201)
async def create_deck(
        deck: schemas.FlashcardDeckCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)  # Важно!
    ):
        db_deck = models.FlashcardDeck(
            **deck.model_dump(exclude={"flashcards"}),
            user_id=current_user.id  # Вот это добавь!
        )
        db.add(db_deck)
        db.commit()
        db.refresh(db_deck)

        for flashcard_data in deck.flashcards:
            db_flashcard = models.Flashcard(deck_id=db_deck.id, **flashcard_data.model_dump())
            db.add(db_flashcard)

        db.commit()
        db.refresh(db_deck)
        return db_deck




@app.get("/decks/", response_model=List[schemas.FlashcardDeck])
async def read_decks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    decks = db.query(models.FlashcardDeck)\
              .options(joinedload(models.FlashcardDeck.creator))\
              .offset(skip).limit(limit).all()
    return decks
