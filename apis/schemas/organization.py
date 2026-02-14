from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class OrganizationBase(BaseModel):
    name: str
    domain: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationOut(OrganizationBase):
    id: int
    owner_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class OrganizationMemberLine(BaseModel):
    user_id: int
    role: str
    joined_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class OrganizationDetail(OrganizationOut):
    # Depending on needs, might include basic member list
    pass
