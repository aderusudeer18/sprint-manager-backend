from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserSearchItem(BaseModel):
    id: int
    full_name: Optional[str]
    email: str
    role: Optional[str]
    mobile: Optional[str]

    class Config:
        from_attributes = True

class UserSearchResponse(BaseModel):
    items: List[UserSearchItem]
