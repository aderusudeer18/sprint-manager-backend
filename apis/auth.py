from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from core.security import verify_password, create_access_token
from core.config import settings

router = APIRouter()

@router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, retrieve an access token for future requests.
    
    Args:
        form_data: Contains 'username' and 'password'. 
                   Note: 'username' maps to 'email' in our system.
    """
    # 1. Fetch user by email (username)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # 2. Check if user exists & password matches
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Create Access Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # 4. Return standard OAuth2 response
    return {"access_token": access_token, "token_type": "bearer"}
