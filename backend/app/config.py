from pathlib import Path
import os
import sys


def _app_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent


BASE_DIR = _app_root()
ENV_PATH = BASE_DIR / ".env"


def load_env_file(path=ENV_PATH):
    values = _read_env_values(path)
    for key, value in values.items():
        os.environ.setdefault(key, value)


def get_mail_config():
    load_env_file()
    return {
        "email": os.getenv("QQ_EMAIL", "").strip(),
        "auth_code": os.getenv("QQ_AUTH_CODE", "").strip(),
        "host": os.getenv("QQ_IMAP_HOST", "imap.qq.com").strip(),
        "port": int(os.getenv("QQ_IMAP_PORT", "993")),
        "lookback_days": int(os.getenv("MAIL_LOOKBACK_DAYS", "7")),
        "max_fetch": int(os.getenv("MAIL_MAX_FETCH", "10")),
        "initial_sync": os.getenv("MAIL_INITIAL_SYNC", "demo").strip().lower(),
    }


def get_llm_config():
    load_env_file()
    return {
        "mode": os.getenv("LLM_MODE", "rules").strip().lower(),
        "api_base": os.getenv("LLM_API_BASE", "https://api.openai.com/v1").strip().rstrip("/"),
        "api_key": os.getenv("LLM_API_KEY", "").strip(),
        "model": os.getenv("LLM_MODEL", "").strip(),
        "timeout": int(os.getenv("LLM_TIMEOUT_SECONDS", "5")),
        "allow_email_content": _as_bool(os.getenv("LLM_ALLOW_EMAIL_CONTENT", "false")),
    }


def save_mail_config(email, auth_code, lookback_days, max_fetch, initial_sync):
    current = get_mail_config()
    values = _read_env_values()
    values.update(
        {
            "QQ_EMAIL": email.strip(),
            "QQ_AUTH_CODE": auth_code.strip() or current["auth_code"],
            "QQ_IMAP_HOST": current["host"] or "imap.qq.com",
            "QQ_IMAP_PORT": str(current["port"] or 993),
            "MAIL_LOOKBACK_DAYS": str(int(lookback_days)),
            "MAIL_MAX_FETCH": str(int(max_fetch)),
            "MAIL_INITIAL_SYNC": initial_sync,
        }
    )
    _save_env_values(values)


def save_llm_config(mode, api_base, api_key, model, timeout, allow_email_content):
    current = get_llm_config()
    values = _read_env_values()
    values.update(
        {
            "LLM_MODE": mode,
            "LLM_API_BASE": api_base.strip().rstrip("/") or "https://api.openai.com/v1",
            "LLM_API_KEY": api_key.strip() or current["api_key"],
            "LLM_MODEL": model.strip(),
            "LLM_TIMEOUT_SECONDS": str(int(timeout)),
            "LLM_ALLOW_EMAIL_CONTENT": "true" if allow_email_content else "false",
        }
    )
    _save_env_values(values)


def validate_qq_mail_config(config):
    missing = []
    if not config["email"]:
        missing.append("QQ_EMAIL")
    if not config["auth_code"]:
        missing.append("QQ_AUTH_CODE")
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"缺少 QQ 邮箱配置：{joined}。请在设置里的用户管理中填写。")


def _read_env_values(path=ENV_PATH):
    if not path.exists():
        return {}
    values = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _save_env_values(values):
    ENV_PATH.write_text(_format_env(values), encoding="utf-8")
    for key, value in values.items():
        os.environ[key] = value


def _format_env(values):
    return "\n".join(f"{key}={value}" for key, value in values.items()) + "\n"


def _as_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}
