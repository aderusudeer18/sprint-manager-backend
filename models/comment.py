from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


  # make sure Base is imported from your database module

class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to User
    author = relationship("User", back_populates="comments")

