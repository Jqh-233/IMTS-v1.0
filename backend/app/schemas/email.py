from typing import Optional

from pydantic import BaseModel


class EmailOut(BaseModel):
    id: int
    message_id: Optional[str] = None
    subject: str
    sender: str
    body: str
    received_at: str
    is_processed: bool

    model_config = {"from_attributes": True}


class EmailListOut(BaseModel):
    id: int
    message_id: Optional[str] = None
    subject: str
    sender: str
    received_at: str
    is_processed: bool
    task_id: Optional[int] = None
    task_name: Optional[str] = None
    task_status: Optional[str] = None

    model_config = {"from_attributes": True}
