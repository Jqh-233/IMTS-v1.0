"""配置读写 API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import get_llm_config, get_mail_config, save_llm_config, save_mail_config

router = APIRouter(prefix="/api/config", tags=["config"])


class MailConfigBody(BaseModel):
    email: str = ""
    auth_code: str = ""
    lookback_days: int = Field(7, ge=1, le=90)
    max_fetch: int = Field(10, ge=1, le=50)
    initial_sync: str = "demo"


class LLMConfigBody(BaseModel):
    mode: str = Field("hybrid", pattern="^(rules|llm|hybrid)$")
    api_base: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = ""
    timeout: int = Field(10, ge=5, le=120)
    allow_email_content: bool = True


@router.get("")
def get_config():
    mail = get_mail_config()
    llm = get_llm_config()
    return {
        "mail": {
            "email": mail["email"],
            "auth_code": _mask(mail["auth_code"]),
            "host": mail["host"],
            "port": mail["port"],
            "lookback_days": mail["lookback_days"],
            "max_fetch": mail["max_fetch"],
            "initial_sync": mail["initial_sync"],
        },
        "llm": {
            "mode": llm["mode"],
            "api_base": llm["api_base"],
            "api_key": _mask(llm["api_key"]),
            "model": llm["model"],
            "timeout": llm["timeout"],
            "allow_email_content": llm["allow_email_content"],
        },
    }


@router.put("/mail")
def update_mail_config(body: MailConfigBody):
    save_mail_config(body.email, body.auth_code, body.lookback_days, body.max_fetch, body.initial_sync)
    return {"status": "ok"}


@router.put("/llm")
def update_llm_config(body: LLMConfigBody):
    save_llm_config(body.mode, body.api_base, body.api_key, body.model, body.timeout, body.allow_email_content)
    return {"status": "ok"}


@router.post("/llm/test")
def test_llm_connection():
    """测试 LLM 连接，返回模型名称或错误"""
    import requests as req
    config = get_llm_config()

    if not config["api_key"]:
        raise HTTPException(400, "未配置 API Key")

    try:
        r = req.post(
            f"{config['api_base']}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['api_key']}",
            },
            json={
                "model": config["model"],
                "messages": [
                    {"role": "user", "content": "请回复：连接成功"}
                ],
                "max_tokens": 20,
                "temperature": 0,
            },
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        reply = data["choices"][0]["message"]["content"].strip()
        return {"ok": True, "model": config["model"], "reply": reply}
    except req.Timeout:
        raise HTTPException(504, "连接超时，请检查网络或 API 地址")
    except req.HTTPError as e:
        detail = f"API 返回错误 ({e.response.status_code})"
        try:
            detail += f": {e.response.json()}"
        except ValueError:
            detail += f": {e.response.text[:200]}"
        raise HTTPException(502, detail)
    except req.ConnectionError:
        raise HTTPException(502, "无法连接到 API 服务器，请检查 API 地址")


def _mask(value: str) -> str:
    if not value or len(value) <= 6:
        return "***"
    return value[:3] + "***" + value[-3:]
