from pydantic import BaseModel

from models.user import User
from apis.schemas.user import UserCreate

class ProjectCreate(BaseModel):
    title: str
    users: list[int]
    manager_id: int
    organization_id: int
    

class ProjectUpdate(BaseModel):
    title: str | None = None
    
class AssignUsers(BaseModel):
    user_ids: list[int]