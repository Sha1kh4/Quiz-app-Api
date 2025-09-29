from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# Request models
class QuizCreate(BaseModel):
    title: str
    description: str

class QuestionCreate(BaseModel):
    question_text: str
    options: List[str]
    correct_answer: int

class AnswerSubmit(BaseModel):
    question_id: int
    answer: str
    user_id: int

# Response models
class QuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    created_at: datetime

class OptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    text: str
        
class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    question_text: str
    options: List[OptionResponse]

class QuizWithQuestionsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    quiz_id: int
    questions: List[QuestionResponse]

class AnswerResponse(BaseModel):
    message: str
    is_correct: bool
    correct_answer: Optional[str] = None
    current_score: int