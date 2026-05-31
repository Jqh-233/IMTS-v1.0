"""任务 CRUD + 统计 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskOut, TaskStatusUpdate, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
def list_tasks(
    search: str = Query("", description="搜索任务名称"),
    priority: str = Query("", description="按优先级筛选: high/medium/low"),
    sort: str = Query("deadline", description="排序字段: deadline/priority/created_at"),
    db: Session = Depends(get_db),
):
    q = db.query(Task)
    if search:
        q = q.filter(Task.task_name.contains(search))
    if priority:
        q = q.filter(Task.priority == priority)

    priority_order = {"high": 1, "medium": 2, "low": 3}
    q = q.order_by(
        Task.deadline.asc(),
        Task.id.desc(),
    )

    # 显式按优先级排序（Python 侧排序确保 high > medium > low）
    tasks = q.all()
    tasks.sort(key=lambda t: priority_order.get(t.priority, 99))

    # 补充邮件信息
    result = []
    for t in tasks:
        d = TaskOut.model_validate(t)
        if t.email:
            d.email_subject = t.email.subject
            d.email_sender = t.email.sender
        result.append(d)
    return result


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "total": db.query(Task).count(),
        "high_priority": db.query(Task).filter(Task.priority == "high").count(),
        "active": db.query(Task).filter(Task.status != "done").count(),
        "done": db.query(Task).filter(Task.status == "done").count(),
    }


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    d = TaskOut.model_validate(task)
    if task.email:
        d.email_subject = task.email.subject
        d.email_sender = task.email.sender
    return d


@router.post("", response_model=TaskOut, status_code=201)
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    task = Task(
        task_name=body.task_name,
        deadline=body.deadline,
        priority=body.priority.value,
        status=body.status.value,
        category=body.category.value,
        confidence=1.0,
        confidence_source="manual",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, body: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    for field in ("task_name", "deadline", "priority", "category", "status"):
        val = getattr(body, field, None)
        if val is not None:
            setattr(task, field, val.value if hasattr(val, "value") else val)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    db.delete(task)
    db.commit()


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_status(task_id: int, body: TaskStatusUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    task.status = body.status.value
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


