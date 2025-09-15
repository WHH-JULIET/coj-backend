# app/models/schemas.py
from pydantic import BaseModel
from typing import List, Optional
import uuid


class ProblemCreate(BaseModel):
    difficulty: int
    prob_stmt: str
    topic_ids: Optional[List[uuid.UUID]] = None  # accepts list of UUIDs or None

    def __init__(self, **data):
        if 'topic_ids' not in data or data['topic_ids'] is None:
            data['topic_ids'] = []
        super().__init__(**data)


class ProblemOut(BaseModel):
    problem_id: str
    difficulty: int
    prob_stmt: str
    topic_ids: List[str]


    class Config:
        orm_mode = True
