"""邮件列表/详情/同步/提取 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.task_extractor import extract_task as do_extract_task
from app.database import get_db
from app.logging_config import get_logger
from app.models import Email, Task
from app.schemas import EmailListOut, EmailOut, TaskOut
from app.services.mail_sync_service import mark_email_processed, sync_qq_recent_emails, sync_sample_emails

logger = get_logger(__name__)

router = APIRouter(tags=["emails"])


# -- 查询端点 --

@router.get("/api/emails", response_model=list[EmailListOut])
def list_emails(db: Session = Depends(get_db)):
    emails = db.query(Email).order_by(Email.id.desc()).limit(100).all()
    result = []
    for e in emails:
        item = EmailListOut.model_validate(e)
        item.is_processed = bool(e.is_processed)
        task = db.query(Task).filter(Task.email_id == e.id).first()
        if task:
            item.task_id = task.id
            item.task_name = task.task_name
            item.task_status = task.status
        result.append(item)
    return result


@router.get("/api/emails/{email_id}", response_model=EmailOut)
def get_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(Email).get(email_id)
    if not email:
        raise HTTPException(404, "邮件不存在")
    out = EmailOut.model_validate(email)
    out.is_processed = bool(email.is_processed)
    return out


# -- 演示邮件同步 --

@router.post("/api/sync/demo")
def sync_demo(db: Session = Depends(get_db)):
    try:
        all_ids, new_ids = sync_sample_emails(db)
        if not all_ids:
            return {"synced_emails": 0, "extracted_tasks": 0, "message": "无新邮件"}

        created = 0
        failed = 0
        for eid in all_ids:
            # 已有任务则跳过
            if db.query(Task).filter(Task.email_id == eid).first():
                continue

            email = db.query(Email).get(eid)
            if not email:
                continue
            if email.is_processed:
                continue

            email_dict = {
                "id": email.message_id or str(email.id),
                "message_id": email.message_id or str(email.id),
                "subject": email.subject,
                "sender": email.sender,
                "body": email.body,
                "received_at": email.received_at,
                "is_processed": bool(email.is_processed),
            }

            try:
                task_result = do_extract_task(email_dict)
                if task_result.get("should_create_task"):
                    task = Task(
                        email_id=eid,
                        task_name=task_result["task_name"],
                        deadline=task_result["deadline"],
                        priority=task_result["priority"],
                        status=task_result["status"],
                        category=task_result["category"],
                        confidence=task_result.get("confidence", 0.0),
                        confidence_source=task_result.get("confidence_source", "rules"),
                    )
                    db.add(task)
                    created += 1
            except Exception:
                logger.warning("提取演示邮件任务失败 email_id=%d", eid, exc_info=True)
                failed += 1
                continue  # 提取失败的邮件不标记已处理，下次可重试

            mark_email_processed(db, eid)

        db.commit()

        return {
            "synced_emails": len(new_ids),
            "extracted_tasks": created,
            "failed": failed,
            "total_emails": len(all_ids),
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("演示邮件同步异常: %s", e, exc_info=True)
        raise HTTPException(500, f"同步失败：{str(e)}")


# -- QQ 邮箱同步 --

@router.post("/api/sync/qq")
def sync_qq(db: Session = Depends(get_db)):
    try:
        try:
            all_ids, new_ids = sync_qq_recent_emails(db)
        except ValueError as e:
            raise HTTPException(400, str(e))
        except RuntimeError as e:
            raise HTTPException(502, str(e))

        if not all_ids:
            return {"synced_emails": 0, "extracted_tasks": 0, "message": "无新邮件"}

        created = 0
        failed = 0
        for eid in all_ids:
            # 已有任务则跳过
            if db.query(Task).filter(Task.email_id == eid).first():
                continue

            email = db.query(Email).get(eid)
            if not email:
                continue
            if email.is_processed:
                continue

            email_dict = {
                "id": email.message_id or str(email.id),
                "message_id": email.message_id or str(email.id),
                "subject": email.subject,
                "sender": email.sender,
                "body": email.body,
                "received_at": email.received_at,
                "is_processed": bool(email.is_processed),
            }

            try:
                task_result = do_extract_task(email_dict)
                if task_result.get("should_create_task"):
                    task = Task(
                        email_id=eid,
                        task_name=task_result["task_name"],
                        deadline=task_result["deadline"],
                        priority=task_result["priority"],
                        status=task_result["status"],
                        category=task_result["category"],
                        confidence=task_result.get("confidence", 0.0),
                        confidence_source=task_result.get("confidence_source", "rules"),
                    )
                    db.add(task)
                    created += 1
            except Exception:
                logger.warning("提取QQ邮件任务失败 email_id=%d", eid, exc_info=True)
                failed += 1
                continue

            mark_email_processed(db, eid)

        db.commit()

        return {
            "synced_emails": len(new_ids),
            "extracted_tasks": created,
            "failed": failed,
            "total_emails": len(all_ids),
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("QQ邮件同步异常: %s", e, exc_info=True)
        raise HTTPException(500, f"同步失败：{str(e)}")


# -- 提取端点 --

@router.post("/api/emails/{email_id}/extract")
def extract_from_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(Email).get(email_id)
    if not email:
        raise HTTPException(404, "邮件不存在")

    existing = db.query(Task).filter(Task.email_id == email_id).first()
    if existing:
        raise HTTPException(409, "该邮件已提取过任务")

    email_data = {
        "id": email.message_id or str(email.id),
        "message_id": email.message_id or str(email.id),
        "subject": email.subject,
        "sender": email.sender,
        "body": email.body,
        "received_at": email.received_at,
        "is_processed": bool(email.is_processed),
    }

    result = do_extract_task(email_data)

    if not result.get("should_create_task"):
        return {
            "extracted": False,
            "skip_reason": result.get("skip_reason", "该邮件不包含任务要求"),
        }

    task = Task(
        email_id=email.id,
        task_name=result["task_name"],
        deadline=result["deadline"],
        priority=result["priority"],
        status=result["status"],
        category=result["category"],
        confidence=result.get("confidence", 0.8),
        confidence_source=result.get("confidence_source", "rules"),
    )
    db.add(task)
    email.is_processed = 1
    db.commit()
    db.refresh(task)

    return {
        "extracted": True,
        "task": TaskOut.model_validate(task),
        "confidence": task.confidence,
        "low_confidence": task.confidence < 0.7,
    }


# -- 强制加入任务 --

@router.post("/api/emails/{email_id}/force-task")
def force_create_task(email_id: int, db: Session = Depends(get_db)):
    email = db.query(Email).get(email_id)
    if not email:
        raise HTTPException(404, "邮件不存在")

    existing = db.query(Task).filter(Task.email_id == email_id).first()
    if existing:
        return {"created": False, "task_id": existing.id, "message": "该邮件已有任务"}

    email_data = {
        "id": email.message_id or str(email.id),
        "message_id": email.message_id or str(email.id),
        "subject": email.subject,
        "sender": email.sender,
        "body": email.body,
        "received_at": email.received_at,
        "is_processed": bool(email.is_processed),
    }

    result = do_extract_task(email_data)
    if not result.get("should_create_task"):
        result = {
            "should_create_task": True,
            "task_name": email.subject[:40],
            "deadline": result.get("deadline", ""),
            "priority": "medium",
            "status": "pending",
            "category": "通用任务",
            "confidence": 0.5,
            "confidence_source": "manual",
        }

    task = Task(
        email_id=email.id,
        task_name=result["task_name"],
        deadline=result["deadline"],
        priority=result["priority"],
        status=result["status"],
        category=result["category"],
        confidence=result.get("confidence", 0.5),
        confidence_source="manual",
    )
    db.add(task)
    email.is_processed = 1
    db.commit()
    db.refresh(task)

    return {"created": True, "task": TaskOut.model_validate(task)}
