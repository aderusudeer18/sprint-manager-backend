from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models.user import User
from apis.schemas.search_by_name_mobile import UserSearchResponse, UserSearchItem

router = APIRouter()

@router.get("/members", response_model=UserSearchResponse)
def search_members(
    q: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(None, description="Filter by role"),
    db: Session = Depends(get_db)):
    # Base query
    query = db.query(User)

    if q:
        query = query.filter(
            or_(
                User.full_name.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%")
            )
        )
    
    if role:
        query = query.filter(User.role.ilike(f"%{role}%"))

    users = query.all()

    return {
        "items": users
    }
