from pydantic import BaseModel
from typing import List

class UserResult(BaseModel):
    quiz_id: int
    quiz_title: str
    score: int
    total_questions: int
    percentage: float

class UserResultsResponse(BaseModel):
    user_id: int
    results: List[UserResult]
