from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.project import Project
from apis.schemas.project import AssignUsers, ProjectCreate, ProjectUpdate
from models.user import User
from apis.dependencies import get_current_user
import datetime 

router = APIRouter()


# CREATE PROJECT
@router.post("/")
def create_project(
    project_data: ProjectCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Validate: Does the user belong to this Organization?
    # We check the UserOrganization association table
    from models.user_organization import UserOrganization
    membership = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id,
        UserOrganization.organization_id == project_data.organization_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=403, 
            detail="Access Denied: You are not a member of this Organization."
        )

    # 2. Validate: Are the assigned users/manager also members? (Optional but strict)
    # For MVP, checking the creator's permission is the critical step.
    
    users_to_add = db.query(User).filter(User.id.in_(project_data.users)).all()
    new_project = Project(
        title=project_data.title, 
        manager_id = project_data.manager_id,
        organization_id = project_data.organization_id
    )
    new_project.users = users_to_add
    new_project.created_at = datetime.datetime.now(datetime.timezone.utc)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return new_project



# Get all projects
@router.get("/user/{user_id}")
def get_projects_by_user(user_id: int, db: Session = Depends(get_db), ):
    return db.query(Project).join(Project.users).filter(User.id == user_id).all()


# GET PROJECT
@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


# UPDATE PROJECT
@router.put("/{project_id}")
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in project.model_dump(exclude_unset=True).items():
        setattr(db_project, key, value)

    db_project.created_at =  datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(db_project)
    return db_project


# DELETE PROJECT
@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


@router.post("/add-users/{project_id}")
def add_users_to_project(project_id: int, data: AssignUsers, db: Session = Depends(get_db)):

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    users = db.query(User).filter(User.id.in_(data.user_ids)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No valid users found") 
    for user in users:
        if user not in project.users:
            project.users.append(user)

    db.commit()
    return {"message": "Project added to user"}


@router.post("/remove-users/{project_id}")
def remove_users_from_project(project_id: int, data: AssignUsers, db: Session = Depends(get_db)):

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    users = db.query(User).filter(User.id.in_(data.user_ids)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No valid users found") 
    for user in users:
        if user in project.users:
            project.users.remove(user)

    db.commit()
    return {"message": "Project removed from user"}