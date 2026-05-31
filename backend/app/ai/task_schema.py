from datetime import date, timedelta


VALID_PRIORITIES = {"high", "medium", "low"}
VALID_CATEGORIES = {"会议通知", "客户跟进", "科研协作", "报告提交", "通用任务"}


def normalize_task_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("LLM 输出不是 JSON 对象")

    should_create = bool(payload.get("should_create_task", False))
    if not should_create:
        return {
            "should_create_task": False,
            "skip_reason": str(payload.get("reason") or "模型判断该邮件无需进入任务看板"),
        }

    task_name = str(payload.get("task_name") or "").strip()
    if not task_name:
        raise ValueError("LLM 输出缺少 task_name")

    deadline = normalize_deadline(payload.get("deadline"))
    if date.fromisoformat(deadline) < date.today():
        return {
            "should_create_task": False,
            "skip_reason": "任务截止日期已过期，未加入任务看板",
        }
    priority = str(payload.get("priority") or "medium").strip().lower()
    if priority not in VALID_PRIORITIES:
        priority = "medium"

    category = str(payload.get("category") or "通用任务").strip()
    if category not in VALID_CATEGORIES:
        category = "通用任务"

    confidence = payload.get("confidence", 0.8)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.8
    confidence = min(max(confidence, 0.0), 1.0)

    return {
        "should_create_task": True,
        "decision_reason": str(payload.get("reason") or "模型判断该邮件包含行动要求"),
        "task_name": task_name[:40],
        "deadline": deadline,
        "priority": priority,
        "status": "pending",
        "category": category,
        "confidence": confidence,
        "confidence_source": "llm",
    }


def normalize_deadline(value):
    text = str(value or "").strip()
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        return (date.today() + timedelta(days=3)).isoformat()
