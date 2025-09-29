from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.quiz import models as quiz_models
from src.entities import quiz as quiz_entities

def create_quiz(db: Session, quiz_data: quiz_models.QuizCreate):
    existing_quiz = db.query(quiz_entities.Quiz).filter(quiz_entities.Quiz.title == quiz_data.title).first()
    if existing_quiz:
        raise HTTPException(status_code=400, detail="Quiz with this title already exists")
    
    new_quiz = quiz_entities.Quiz(title=quiz_data.title, description=quiz_data.description)
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    return new_quiz

def get_quiz(db: Session, quiz_id: int):
    quiz = db.query(quiz_entities.Quiz).filter(quiz_entities.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

def create_question(db: Session, quiz_id: int, question_data: quiz_models.QuestionCreate):
    quiz = db.query(quiz_entities.Quiz).filter(quiz_entities.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if question_data.correct_answer >= len(question_data.options) or question_data.correct_answer < 0:
        raise HTTPException(status_code=400, detail="Invalid correct_answer index")
    
    new_question = quiz_entities.Question(
        quiz_id=quiz_id, 
        question_text=question_data.question_text
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    
    for i, option_text in enumerate(question_data.options):
        is_correct = (i == question_data.correct_answer)
        new_option = quiz_entities.QuestionOptions(
            question_id=new_question.id,
            option_text=option_text,
            correct_answer=is_correct
        )
        db.add(new_option)
    
    db.commit()
    return new_question

def submit_answer(db: Session, quiz_id: int, answer_data: quiz_models.AnswerSubmit):
    quiz = db.query(quiz_entities.Quiz).filter(quiz_entities.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    question = db.query(quiz_entities.Question).filter(
        quiz_entities.Question.id == answer_data.question_id,
        quiz_entities.Question.quiz_id == quiz_id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found in this quiz")
    
    existing_attempt = db.query(quiz_entities.Attempt).filter(
        quiz_entities.Attempt.quiz_id == quiz_id,
        quiz_entities.Attempt.user_id == answer_data.user_id,
        quiz_entities.Attempt.question_id == answer_data.question_id
    ).first()
    
    if existing_attempt:
        raise HTTPException(status_code=400, detail="You have already attempted this question")

    new_attempt = quiz_entities.Attempt(
        quiz_id=quiz_id,
        user_id=answer_data.user_id,
        question_id=answer_data.question_id,
        selected_option=answer_data.answer
    )
    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    correct_option = db.query(quiz_entities.QuestionOptions).filter(
        quiz_entities.QuestionOptions.question_id == answer_data.question_id,
        quiz_entities.QuestionOptions.correct_answer == True
    ).first()

    if not correct_option:
        raise HTTPException(status_code=500, detail="No correct option found for this question")

    is_correct = answer_data.answer.strip().lower() == correct_option.option_text.strip().lower()

    user_result = db.query(quiz_entities.Result).filter(
        quiz_entities.Result.quiz_id == quiz_id,
        quiz_entities.Result.user_id == answer_data.user_id
    ).first()

    if user_result:
        if is_correct:
            user_result.score += 1
    else:
        user_result = quiz_entities.Result(
            quiz_id=quiz_id,
            user_id=answer_data.user_id,
            score=1 if is_correct else 0
        )
        db.add(user_result)

    db.commit()
    db.refresh(user_result)

    return {
        "message": "Correct answer!" if is_correct else "Incorrect answer",
        "is_correct": is_correct,
        "correct_answer": correct_option.option_text if not is_correct else None,
        "current_score": user_result.score
    }

def get_quiz_questions(db: Session, quiz_id: int):
    quiz = db.query(quiz_entities.Quiz).filter(quiz_entities.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = db.query(quiz_entities.Question).filter(quiz_entities.Question.quiz_id == quiz_id).all()
    
    result = []
    for question in questions:
        options = db.query(quiz_entities.QuestionOptions).filter(
            quiz_entities.QuestionOptions.question_id == question.id
        ).all()
        
        result.append({
            "id": question.id,
            "question_text": question.question_text,
            "options": [{"id": opt.id, "text": opt.option_text} for opt in options]
        })
    
    return {"quiz_id": quiz_id, "questions": result}