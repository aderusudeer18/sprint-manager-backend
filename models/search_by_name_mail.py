# This model file is intended for any database models related to member search.
# Currently, the search logic uses the existing User model from models/user.py.

from database import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone

class MemberSearchLog(Base):
    __tablename__ = "member_search_log"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    performed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
