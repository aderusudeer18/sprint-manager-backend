from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import CITEXT

from models.association import user_projects

class User(Base):
    __tablename__="user"

    id=Column(Integer,primary_key=True,index=True)
    full_name=Column(String,index=True,nullable=True)
    email = Column(CITEXT, index=True, nullable=False, unique=True)
    password=Column(String,nullable=False)
    mobile = Column(String, nullable=True, unique=True)
    role=Column(String,index=True, nullable=True)
    location=Column(String,index=True, nullable=True)
    organisation=Column(CITEXT,index=True, nullable=True, unique=True)
    projects = relationship("Project", secondary=user_projects, back_populates="users")
    is_admin=Column(Boolean, default=False)  # 0 for False, 1 for True
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    comments = relationship("Comment", back_populates="author")
