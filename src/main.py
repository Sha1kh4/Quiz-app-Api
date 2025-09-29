from fastapi import FastAPI
from src.database.core import Base, engine
from src.quiz.controller import router as quiz_router
from src.users.controller import router as user_router
app = FastAPI()

""" Only uncomment below to create new tables, 
otherwise the tests will fail if not connected
"""
Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Quiz App API"}

app.include_router(quiz_router)
app.include_router(user_router)
