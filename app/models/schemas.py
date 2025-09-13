from pydantic import BaseModel
from typing import List

class ProblemCreate(BaseModel):
    difficulty: int
    prob_stmt: str
    topic_ids: List[str]  # List of topic IDs to link

class ProblemOut(BaseModel):
    problem_id: str
    difficulty: int
    prob_stmt: str
    topic_ids: List[str]

    class Config:
        orm_mode = True