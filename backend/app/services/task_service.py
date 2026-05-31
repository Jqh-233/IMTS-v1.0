from app.ai.task_extractor import extract_task
from app.data.database import connect
from app.services.mail_sync_service import (
    list_emails,
    mark_email_processed,
    sync_qq_recent_emails,
    sync_sample_emails,
)


def list_tasks(db_path):
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
                tasks.*,
                emails.sender,
                emails.subject,
                emails.body
            FROM tasks
            LEFT JOIN emails ON emails.id = tasks.email_id
            ORDER BY
                CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
                deadline ASC,
                tasks.id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def list_raw_emails(db_path):
    with connect(db_path) as conn:
        return list_emails(conn)


def sync_demo_and_auto_extract(db_path):
    created = 0
    with connect(db_path) as conn:
        email_ids = sync_sample_emails(conn)
        created = _extract_new_tasks(conn, email_ids)
    return created


def sync_qq_and_auto_extract(db_path):
    with connect(db_path) as conn:
        email_ids = sync_qq_recent_emails(conn)
        return _extract_new_tasks(conn, email_ids)


def extract_email_by_id(db_path, email_id):
    with connect(db_path) as conn:
        existing = _get_task_by_email(conn, email_id)
        if existing:
            return dict(existing)
        email = _get_email(conn, email_id)
        task = extract_task(email, force=True)
        task_id = _insert_task(conn, email_id, task)
        mark_email_processed(conn, email_id)
        task["id"] = task_id
        task["email_id"] = email_id
        return task


def update_status(db_path, task_id, status):
    with connect(db_path) as conn:
        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))


def update_task_details(db_path, task_id, task_name, deadline, priority, category, status):
    with connect(db_path) as conn:
        conn.execute(
            """
            UPDATE tasks
            SET task_name = ?, deadline = ?, priority = ?, category = ?, status = ?
            WHERE id = ?
            """,
            (task_name, deadline, priority, category, status, task_id),
        )


def delete_task(db_path, task_id):
    with connect(db_path) as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


def clear_tasks(db_path):
    with connect(db_path) as conn:
        conn.execute("DELETE FROM tasks")
        conn.execute("DELETE FROM emails")


def _get_email(conn, email_id):
    row = conn.execute(
        "SELECT id, message_id, sender, subject, body, is_processed FROM emails WHERE id = ?",
        (email_id,),
    ).fetchone()
    if not row:
        raise ValueError(f"Email not found: {email_id}")
    return dict(row)


def _task_exists_for_email(conn, email_id):
    return _get_task_by_email(conn, email_id) is not None


def _get_task_by_email(conn, email_id):
    return conn.execute(
        "SELECT * FROM tasks WHERE email_id = ? ORDER BY id DESC LIMIT 1",
        (email_id,),
    ).fetchone()


def _insert_task(conn, email_id, task):
    columns = [
        "email_id",
        "task_name",
        "deadline",
        "priority",
        "status",
        "category",
        "confidence",
        "confidence_source",
    ]
    values = [
        email_id,
        task["task_name"],
        task["deadline"],
        task["priority"],
        task["status"],
        task["category"],
        task.get("confidence", 0.0),
        task.get("confidence_source", "rules"),
    ]

    columns.append("created_at")
    placeholders = ", ".join("?" for _ in values)
    sql = f"""
        INSERT INTO tasks ({", ".join(columns)})
        VALUES ({placeholders}, datetime('now', 'localtime'))
    """
    cursor = conn.execute(sql, values)
    task_id = cursor.lastrowid
    return task_id


def _extract_new_tasks(conn, email_ids):
    created = 0
    for email_id in email_ids:
        email = _get_email(conn, email_id)
        if not _task_exists_for_email(conn, email_id) and not email["is_processed"]:
            task = extract_task(email)
            if not task.get("should_create_task"):
                mark_email_processed(conn, email_id)
                continue
            _insert_task(conn, email_id, task)
            mark_email_processed(conn, email_id)
            created += 1
    return created
