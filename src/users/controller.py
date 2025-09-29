from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.users import service as user_service

router = APIRouter(tags=["users"])

@router.get("/user/{user_id}/results")
async def get_user_results(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user_results(db, user_id)