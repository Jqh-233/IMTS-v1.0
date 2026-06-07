import re
from datetime import date, datetime, timedelta

from app.ai.llm_client import extract_task_with_llm
from app.ai.prompt_engine import build_task_extraction_prompt
from app.config import get_llm_config
from app.logging_config import get_logger

logger = get_logger(__name__)


ACTION_PATTERN = r"提交|完成|确认|回复|处理|修改|发送|发来|参加|准备|补充|审批|整理|提供|更新|安排|联系|跟进|上传|填写|报名"
DEADLINE_PATTERN = r"今天|明天|后天|本周|下周|周[一二三四五六日天]|截止|之前|前|月底|尽快|\d{1,2}月\d{1,2}日?"
NEGATIVE_DEADLINE_PATTERN = r"没有明确截止|无明确截止|没有截止|无截止|没有明确时间|无明确时间"
STRONG_NON_TASK_PATTERN = r"广告|促销|优惠|订阅|newsletter|验证码|自动回复|仅为通知|无需回复|不用回复|不需要回复|无需处理|不用处理|Steam|交易收据|购买收据|钱包充值|退款申请|购买已退款|登录操作|激活产品|社区市场|愿望单|领取.*奖励|领取.*补给箱|折扣"
WEAK_NON_TASK_PATTERN = r"系统通知|登录提醒|账单已生成"


def extract_task(email, force=False):
    config = get_llm_config()
    mode = config["mode"]

    if mode in {"llm", "hybrid"}:
        try:
            task = extract_task_with_llm(email, config)
            task["confidence_source"] = "llm"
            if force and not task.get("should_create_task"):
                return extract_task_by_rules(email, force=True)
            task["debug_prompt"] = build_task_extraction_prompt(email)
            return task
        except Exception as exc:
            if mode == "llm":
                raise
            logger.warning("LLM 提取失败，降级到规则引擎: %s", exc)
            fallback = extract_task_by_rules(email, force=force)
            fallback["llm_error"] = str(exc)
            return fallback

    return extract_task_by_rules(email, force=force)


def extract_task_by_rules(email, force=False):
    decision = should_create_task(email)
    if not force and not decision["should_create_task"]:
        return {
            "should_create_task": False,
            "skip_reason": decision["reason"],
            "debug_prompt": build_task_extraction_prompt(email),
        }

    text = build_email_text(email)
    deadline = infer_deadline(text)
    if not force and _is_overdue(deadline):
        return {
            "should_create_task": False,
            "skip_reason": "任务截止日期已过期，未加入任务看板",
            "debug_prompt": build_task_extraction_prompt(email),
        }
    priority = infer_priority(text)

    return {
        "should_create_task": True,
        "decision_reason": decision["reason"] if not force else "用户手动加入任务看板",
        "task_name": infer_task_name(email["subject"], email["body"]),
        "deadline": deadline,
        "priority": priority,
        "status": "pending",
        "category": infer_category(text),
        "confidence": 0.0,
        "confidence_source": "rules",
        "debug_prompt": build_task_extraction_prompt(email),
    }


def should_create_task(email):
    text = build_email_text(email)
    has_action = re.search(ACTION_PATTERN, text) is not None
    has_deadline = re.search(DEADLINE_PATTERN, text) is not None and re.search(NEGATIVE_DEADLINE_PATTERN, text) is None
    has_request = re.search(r"请|麻烦|需要|务必|请于|请在|烦请", text) is not None
    has_strong_non_task = re.search(STRONG_NON_TASK_PATTERN, text, flags=re.IGNORECASE) is not None
    has_weak_non_task = re.search(WEAK_NON_TASK_PATTERN, text, flags=re.IGNORECASE) is not None

    if has_strong_non_task:
        return {"should_create_task": False, "reason": "疑似通知、广告或无需行动的邮件"}
    if has_weak_non_task and not (has_action and (has_deadline or has_request)):
        return {"should_create_task": False, "reason": "疑似通知、广告或无需行动的邮件"}

    if has_action and (has_deadline or has_request):
        return {"should_create_task": True, "reason": "邮件包含明确行动要求"}
    if has_deadline and has_request:
        return {"should_create_task": True, "reason": "邮件包含请求语气和时间约束"}
    return {"should_create_task": False, "reason": "未识别到明确行动要求"}


def build_email_text(email):
    return f"{email.get('subject', '')}\n{email.get('body', '')}"


def _is_overdue(deadline):
    try:
        return date.fromisoformat(deadline) < date.today()
    except ValueError:
        return False


def infer_deadline(text):
    today = datetime.now().date()
    relative_days = {
        "今天": 0,
        "明天": 1,
        "后天": 2,
    }
    for label, days in relative_days.items():
        if label in text:
            return (today + timedelta(days=days)).isoformat()

    if "月底" in text:
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        return (next_month - timedelta(days=1)).isoformat()

    next_weekday_match = re.search(r"下周([一二三四五六日天])", text)
    if next_weekday_match:
        week_map = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6, "天": 6}
        target = week_map[next_weekday_match.group(1)]
        return (today + timedelta(days=7 + target - today.weekday())).isoformat()

    month_day = re.search(r"(\d{1,2})月(\d{1,2})日?", text)
    if month_day:
        deadline = today.replace(month=int(month_day.group(1)), day=int(month_day.group(2)))
        if (today - deadline).days > 180:
            deadline = deadline.replace(year=deadline.year + 1)
        return deadline.isoformat()

    weekday_match = re.search(r"(?:本周|周)([一二三四五六日天])", text)
    if weekday_match:
        week_map = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6, "天": 6}
        target = week_map[weekday_match.group(1)]
        return (today + timedelta(days=(target - today.weekday()) % 7 or 7)).isoformat()

    return (today + timedelta(days=3)).isoformat()


def infer_priority(text):
    if re.search(r"紧急|今天|明天|逾期|务必|优先级.*高|高优先|下班前|中午前|无法登录|登录异常|故障|投诉|影响.*使用", text):
        return "high"
    if re.search(r"尽快|客户|本周|下周|周|会议|确认|提交|截止|审批|报名|跟进", text):
        return "medium"
    return "low"


def infer_category(text):
    if re.search(r"会议|例会|参会|参加会议", text):
        return "会议通知"
    if re.search(r"客户|报价|售后|跟进", text):
        return "客户跟进"
    if re.search(r"论文|实验|审稿|科研", text):
        return "科研协作"
    if re.search(r"报告|审批|提交|整理", text):
        return "报告提交"
    return "通用任务"


def infer_task_name(subject, body):
    text = f"{subject}。{body}"
    patterns = [
        rf"(?:{ACTION_PATTERN})[^。；，,\n]{{2,28}}",
        r"请[^。；，,\n]{0,8}[^。；，,\n]{4,28}",
        r"麻烦[^。；，,\n]{0,8}[^。；，,\n]{4,28}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).removeprefix("请").removeprefix("麻烦").strip()[:28]
    return subject[:28]
