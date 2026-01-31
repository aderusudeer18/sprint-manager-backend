from sqlalchemy import Column, Integer, String, Enum, Text, ForeignKey, DateTime
from database import Base
from datetime import datetime, timezone


WorkType = ('Bug', 'Task', 'Story', 'Review', 'Closed - Won\'t Do')
Workflow = ('Backlog', 'To Do', 'In Progress', 'On Hold', 'QA', 'Review' , 'Closed - Won\'t Do', 'Done')
Priority = ('Blocker', 'Critical', 'Major','Medium', 'Minor', 'Trivial')



class Task(Base):
    __tablename__ = "task"
   

    id = Column(Integer, primary_key=True, index=True)

    work_type = Column(Enum(*WorkType, name="work_type_enum"), nullable=False)
    code = Column(Integer, index=True,  unique=True,nullable=False)
    title = Column(String, index=True, nullable=False)
    work_flow = Column(Enum(*Workflow, name="workflow_enum"), nullable=True)
    story_points = Column(Integer, nullable=True)
    priority = Column(Enum(*Priority, name="status_enum"), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    parent_task =   Column(Integer, ForeignKey("task.id"), nullable=True)

    sprint_id = Column(Integer, ForeignKey ("sprint.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)

    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)