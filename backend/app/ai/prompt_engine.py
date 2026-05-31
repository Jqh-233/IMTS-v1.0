import json
from datetime import datetime


def build_task_extraction_prompt(email):
    now = datetime.now().astimezone()
    today = now.date().isoformat()
    weekday = now.strftime("%A")
    schema = {
        "should_create_task": "boolean",
        "reason": "string，判断依据",
        "task_name": "string，20字以内；无任务时为空",
        "deadline": "string，YYYY-MM-DD",
        "priority": "high | medium | low",
        "category": "会议通知 | 客户跟进 | 科研协作 | 报告提交 | 通用任务",
        "confidence": "number，0-1，表示判断的确定性",
    }
    return "\n".join(
        [
            "你是邮件任务提取助手。严格输出 JSON，不要 Markdown，不要代码块。",

            # ── 核心判断标准 ──
            "【任务的三要素】同时满足以下三条才创建任务：",
            "1. 邮件要求收件人执行某个具体行动",
            "2. 该行动有明确或可推断的完成时间",
            "3. 行动属于工作/学习职责范畴，不是纯粹的娱乐消费",

            "【不创建任务的情况】",
            "- 纯信息通知，没有要求收件人做任何事",
            "- 广告、营销、订阅、验证码、自动回复",
            "- 交易凭证：收据、充值、退款、购买确认",
            "- 邮件中提到的行动是针对其他人的，收件人只是被抄送或转发",

            # ── few-shot 示例 ──
            "【示例1-应创建任务】发件人：主管，主题：请明天下午前提交本周工作周报",
            "正文：请明天下午18:00前提交本周工作周报，重点说明项目进展、风险和下周计划。",
            "正确输出：should_create_task=true, task_name=提交本周工作周报, deadline=明天, priority=medium, confidence=0.95",
            "",
            "【示例2-不应创建任务】发件人：安全中心，主题：登录验证码",
            "正文：你的验证码是384921，5分钟内有效。若非本人操作，请忽略。",
            "正确输出：should_create_task=false, reason=验证码通知无需进入任务看板",
            "",

            # ── 日期 ──
            f"当前日期：{today}（{weekday}）。",
            "今天/明天/后天/本周X/下周X/月底 需换算为 YYYY-MM-DD。",
            "截止日期早于今天则 should_create_task=false。",
            "无明确日期时推断合理值。",

            # ── 优先级 ──
            "high: 今天/明天截止，或客户故障/影响业务的问题",
            "medium: 本周/下周截止，常规工作任务",
            "low: 无紧迫性的一般事项",

            # ── 置信度 ──
            "0.90+: 行动、对象、日期都明确",
            "0.75-0.89: 基本明确有小量推断",
            "0.60-0.74: 存在歧义需用户确认",
            "<0.60: 不创建任务",

            # ── 输出 ──
            json.dumps(schema, ensure_ascii=False, indent=2),
            "",
            f"发件人：{email.get('sender', '')}",
            f"主题：{email.get('subject', '')}",
            f"正文：{email.get('body', '')[:4000]}",
        ]
    )
