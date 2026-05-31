from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String, nullable=True)
    subject = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    received_at = Column(String, nullable=False)
    is_processed = Column(Integer, nullable=False, default=0)

    tasks = relationship("Task", back_populates="email")
