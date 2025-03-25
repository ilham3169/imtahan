from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = False
    username: str

class UserCreate(UserBase):
    password: str
    result: int  

class UserResponse(UserBase):
    id: int
    result: int
    class Config:
        from_attributes = True

class UserLogin(BaseModel):  
    username: str
    password: str

class EmailSchema(BaseModel):
    email: EmailStr

class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str

class ExamBase(BaseModel):
    name: str
    time: str

class ExamCreate(ExamBase):
    pass

class ExamResponse(ExamBase):
    id: int
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    content: str

class QuestionCreate(QuestionBase):
    exam_id: int

class QuestionResponse(QuestionBase):
    id: int
    exam_id: int
    class Config:
        from_attributes = True

class AnswerBase(BaseModel):
    score: int
    content: str

class AnswerCreate(AnswerBase):
    question_id: int
    content: str

class AnswerResponse(AnswerBase):
    id: int
    question_id: int
    class Config:
        from_attributes = True

class UserExamResponse(BaseModel):
    id: int
    user_id: int
    exam_id: int
    completed_at: datetime
    score: int

    class Config:
        orm_mode = True