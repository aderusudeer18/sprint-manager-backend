from pydantic import BaseModel
from typing import List
from datetime import datetime



class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    user_id: int  


class CommentOut(CommentBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
    # model_config = ConfigDict(from_attributes=True)

'''class CommentCreate(BaseModel):
    task_id: int
    text: str
    mentioned_user_ids: List[int] = []

class CommentUpdate(BaseModel):
    text: str
    mentioned_user_ids: List[int] = []

class CommentResponse(BaseModel):
    id: int
    task_id: int
    author_id: int
    text: str
    created_at: datetime'''



