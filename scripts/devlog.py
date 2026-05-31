"""Daily development log manager.

Usage:
    python scripts/devlog.py add "完成事项描述"
    python scripts/devlog.py todo "待办事项描述"
    python scripts/devlog.py today   # 查看今日日志
    python scripts/devlog.py list    # 列出所有日志文件
"""

import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "devlog"


def _today_file():
    return LOG_DIR / f"{date.today().isoformat()}.md"


def _ensure_dir():
    LOG_DIR.mkdir(exist_ok=True)


def _read_today():
    f = _today_file()
    if f.exists():
        return f.read_text(encoding="utf-8")
    return ""


def _write_today(content):
    _ensure_dir()
    _today_file().write_text(content, encoding="utf-8")


def cmd_add(description):
    """Add a completed item to today's log."""
    existing = _read_today()
    today = date.today().isoformat()

    if not existing:
        existing = f"# 开发日志 {today}\n\n## 完成事项\n\n## 待办事项\n\n"

    # Insert before 待办事项 section
    if "## 待办事项" in existing:
        parts = existing.split("## 待办事项", 1)
        existing = parts[0].rstrip() + f"\n- [x] {description}\n\n## 待办事项" + parts[1]
    else:
        existing += f"\n- [x] {description}\n"

    _write_today(existing)
    print(f"[devlog] 已记录完成: {description}")


def cmd_todo(description):
    """Add a todo item to today's log."""
    existing = _read_today()
    today = date.today().isoformat()

    if not existing:
        existing = f"# 开发日志 {today}\n\n## 完成事项\n\n## 待办事项\n\n"

    existing += f"- [ ] {description}\n"
    _write_today(existing)
    print(f"[devlog] 已记录待办: {description}")


def cmd_today():
    """Print today's log."""
    content = _read_today()
    if content:
        print(content)
    else:
        print(f"今日 ({date.today()}) 暂无日志。")


def cmd_list():
    """List all log files."""
    _ensure_dir()
    files = sorted(LOG_DIR.glob("*.md"), reverse=True)
    if not files:
        print("暂无日志文件。")
        return
    for f in files:
        lines = f.read_text(encoding="utf-8").splitlines()
        first_done = next((l for l in lines if l.startswith("- [x]")), None)
        summary = first_done.replace("- [x] ", "")[:60] if first_done else "(无完成记录)"
        print(f"  {f.stem}  {summary}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    arg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    commands = {
        "add": lambda: cmd_add(arg),
        "todo": lambda: cmd_todo(arg),
        "today": cmd_today,
        "list": cmd_list,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"未知命令: {command}")
        print("可用命令: add, todo, today, list")
        sys.exit(1)
