from datetime import datetime

from sqlalchemy import REAL, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=True)
    task_name = Column(String, nullable=False)
    deadline = Column(String, nullable=False)
    priority = Column(String, nullable=False, default="medium")
    status = Column(String, nullable=False, default="pending")
    category = Column(String, nullable=False, default="通用任务")
    confidence = Column(REAL, nullable=False, default=0.8)
    confidence_source = Column(String, nullable=False, default="rules")
    created_at = Column(DateTime, default=datetime.now)

    email = relationship("Email", back_populates="tasks")
