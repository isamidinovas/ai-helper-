from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
import crud
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
from datetime import timedelta
from models import User
# main.py
from fastapi import FastAPI
from crud import get_current_user
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
