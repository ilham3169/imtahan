from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response # type: ignore
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy.sql.expression import text # type: ignore
from database import sessionLocal
from models import Question, Exam
from schemas import QuestionResponse, QuestionCreate
import logging
from datetime import datetime
import pytz # type: ignore



TIMEZONE = pytz.timezone("Asia/Baku")

router = APIRouter(
    prefix="/questions",
    tags=["questions"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
logger = logging.getLogger("uvicorn.error")


@router.get("", response_model=List[QuestionResponse], status_code=status.HTTP_200_OK)
async def get_all_questions(db: db_dependency):
    questions = db.query(Question).all()
    return questions

@router.post("/create", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(question: QuestionCreate, db: db_dependency):
    exam = db.query(Exam).filter(Exam.id == question.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    db_question = Question(
        content=question.content,
        exam_id=question.exam_id
    )
    
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    return db_question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(question_id: int, db: db_dependency): # type: ignore

    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    
    db.delete(question)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)