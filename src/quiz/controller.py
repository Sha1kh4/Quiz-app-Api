from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.quiz import service as quiz_service
from src.quiz import models as quiz_models

router = APIRouter(tags=["quiz"])

@router.post("/create-quiz")
async def create_quiz(quiz_data: quiz_models.QuizCreate, db: Session = Depends(get_db)):
    new_quiz = quiz_service.create_quiz(db, quiz_data)
    return {
        "message": "Quiz created successfully",
        "id": new_quiz.id,
        "title": new_quiz.title
    }

@router.get("/quiz/{quiz_id}")
async def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = quiz_service.get_quiz(db, quiz_id)
    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "created_at": quiz.created_at
    }

@router.post("/quiz/{quiz_id}/question")
async def create_question(
    quiz_id: int, 
    question_data: quiz_models.QuestionCreate, 
    db: Session = Depends(get_db)
):
    new_question = quiz_service.create_question(db, quiz_id, question_data)
    return {
        "message": "Question created successfully",
        "question_id": new_question.id,
        "quiz_id": quiz_id
    }

@router.post("/quiz/{quiz_id}/answer")
async def submit_answer(
    quiz_id: int, 
    answer_data: quiz_models.AnswerSubmit, 
    db: Session = Depends(get_db)
):
    return quiz_service.submit_answer(db, quiz_id, answer_data)

@router.get("/quiz/{quiz_id}/questions")
async def get_quiz_questions(quiz_id: int, db: Session = Depends(get_db)):
    return quiz_service.get_quiz_questions(db, quiz_id)