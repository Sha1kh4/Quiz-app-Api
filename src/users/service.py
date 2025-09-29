from sqlalchemy.orm import Session
from src.entities import quiz as quiz_entities
from src.entities import user as user_entities

def get_user_results(db: Session, user_id: int):
    results = db.query(quiz_entities.Result).filter(quiz_entities.Result.user_id == user_id).all()
    
    user_results = []
    for result in results:
        quiz = db.query(quiz_entities.Quiz).filter(quiz_entities.Quiz.id == result.quiz_id).first()
        total_questions = db.query(quiz_entities.Question).filter(quiz_entities.Question.quiz_id == result.quiz_id).count()
        
        user_results.append({
            "quiz_id": result.quiz_id,
            "quiz_title": quiz.title if quiz else "Unknown",
            "score": result.score,
            "total_questions": total_questions,
            "percentage": (result.score / total_questions * 100) if total_questions > 0 else 0
        })
    
    return {"user_id": user_id, "results": user_results}