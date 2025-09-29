from fastapi import FastAPI
from src.quiz.controller import router as quiz_router
from src.users.controller import router as users_router

def register_routes(app: FastAPI):
    app.include_router(quiz_router)
    app.include_router(users_router)