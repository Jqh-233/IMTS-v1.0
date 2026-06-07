from datetime import datetime
from email import policy
from email.header import decode_header
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
import html
import imaplib
import re
from datetime import timedelta

from sqlalchemy.orm import Session

from app.config import get_mail_config, validate_qq_mail_config
from app.models import Email, Task

# ── 演示邮件数据（15 封，内联避免跨包依赖） ──

SAMPLE_EMAILS = [
    # -- 明确任务 (8 封) --
    {"id":"demo-01","name":"周报提交","sender":"主管 manager@example.com","subject":"请明天下午前提交本周工作周报","body":"请明天下午18:00前提交本周工作周报，重点说明项目进展、风险和下周计划。","expected_should_create":True},
    {"id":"demo-02","name":"客户故障","sender":"客户 support@example.com","subject":"系统登录异常需要今天处理","body":"客户反馈系统登录一直失败，麻烦今天下班前定位原因并回复处理结果。","expected_should_create":True},
    {"id":"demo-03","name":"培训报名","sender":"培训中心 training@example.com","subject":"下周三前完成数据安全培训报名","body":"请在下周三前填写报名表并确认是否参加线下考试。","expected_should_create":True},
    {"id":"demo-04","name":"项目例会","sender":"项目秘书 secretary@example.com","subject":"本周五项目例会材料准备","body":"请本周五15:00参加项目例会，并提前准备各自模块的进展说明。","expected_should_create":True},
    {"id":"demo-05","name":"合同确认","sender":"法务 legal@example.com","subject":"合同条款确认","body":"请明天上午前确认附件合同中的付款条款，如有问题请直接批注后回复。","expected_should_create":True},
    {"id":"demo-06","name":"客户回访","sender":"销售总监 sales@example.com","subject":"重点客户回访安排","body":"麻烦尽快联系A公司客户，确认试用反馈并更新CRM记录。","expected_should_create":True},
    {"id":"demo-07","name":"论文修改","sender":"导师 li@lab.edu","subject":"论文审稿意见修改","body":"请在下周内完成第二轮审稿意见修改，重点补充实验对照组和消融分析。","expected_should_create":True},
    {"id":"demo-08","name":"账单确认","sender":"财务 finance@example.com","subject":"账单已生成请确认付款信息","body":"本月账单已生成，请今天确认付款信息是否正确。如有问题请直接回复。","expected_should_create":True},
    # -- 明确非任务 (5 封) --
    {"id":"demo-09","name":"验证码","sender":"安全中心 security@example.com","subject":"登录验证码","body":"你的验证码是384921，5分钟内有效。若非本人操作请忽略。","expected_should_create":False},
    {"id":"demo-10","name":"系统维护","sender":"IT运维 it@example.com","subject":"系统维护通知","body":"系统将在周六凌晨进行维护，期间可能短暂不可用。本邮件仅为通知无需处理。","expected_should_create":False},
    {"id":"demo-11","name":"游戏活动","sender":"游戏活动 promo@example.com","subject":"限时活动登录领取补给箱","body":"后天前登录游戏可领取补给箱。该奖励为限时活动福利。","expected_should_create":False},
    {"id":"demo-12","name":"自动回复","sender":"auto-reply@example.com","subject":"自动回复我已收到你的邮件","body":"我目前正在休假，回来后会尽快处理。本邮件为自动回复。","expected_should_create":False},
    {"id":"demo-13","name":"广告促销","sender":"优惠 newsletter@shop.example.com","subject":"限时优惠会员专享折扣","body":"本周商城促销活动开启，点击链接领取优惠券。本邮件为广告订阅内容。","expected_should_create":False},
    # -- 陷阱 (2 封，规则易误判) --
    {"id":"demo-14","name":"转发他人任务","sender":"同事 colleague@example.com","subject":"Fwd: 会议纪要摘录","body":"纪要里提到市场部需要在明天前提交活动预算。这个事项由市场部负责，我只是转发给你了解背景。","expected_should_create":False,"expected_rule_may_fail":True},
    {"id":"demo-15","name":"条件安全提醒","sender":"安全中心 security@example.com","subject":"账户安全提醒","body":"如果不是你本人操作请尽快修改密码；如果是你本人操作可以忽略本提醒。","expected_should_create":False,"expected_rule_may_fail":True},
]


def sync_sample_emails(db: Session):
    """同步演示邮件，返回新导入的邮件 ID 列表"""
    new_ids = []
    for email in SAMPLE_EMAILS:
        result = save_email(db, email)
        if result["is_new"]:
            new_ids.append(result["email_id"])
    return new_ids


def sync_qq_recent_emails(db: Session):
    """同步 QQ 近期邮件，返回新导入的邮件 ID 列表"""
    config = get_mail_config()
    validate_qq_mail_config(config)

    since_date = (datetime.now() - timedelta(days=config["lookback_days"])).strftime("%d-%b-%Y")
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
            return []

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
            result = save_email(db, email_data)
            if result["is_new"]:
                new_ids.append(result["email_id"])

    return new_ids



def save_email(db: Session, email: dict):
    """保存邮件（通过 message_id 去重），返回 {"email_id": int, "is_new": bool}"""
    message_id = email.get("id") or email.get("message_id") or ""

    # 去重：message_id 非空时查找已有记录
    if message_id:
        existing = db.query(Email).filter(Email.message_id == message_id).first()
        if existing:
            existing.subject = email["subject"]
            existing.sender = email["sender"]
            existing.body = email["body"]
            db.flush()
            return {"email_id": existing.id, "is_new": False}

    new_email = Email(
        message_id=message_id,
        subject=email["subject"],
        sender=email["sender"],
        body=email["body"],
        received_at=email.get("received_at") or datetime.now().isoformat(timespec="seconds"),
        is_processed=0,
    )
    db.add(new_email)
    db.flush()
    return {"email_id": new_email.id, "is_new": True}


def mark_email_processed(db: Session, email_id: int):
    email = db.query(Email).get(email_id)
    if email:
        email.is_processed = 1
        db.flush()


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
