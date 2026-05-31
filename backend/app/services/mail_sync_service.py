from datetime import datetime
from email import policy
from email.header import decode_header
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
import html
import imaplib
import re
from datetime import timedelta

from app.config import get_mail_config, validate_qq_mail_config
from app.data.sample_emails import SAMPLE_EMAILS


def sync_sample_emails(conn):
    """返回 (all_email_ids, new_email_ids)"""
    all_ids = []
    new_ids = []
    for email in SAMPLE_EMAILS:
        result = save_email(conn, email)
        all_ids.append(result["email_id"])
        if result["is_new"]:
            new_ids.append(result["email_id"])
    return all_ids, new_ids


def sync_qq_recent_emails(conn):
    """返回 (all_email_ids, new_email_ids)"""
    config = get_mail_config()
    validate_qq_mail_config(config)

    since_date = (datetime.now() - timedelta(days=config["lookback_days"])).strftime("%d-%b-%Y")
    all_ids = []
    new_ids = []

    with imaplib.IMAP4_SSL(config["host"], config["port"]) as client:
        client.login(config["email"], config["auth_code"])
        client.select("INBOX", readonly=True)
        status, data = client.search(None, "SINCE", since_date)
        if status != "OK":
            raise RuntimeError("QQ 邮箱搜索近期邮件失败。")

        mail_ids = data[0].split()
        batch = mail_ids[-config["max_fetch"] :]
        if not batch:
            return [], []

        # 批量 fetch：一次 IMAP 请求拉多封
        fetch_set = ",".join(m.decode("utf-8", errors="ignore") for m in reversed(batch))
        status, msg_data_list = client.fetch(fetch_set, "(BODY.PEEK[])")
        if status != "OK":
            raise RuntimeError("QQ 邮箱批量获取邮件失败。")

        for item in msg_data_list:
            if not isinstance(item, tuple):
                continue
            raw_message = _first_message_bytes([item])
            if not raw_message:
                continue
            mail_id = item[0].decode("utf-8", errors="ignore").split()[0] if isinstance(item[0], bytes) else str(item[0]).split()[0]
            email_data = _parse_email(raw_message, fallback_id=mail_id)
            result = save_email(conn, email_data)
            all_ids.append(result["email_id"])
            if result["is_new"]:
                new_ids.append(result["email_id"])

    return all_ids, new_ids


def list_emails(conn):
    rows = conn.execute(
        """
        SELECT
            emails.*,
            tasks.id AS task_id,
            tasks.task_name,
            tasks.status AS task_status
        FROM emails
        LEFT JOIN tasks ON tasks.email_id = emails.id
        WHERE
            emails.message_id = ''
            OR emails.id = (
                SELECT MIN(e2.id)
                FROM emails e2
                WHERE e2.message_id = emails.message_id
            )
        ORDER BY emails.id DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]


def save_email(conn, email):
    """保存邮件，返回 {"email_id": int, "is_new": bool}"""
    message_id = email.get("id") or email.get("message_id") or ""
    if message_id:
        existing = conn.execute(
            "SELECT id FROM emails WHERE message_id = ? ORDER BY id LIMIT 1",
            (message_id,),
        ).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE emails
                SET subject = ?, sender = ?, body = ?
                WHERE id = ?
                """,
                (email["subject"], email["sender"], email["body"], existing["id"]),
            )
            return {"email_id": existing["id"], "is_new": False}

    cursor = conn.execute(
        """
        INSERT INTO emails (message_id, subject, sender, body, received_at, is_processed)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            message_id,
            email["subject"],
            email["sender"],
            email["body"],
            email.get("received_at") or datetime.now().isoformat(timespec="seconds"),
            0,
        ),
    )
    return {"email_id": cursor.lastrowid, "is_new": True}


def mark_email_processed(conn, email_id):
    conn.execute("UPDATE emails SET is_processed = 1 WHERE id = ?", (email_id,))


def _first_message_bytes(msg_data):
    for item in msg_data:
        if isinstance(item, tuple) and item[1]:
            return item[1]
    return None


def _parse_email(raw_message, fallback_id):
    message = BytesParser(policy=policy.default).parsebytes(raw_message)
    message_id = (message.get("Message-ID") or fallback_id).strip()
    subject = _decode_mime_header(message.get("Subject") or "(无主题)")
    sender = _decode_mime_header(message.get("From") or "(未知发件人)")
    received_at = _parse_message_date(message.get("Date"))
    body = _extract_body(message)

    return {
        "id": message_id,
        "message_id": message_id,
        "subject": subject,
        "sender": sender,
        "body": body,
        "received_at": received_at,
    }


def _decode_mime_header(value):
    fragments = []
    for fragment, charset in decode_header(value):
        if isinstance(fragment, bytes):
            fragments.append(fragment.decode(charset or "utf-8", errors="replace"))
        else:
            fragments.append(fragment)
    return "".join(fragments).strip()


def _parse_message_date(value):
    if not value:
        return datetime.now().isoformat(timespec="seconds")
    try:
        return parsedate_to_datetime(value).isoformat(timespec="seconds")
    except (TypeError, ValueError):
        return datetime.now().isoformat(timespec="seconds")


def _extract_body(message):
    if message.is_multipart():
        plain_parts = []
        html_parts = []
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                continue
            content_type = part.get_content_type()
            if content_type == "text/plain":
                plain_parts.append(_get_part_text(part))
            elif content_type == "text/html":
                html_parts.append(_html_to_text(_get_part_text(part)))
        text = "\n".join(part for part in plain_parts if part).strip()
        if text:
            return text
        return "\n".join(part for part in html_parts if part).strip()

    if message.get_content_type() == "text/html":
        return _html_to_text(_get_part_text(message))
    return _get_part_text(message)


def _get_part_text(part):
    try:
        return part.get_content().strip()
    except LookupError:
        payload = part.get_payload(decode=True) or b""
        return payload.decode("utf-8", errors="replace").strip()


def _html_to_text(value):
    value = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value)
    value = re.sub(r"(?i)<br\s*/?>", "\n", value)
    value = re.sub(r"(?i)</p>", "\n", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"[ \t\r\f\v]+", " ", value).strip()
