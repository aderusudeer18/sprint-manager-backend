from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.task import Task
from apis.schemas.ai import PromptRequest 
from typing import List, Optional
from fastapi import Query
import datetime
from apis.ai import send_task_to_gemini
from apis.schemas.task import TaskCreate, TaskUpdate, Workflow, WorkType, Priority
from apis.schemas.task import validate_search_query


router = APIRouter()


NO_DESCRIPTION_GENERATED = "No description generated"
TASK_NOT_FOUND = "Task not found"

@router.post("/")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):

    last_task = db.query(Task).order_by(Task.code.desc()).first()
    new_code = int(last_task.code) + 1 if last_task else 1001

    new_task = Task(
        work_type=task.work_type,
        title=task.title,
        work_flow=task.work_flow,
        story_points=task.story_points,
        priority=task.priority,
        user_id=task.user_id,
        parent_task = task.parent_task if task.parent_task not in [0, "", None] else None,
        sprint_id=task.sprint_id,
        project_id=task.project_id,
        description=task.description,
        code=new_code  

    )
    
    new_task.created_at = datetime.datetime.now(datetime.timezone.utc)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return {
        "task": new_task
       
    }

@router.get("/all") 
def get_all_tasks(
    project_ids: List[int] = Query(...), 
    sprint_ids: Optional[List[int]] = Query(None), 
    user_ids: Optional[List[int]] = Query(None),
    work_type: Optional[WorkType] = None,
    work_flow: Optional[Workflow] = None,
    priority: Optional[Priority] = None,
    story_points: Optional[int] = None, 
    description: Optional[str] = None,
    parent_task: Optional[int] = None, 
    db: Session = Depends(get_db)
):
   
    query = db.query(Task).filter(Task.project_id.in_(project_ids))

    if sprint_ids:
        query = query.filter(Task.sprint_id.in_(sprint_ids))
    
    if user_ids:
        query = query.filter(Task.user_id.in_(user_ids))

    if work_type:
        query = query.filter(Task.work_type == work_type)

    if work_flow:
        query = query.filter(Task.work_flow == work_flow)

    if priority:
        query = query.filter(Task.priority == priority)

    if story_points is not None:
        query = query.filter(Task.story_points == story_points)

    # 3. Use .contains() for descriptions to allow partial searches
    if description:
        query = query.filter(Task.description.contains(description))

    if parent_task is not None:
        query = query.filter(Task.parent_task == parent_task)

    return query.all()


@router.get("/unassigned")
def get_unassigned_tasks(
    project_ids: List[int] = Query(...), 
    user_ids: Optional[List[int]] = Query(None), 
    sprint_ids: Optional[List[int]] = Query(None), 
    backlog: bool = False,
    work_type: Optional[WorkType] = None,
    work_flow: Optional[Workflow] = None,
    priority: Optional[Priority] = None,
    story_points: Optional[int] = None, 
    description: Optional[str] = None,
    parent_task: Optional[int] = None, 
    db: Session = Depends(get_db)):
    # Base query restricted to the projects provided
    query = db.query(Task).filter(Task.project_id.in_(project_ids))

    if backlog:
        # Pure Backlog:  no sprint
        query = query.filter( Task.sprint_id.is_(None))
         
    elif sprint_ids:
        # Assigned to specific sprints but NO user assigned
        query = query.filter(Task.sprint_id.in_(sprint_ids), Task.user_id.is_(None))

    # Logic for Assignment/Sprint filtering
    elif user_ids:
        # Assigned to specific users but NOT assigned to a sprint
        query = query.filter(Task.user_id.in_(user_ids), Task.sprint_id.is_(None))

    # Attribute Filters
    if work_type:
        query = query.filter(Task.work_type == work_type)
    if work_flow:
        query = query.filter(Task.work_flow == work_flow)
    if priority:
        query = query.filter(Task.priority == priority)
    if story_points is not None:
        query = query.filter(Task.story_points == story_points)
    if description:
        query = query.filter(Task.description.ilike(f"%{description}%"))
    if parent_task is not None:
        query = query.filter(Task.parent_task == parent_task)

    return query.all()


# GET TASK BY ID
@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail=TASK_NOT_FOUND)

    return task


# UPDATE TASK
@router.patch("/{task_id}")
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail=TASK_NOT_FOUND)
    
    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)

    db_task.updated_at=  datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(db_task)
    return db_task



# UPDATE DESCRIPTION
@router.patch("/{task_id}/description")
def update_description(task_id: int, req: PromptRequest, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail=TASK_NOT_FOUND)

    try:
        prompt=req.prompt
        request = PromptRequest(prompt=prompt)
        result = send_task_to_gemini(request)
        description = result.get("result", NO_DESCRIPTION_GENERATED)
       
    except Exception as e:
        description = f"Error generating description: {str(e)}"

    # Update the task
    db_task.description = description
    db_task.updated_at =  datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(db_task)

    return db_task



# DELETE TASK
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail=TASK_NOT_FOUND)

    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}



# 🔍 SEARCH TASKS
@router.get("/search/ByTitle")
def search_tasks(
    q: str = Query(..., description="Task title"),
    db: Session = Depends(get_db)
):
    search_text = validate_search_query(q)  # ✅ validation used here

    tasks = (
        db.query(Task)
        .filter(Task.title.ilike(f"%{search_text}%"))
        .all()
    )
    if len(tasks):
        return tasks
    else:
        return "No task is found with your search!"