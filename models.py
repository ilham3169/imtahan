from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(63), nullable=False)
    last_name = Column(String(63), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    password = Column(String(255), nullable=False)
    result = Column(Integer, nullable=False)
    username = Column(String(50), unique=True, nullable=False)

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    time = Column(String(50), nullable=False)
    
    questions = relationship("Question", back_populates="exam")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    
    exam = relationship("Exam", back_populates="questions")
    answers = relationship("Answer", back_populates="question")

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    score = Column(Integer, nullable=False)
    content = Column(String(1023), nullable=False)
    
    question = relationship("Question", back_populates="answers")

class UserExam(Base):
    __tablename__ = "user_exams"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    completed_at = Column(DateTime, default=func.now())
    score = Column(Integer)

class UserAnswer(Base):
    __tablename__ = "user_answers"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    answer_id = Column(Integer, ForeignKey("answers.id"), primary_key=True)
    user_answer = Column(String(255))  # User's submitted answer
    answer_result = Column(Boolean)  # True if correct, False if incorrect