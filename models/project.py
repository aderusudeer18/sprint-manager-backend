from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from models.organization import Organization
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from models.association import user_projects

class Project(Base):
    __tablename__="project"
    
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String,index=True)
    manager_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    organization = relationship("Organization", back_populates="projects")
    users = relationship("User", secondary=user_projects, back_populates="projects")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)