from fastapi import APIRouter, Depends, HTTPException, status
from apis.dependencies import get_current_user
from sqlalchemy.orm import Session
from database import get_db
from models.user import User   # correct model
from models.project import Project
from apis.schemas.user import UserCreate, UserUpdate, UserGet
import datetime
from typing import Optional

router = APIRouter()


# CREATE USER
@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        # Use HTTPException so the frontend 'catch' block triggers
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ID is already registered"
        )

    if user.mobile:
        existing_mobile = db.query(User).filter(User.mobile == user.mobile).first()
        if existing_mobile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already registered"
            )
        
    
    # SECURITY: Hash the password before saving to DB
    # Never store plain-text passwords!
    from core.security import get_password_hash
    hashed_password = get_password_hash(user.password)
    
    # Create user model with hashed password
    user_data = user.model_dump()
    raw_password = user_data.pop("password")
    org_name = user_data.pop("organisation", None) # Remove organisation from user_data
    
    new_user = User(**user_data, password=hashed_password)
    
    new_user.created_at = datetime.datetime.now(datetime.timezone.utc)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create Organization for the user
    # Logic: Use provided name or default to email domain
    final_org_name = org_name if org_name else user.email.split('@')[-1]
    
    # Create Org
    from models.organization import Organization
    from models.user_organization import UserOrganization
    
    new_org = Organization(
        name=final_org_name,
        owner_id=new_user.id
        # domain could be inferred, but let's leave it null for now or extracted
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    # Add User as Admin of this Org
    membership = UserOrganization(
        user_id=new_user.id,
        organization_id=new_org.id,
        role="Admin"
    )
    db.add(membership)
    db.commit()
    
    return {"User created successfully": new_user, "Organization created": new_org.name}


@router.post("/valid")
def validate_user(getuser: UserGet, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == getuser.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    from core.security import verify_password
    if not verify_password(getuser.password, user.password):
        raise HTTPException(status_code=404, detail="Please check your password")
    # if getuser.password != user.password:
    #     raise HTTPException(status_code=404, detail="Please check your password")

    return user


@router.get("/project/{project_id}", dependencies=[Depends(get_current_user)])
def get_users_by_project(project_id: int, db: Session = Depends(get_db), ):
    return db.query(User).join(User.projects).filter(Project.id == project_id).all()


@router.get("/assignproject/{organisation}", dependencies=[Depends(get_current_user)])  
def get_users_not_in_project(organisation: str, project_id: int, db: Session = Depends(get_db), ):
    
        return (
        db.query(User)
        .filter(
            User.organisation == organisation,
            # This selects users who DO NOT have a project with this ID
            ~User.projects.any(Project.id == project_id)
        )
        .all()
    )
   
@router.get("/unassignproject/{organisation}", dependencies=[Depends(get_current_user)])  
def get_users_in_project(organisation: str, project_id: int, db: Session = Depends(get_db), ):
    
       return (
        db.query(User)
        .join(User.projects) # Connects the User table to the Projects table
        .filter(
            User.organisation == organisation,
            Project.id == project_id # Filters for specifically this project
        )
        .all()
    )

# GET USER BY ID
@router.get("/{user_id}", dependencies=[Depends(get_current_user)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# UPDATE USER
@router.patch("/{user_id}", dependencies=[Depends(get_current_user)])
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.model_dump(exclude_unset=True)
    if "organisation" in user_data:
        del user_data["organisation"] # Handle separately if needed, or ignore

    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    db_user.updated_at =  datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(db_user)
    return db_user


# DELETE USER
@router.delete("/{user_id}", dependencies=[Depends(get_current_user)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}