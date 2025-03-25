from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response # type: ignore
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy.sql.expression import text # type: ignore
from database import sessionLocal
from models import Question, Exam, UserAnswer, Answer
from schemas import UserAnswerResponse, UserAnswerCreate
import logging
from datetime import datetime
import pytz # type: ignore

router = APIRouter(
    prefix="/user-answers",
    tags=["user-answers"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("", response_model=List[UserAnswerResponse], status_code=status.HTTP_200_OK)
async def get_all_user_answers(db: db_dependency):
    user_ans = db.query(UserAnswer).all()
    return user_ans

@router.post("/create", response_model=List[UserAnswerResponse], status_code=status.HTTP_201_CREATED)
async def create_user_answer(user_answer_data: UserAnswerCreate, db: db_dependency):
    user_id = user_answer_data.user_id
    created_answers = []  # To store created UserAnswer objects

    # Process each answer in the list
    for answer_data in user_answer_data.answer:
        question_id = answer_data.question_id
        answer_id = answer_data.answer_id
        user_answer = answer_data.user_answer

        # Check if the answer exists and get the correct answer content
        correct_answer_record = db.query(Answer).filter(Answer.id == answer_id).first()
        if not correct_answer_record:
            raise HTTPException(status_code=404, detail=f"Answer with id {answer_id} not found")

        # Compute answer_result
        answer_result = (user_answer == correct_answer_record.content)

        # Create new UserAnswer object
        db_user_answer = UserAnswer(
            user_id=user_id,
            question_id=question_id,
            answer_id=answer_id,
            user_answer=user_answer,
            answer_result=answer_result
        )

        # Check for duplicate entry
        existing_answer = db.query(UserAnswer).filter(
            UserAnswer.user_id == user_id,
            UserAnswer.question_id == question_id,
            UserAnswer.answer_id == answer_id
        ).first()
        if existing_answer:
            raise HTTPException(status_code=400, detail=f"User answer already exists for question {question_id}")

        # Add to the list of objects to commit
        created_answers.append(db_user_answer)

    # Add all answers to the database in one transaction
    try:
        db.add_all(created_answers)
        db.commit()
        for answer in created_answers:
            db.refresh(answer)  # Refresh each object to get updated data
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return created_answers