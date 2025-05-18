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
from pydantic import BaseModel
import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import  os
from dotenv import load_dotenv
import fitz  # PyMuPDF
from docx import Document
from fastapi import FastAPI, File, Form, UploadFile
import google.generativeai as genai
import os
import docx
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
from io import BytesIO
import base64
from fastapi import FastAPI
from crud import get_current_user, update_flashcard
models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)
load_dotenv()

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
# API_KEY = "AIzaSyDP5gAM_SFEgidSaVouogVrdsH8PrZyS9c"
class GeminiRequest(BaseModel):
    text: str
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



@app.post("/create/decks/", response_model=schemas.FlashcardDeck, status_code=201)
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

@app.delete("/decks/{deck_id}", status_code=204)
async def delete_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Deletes a specific flashcard deck by its ID.
    Only the creator of the deck can delete it.
    """
    db_deck = db.query(models.FlashcardDeck).filter(models.FlashcardDeck.id == deck_id).first()
    if not db_deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    if db_deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this deck")

    db.delete(db_deck)
    db.commit()
    return None 


@app.get("/decks/{id}", response_model=schemas.FlashcardDeck)
async def read_deck_by_id(
    id: int,  
    db: Session = Depends(get_db)
):
    deck = (
        db.query(models.FlashcardDeck)
        .options(joinedload(models.FlashcardDeck.creator))
        .filter(models.FlashcardDeck.id == id)
        .first()
    )
    if not deck:
        raise HTTPException(status_code=404, detail=f"No deck found with id: {id}")
    return deck
@app.put("/decks/{deck_id}", response_model=schemas.FlashcardDeck)
async def update_deck(
    deck_id: int,
    deck_update: schemas.FlashcardDeckUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
   
    db_deck = db.query(models.FlashcardDeck).filter(models.FlashcardDeck.id == deck_id).first()
    if not db_deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    if db_deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this deck")

    # Update the deck attributes
    for key, value in deck_update.model_dump(exclude_unset=True).items():
        setattr(db_deck, key, value)

    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    return db_deck
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")
genai.configure(api_key=GOOGLE_API_KEY)

available_models = list(genai.list_models())  

model_name = 'models/gemini-1.5-flash-latest'  
model = genai.GenerativeModel(model_name)

async def generate_gemini_response(prompt, image_parts):
    try:
        if image_parts:
            response = model.generate_content([prompt] + image_parts)
        else:
            response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"
@app.post("/chat")
async def chat_with_gemini(prompt: str = Form(...)):
    """Принимает текстовый запрос и возвращает ответ от Gemini."""
    response = await generate_gemini_response(prompt)
    return {"response": response}




def docx_to_pdf(docx_content: bytes) -> bytes:
    """Преобразует содержимое .docx в .pdf (в памяти)."""

    pdf_buffer = BytesIO()  
    doc = docx.Document(BytesIO(docx_content)) 
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    textobject = c.beginText()
    textobject.setTextOrigin(10, 730) 

    for paragraph in doc.paragraphs:
        textobject.textLine(paragraph.text)

    c.drawText(textobject)
    c.save()
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()
    return pdf_bytes


@app.post("/chat-with-document")
async def chat_with_document(
    file: Optional[UploadFile] = File(None),
    prompt: Optional[str] = Form(None)
):
    """Принимает необязательный файл и необязательный текстовый запрос, возвращает ответ от Gemini."""

    file_contents = None
    if file:
        if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            file_contents = docx_to_pdf(await file.read())  # Преобразуем docx в pdf
            file_name = file.filename.replace(".docx", ".pdf")
            file_content_type = "application/pdf"
        else:
            file_contents = await file.read()
            file_name = file.filename
            file_content_type = file.content_type

    image_parts = []
    if file_contents:
        image_parts = [{"mime_type": file_content_type, "data": file_contents}]

    response = await generate_gemini_response(prompt if prompt else "", image_parts)
    return {"response": response}
