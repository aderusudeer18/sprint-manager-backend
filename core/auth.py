from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User

def get_current_user(db: Session = Depends(get_db)):
    """
    TEMP implementation:
    Returns first user from DB.
    Replace with JWT later.
    """
    user = db.query(User).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )

    return user
