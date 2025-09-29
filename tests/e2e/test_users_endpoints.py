import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database.core import get_db, Base

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_users.db"
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

class TestUserEndpoints:
    def test_get_user_results(self, setup_database):
        # Setup: Create quiz, questions, and submit answers
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
        
        response = client.get("/user/1/results")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["quiz_id"] == quiz_id
        assert data["results"][0]["score"] == 1
        assert data["results"][0]["total_questions"] == 1
        assert data["results"][0]["percentage"] == 100.0