import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database.core import get_db, Base

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_quiz.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

class TestQuizEndpoints:
    
    def test_root_endpoint(self, setup_database):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Quiz App API"}

    def test_create_quiz_success(self, setup_database):
        quiz_data = {
            "title": "Python Basics",
            "description": "Test your Python knowledge"
        }
        response = client.post("/create-quiz", json=quiz_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Quiz created successfully"
        assert data["title"] == "Python Basics"
        assert "id" in data

    def test_create_quiz_duplicate_title(self, setup_database):
        quiz_data = {
            "title": "Python Basics",
            "description": "Test your Python knowledge"
        }
        client.post("/create-quiz", json=quiz_data)
        response = client.post("/create-quiz", json=quiz_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_get_quiz_success(self, setup_database):
        quiz_data = {
            "title": "Math Quiz",
            "description": "Basic math questions"
        }
        create_response = client.post("/create-quiz", json=quiz_data)
        quiz_id = create_response.json()["id"]
        
        response = client.get(f"/quiz/{quiz_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == quiz_id
        assert data["title"] == "Math Quiz"
        assert data["description"] == "Basic math questions"

    def test_get_quiz_not_found(self, setup_database):
        response = client.get("/quiz/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Quiz not found"

    def test_create_question_success(self, setup_database):
        quiz_data = {
            "title": "Science Quiz",
            "description": "Science questions"
        }
        quiz_response = client.post("/create-quiz", json=quiz_data)
        quiz_id = quiz_response.json()["id"]
        
        question_data = {
            "question_text": "What is the chemical symbol for water?",
            "options": ["H2O", "CO2", "O2", "NaCl"],
            "correct_answer": 0
        }
        response = client.post(f"/quiz/{quiz_id}/question", json=question_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Question created successfully"
        assert data["quiz_id"] == quiz_id
        assert "question_id" in data

    def test_create_question_invalid_quiz(self, setup_database):
        question_data = {
            "question_text": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": 1
        }
        response = client.post("/quiz/999/question", json=question_data)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Quiz not found"

    def test_create_question_invalid_correct_answer(self, setup_database):
        quiz_data = {
            "title": "Test Quiz",
            "description": "Test"
        }
        quiz_response = client.post("/create-quiz", json=quiz_data)
        quiz_id = quiz_response.json()["id"]
        
        question_data = {
            "question_text": "Test question?",
            "options": ["A", "B"],
            "correct_answer": 5
        }
        response = client.post(f"/quiz/{quiz_id}/question", json=question_data)
        
        assert response.status_code == 400
        assert "Invalid correct_answer index" in response.json()["detail"]

    def test_submit_answer_correct(self, setup_database):
        quiz_data = {"title": "Test Quiz", "description": "Test"}
        quiz_response = client.post("/create-quiz", json=quiz_data)
        quiz_id = quiz_response.json()["id"]
        
        question_data = {
            "question_text": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": 1
        }
        question_response = client.post(f"/quiz/{quiz_id}/question", json=question_data)
        question_id = question_response.json()["question_id"]
        
        answer_data = {
            "question_id": question_id,
            "answer": "4",
            "user_id": 1
        }
        response = client.post(f"/quiz/{quiz_id}/answer", json=answer_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is True
        assert data["message"] == "Correct answer!"
        assert data["current_score"] == 1

    def test_submit_answer_incorrect(self, setup_database):
        quiz_data = {"title": "Test Quiz", "description": "Test"}
        quiz_response = client.post("/create-quiz", json=quiz_data)
        quiz_id = quiz_response.json()["id"]
        
        question_data = {
            "question_text": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": 1
        }
        question_response = client.post(f"/quiz/{quiz_id}/question", json=question_data)
        question_id = question_response.json()["question_id"]
        
        answer_data = {
            "question_id": question_id,
            "answer": "3",
            "user_id": 1
        }
        response = client.post(f"/quiz/{quiz_id}/answer", json=answer_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is False
        assert data["message"] == "Incorrect answer"
        assert data["correct_answer"] == "4"
        assert data["current_score"] == 0

    def test_submit_answer_duplicate_attempt(self, setup_database):
        quiz_data = {"title": "Test Quiz", "description": "Test"}
        quiz_response = client.post("/create-quiz", json=quiz_data)
        quiz_id = quiz_response.json()["id"]
        
        question_data = {
            "question_text": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": 1
        }
        question_response = client.post(f"/quiz/{quiz_id}/question", json=question_data)
        question_id = question_response.json()["question_id"]
        
        answer_data = {
            "question_id": question_id,
            "answer": "4",
            "user_id": 1
        }
        client.post(f"/quiz/{quiz_id}/answer", json=answer_data)
        
        response = client.post(f"/quiz/{quiz_id}/answer", json=answer_data)
        
        assert response.status_code == 400
        assert "already attempted" in response.json()["detail"]

    def test_get_quiz_questions(self, setup_database):
        quiz_data = {"title": "Test Quiz", "description": "Test"}
        quiz_response = client.post("/create-quiz", json=quiz_data)
        quiz_id = quiz_response.json()["id"]
        
        questions = [
            {"question_text": "What is 2+2?", "options": ["3", "4", "5", "6"], "correct_answer": 1},
            {"question_text": "What is the capital of France?", "options": ["London", "Berlin", "Paris", "Madrid"], "correct_answer": 2}
        ]
        
        for question in questions:
            client.post(f"/quiz/{quiz_id}/question", json=question)
        
        response = client.get(f"/quiz/{quiz_id}/questions")
        
        assert response.status_code == 200
        data = response.json()
        assert data["quiz_id"] == quiz_id
        assert len(data["questions"]) == 2
        assert data["questions"][0]["question_text"] == "What is 2+2?"
        assert len(data["questions"][0]["options"]) == 4

    def test_case_insensitive_answer(self, setup_database):
        quiz_data = {"title": "Test Quiz", "description": "Test"}
        quiz_response = client.post("/create-quiz", json=quiz_data)
        quiz_id = quiz_response.json()["id"]
        
        question_data = {
            "question_text": "What is the capital of France?",
            "options": ["London", "Paris", "Berlin", "Madrid"],
            "correct_answer": 1
        }
        question_response = client.post(f"/quiz/{quiz_id}/question", json=question_data)
        question_id = question_response.json()["question_id"]
        
        answer_data = {
            "question_id": question_id,
            "answer": "PARIS",
            "user_id": 1
        }
        response = client.post(f"/quiz/{quiz_id}/answer", json=answer_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is True
