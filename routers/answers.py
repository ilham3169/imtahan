from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response # type: ignore
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy.sql.expression import text # type: ignore
from database import sessionLocal
from models import Question, Exam, Answer
from schemas import AnswerResponse, AnswerCreate
import logging
from datetime import datetime
import pytz # type: ignore



TIMEZONE = pytz.timezone("Asia/Baku")

router = APIRouter(
    prefix="/answers",
    tags=["answers"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
logger = logging.getLogger("uvicorn.error")


@router.get("", response_model=List[AnswerResponse], status_code=status.HTTP_200_OK)
async def get_all_answers(db: db_dependency):
    answers = db.query(Answer).all()
    return answers

@router.post("/create", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def create_answer(answer: AnswerCreate, db: db_dependency):
    question = db.query(Question).filter(Question.id == answer.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    db_answer = Answer(
        score=answer.score,
        question_id=answer.question_id,
        content=answer.content 
    )
    
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    
    return db_answer

