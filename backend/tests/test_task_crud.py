"""任务 CRUD API 测试"""
import pytest
from app.models import Email, Task


def seed_email(db, message_id="test-01", subject="测试邮件", sender="test@test.com"):
    """辅助：插入一封测试邮件"""
    email = Email(
        message_id=message_id,
        subject=subject,
        sender=sender,
        body="这是一封测试邮件内容，请明天前提交周报。",
        received_at="2026-06-01T10:00:00",
        is_processed=0,
    )
    db.add(email)
    db.flush()
    return email


class TestListTasks:
    def test_empty_list(self, client, db):
        res = client.get("/api/tasks")
        assert res.status_code == 200
        assert res.json() == []

    def test_list_with_tasks(self, client, db):
        email = seed_email(db)
        task = Task(email_id=email.id, task_name="测试任务", deadline="2026-06-15",
                    priority="high", status="pending", category="通用任务",
                    confidence=0.9, confidence_source="rules")
        db.add(task)
        db.commit()

        res = client.get("/api/tasks")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["task_name"] == "测试任务"
        assert data[0]["priority"] == "high"


class TestCreateTask:
    def test_create_success(self, client, db):
        payload = {
            "task_name": "新建任务",
            "deadline": "2026-06-20",
            "priority": "medium",
            "status": "pending",
            "category": "通用任务",
        }
        res = client.post("/api/tasks", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["task_name"] == "新建任务"
        assert data["confidence"] == 1.0
        assert data["confidence_source"] == "manual"


class TestUpdateTask:
    def test_update_not_found(self, client):
        res = client.put("/api/tasks/999", json={"task_name": "不存在的任务"})
        assert res.status_code == 404

    def test_update_success(self, client, db):
        seed_email(db)
        task = Task(email_id=1, task_name="旧名称", deadline="2026-06-01",
                    priority="low", status="pending", category="通用任务",
                    confidence=0.5, confidence_source="rules")
        db.add(task)
        db.commit()

        res = client.put(f"/api/tasks/{task.id}", json={
            "task_name": "新名称",
            "priority": "high",
        })
        assert res.status_code == 200
        assert res.json()["task_name"] == "新名称"
        assert res.json()["priority"] == "high"


class TestDeleteTask:
    def test_delete_not_found(self, client):
        res = client.delete("/api/tasks/999")
        assert res.status_code == 404

    def test_delete_success(self, client, db):
        seed_email(db)
        task = Task(email_id=1, task_name="待删除", deadline="2026-06-01",
                    priority="low", status="pending", category="通用任务",
                    confidence=0.5, confidence_source="rules")
        db.add(task)
        db.commit()

        res = client.delete(f"/api/tasks/{task.id}")
        assert res.status_code == 204


class TestStatusUpdate:
    def test_update_status(self, client, db):
        seed_email(db)
        task = Task(email_id=1, task_name="状态测试", deadline="2026-06-01",
                    priority="medium", status="pending", category="通用任务",
                    confidence=0.8, confidence_source="rules")
        db.add(task)
        db.commit()

        res = client.patch(f"/api/tasks/{task.id}/status", json={"status": "done"})
        assert res.status_code == 200
        assert res.json()["status"] == "done"


class TestStats:
    def test_stats_empty(self, client):
        res = client.get("/api/tasks/stats")
        assert res.status_code == 200
        assert res.json() == {"total": 0, "high_priority": 0, "active": 0, "done": 0}

    def test_stats_with_data(self, client, db):
        seed_email(db, message_id="s1")
        seed_email(db, message_id="s2")
        tasks = [
            Task(email_id=1, task_name="A", deadline="2026-06-01", priority="high", status="pending", category="X", confidence=1.0, confidence_source="rules"),
            Task(email_id=1, task_name="B", deadline="2026-06-02", priority="medium", status="done", category="X", confidence=1.0, confidence_source="rules"),
            Task(email_id=2, task_name="C", deadline="2026-06-03", priority="high", status="processing", category="X", confidence=1.0, confidence_source="rules"),
        ]
        for t in tasks:
            db.add(t)
        db.commit()

        res = client.get("/api/tasks/stats")
        assert res.status_code == 200
        stats = res.json()
        assert stats["total"] == 3
        assert stats["high_priority"] == 2
        assert stats["active"] == 2  # pending + processing
        assert stats["done"] == 1
