import json
import re

import requests

from app.ai.prompt_engine import build_task_extraction_prompt
from app.ai.task_schema import normalize_task_payload

# 复用 HTTP 连接，避免每次请求重建 TCP+TLS
_session = requests.Session()


def extract_task_with_llm(email, config):
    if not config["api_key"] and not _is_local_api(config["api_base"]):
        raise ValueError("未配置 LLM API Key")
    if not config["model"]:
        raise ValueError("未配置 LLM 模型名称")
    if not config["allow_email_content"]:
        raise ValueError("未允许将邮件内容发送给外部模型")

    url = f"{config['api_base']}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if config["api_key"]:
        headers["Authorization"] = f"Bearer {config['api_key']}"
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": "你只输出合法 JSON。"},
            {"role": "user", "content": build_task_extraction_prompt(email)},
        ],
        "temperature": 0.2,
        "max_tokens": 1000,
        "response_format": {"type": "json_object"},
    }
    if "deepseek" in config["api_base"]:
        payload["thinking"] = {"type": "disabled"}
    response = _session.post(url, headers=headers, json=payload, timeout=config["timeout"])
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    if not content or not content.strip():
        raise ValueError("DeepSeek API 返回了空内容，请稍后重试或调整提示词。")
    return normalize_task_payload(_parse_json_object(content))


def _parse_json_object(content):
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _is_local_api(api_base):
    return "localhost" in api_base or "127.0.0.1" in api_base
