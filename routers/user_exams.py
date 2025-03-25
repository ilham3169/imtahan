from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import sessionLocal
from models import User, Exam, UserExam
from schemas import UserExamResponse
import jwt
from datetime import datetime
from typing import Annotated

router = APIRouter(
    prefix="/user-exams",
    tags=["user-exams"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

