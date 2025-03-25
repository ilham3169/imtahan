from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response # type: ignore
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy.sql.expression import text # type: ignore
from database import sessionLocal
from models import Question, Exam
from schemas import ExamResponse, ExamCreate
import logging
from datetime import datetime
import pytz # type: ignore



TIMEZONE = pytz.timezone("Asia/Baku")

router = APIRouter(
    prefix="/exams",
    tags=["exams"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
logger = logging.getLogger("uvicorn.error")


@router.get("", response_model=List[ExamResponse], status_code=status.HTTP_200_OK)
async def get_all_exams(db: db_dependency): # type: ignore
    exams = db.query(Exam).all()
    return exams

@router.post("/create", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def create_exam(exam: ExamCreate, db: db_dependency): # type: ignore
    db_exam = Exam( name=exam.name, time=exam.time )
    
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    
    return db_exam

@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(exam_id: int, db: db_dependency): # type: ignore

    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    
    db.delete(exam)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)