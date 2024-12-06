import os
from io import BytesIO
import openai
from fastapi import FastAPI, UploadFile, File, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv
from init_db import SessionLocal, Question

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class QuestionResponse(BaseModel):
    id: int
    text: str
    correct_example: str

    class Config:
        from_attributes = True

@app.get("/questions", response_model=List[QuestionResponse])
def get_questions(db: Session = Depends(get_db)):
    return db.query(Question).all()

@app.post("/transcribe_and_evaluate")
async def transcribe_and_evaluate(
    file: UploadFile = File(...),
    question_id: int = Form(...),
    db: Session = Depends(get_db)
):
    audio_content = await file.read()
    audio_file = BytesIO(audio_content)
    audio_file.name = file.filename

    try:
        transcription_response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            language="de"
        )
        transcription = transcription_response["text"]
    except Exception as e:
        return {"error": "Failed to transcribe audio", "details": str(e)}

    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        return {"error": f"Question with ID {question_id} not found in the database"}

    prompt = f"""
    Pytanie: "{question.text}"
    Transkrypcja odpowiedzi użytkownika: "{transcription}"
    Poprawny przykład odpowiedzi: "{question.correct_example}"

    Oceń odpowiedź użytkownika w skali 1-4, gdzie:
    1 - Używa pojedynczych słów, komunikacja lakoniczna.
    2 - Próbuje układać zdania, ale niepoprawne gramatycznie.
    3 - Poprawne w co najmniej 75% gramatycznie, rozwija komunikację.
    4 - Poprawna gramatycznie i rozwinięta odpowiedź.

    Podaj uzasadnienie swojej oceny i wynik (np. "Ocena: 3. Użytkownik poprawnie ułożył 75% zdań, ale brakuje specjalistycznych terminów").
    """
    try:
        evaluation_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem języka niemieckiego oceniającym odpowiedzi."},
                {"role": "user", "content": prompt}
            ]
        )
        evaluation = evaluation_response["choices"][0]["message"]["content"]
    except Exception as e:
        return {"error": "Failed to evaluate response", "details": str(e)}

    return {"transcription": transcription, "evaluation": evaluation}