from enum import Enum


class Priority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Status(str, Enum):
    pending = "pending"
    processing = "processing"
    done = "done"


class Category(str, Enum):
    meeting = "会议通知"
    customer = "客户跟进"
    research = "科研协作"
    report = "报告提交"
    general = "通用任务"


class ConfidenceSource(str, Enum):
    rules = "rules"
    llm = "llm"
    hybrid = "hybrid"
