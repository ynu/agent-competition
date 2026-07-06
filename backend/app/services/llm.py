"""
LLM 内容检测服务
"""
import json
import re
import httpx
from typing import Dict, Any
from sqlalchemy.orm import Session


def get_setting(db: Session, key: str, default: str = "") -> str:
    """获取配置"""
    from app.models.setting import Setting
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        return setting.value or default
    return default


def check_llm_enabled(db: Session) -> bool:
    """检查LLM是否启用"""
    enabled = get_setting(db, "llm_enabled", "false")
    return enabled.lower() in ("true", "1", "yes")


def get_llm_config(db: Session) -> Dict[str, str]:
    """获取LLM配置"""
    return {
        "base_url": get_setting(db, "llm_base_url", "https://api.openai.com/v1"),
        "api_key": get_setting(db, "llm_api_key", ""),
        "model": get_setting(db, "llm_model", "gpt-4o-mini"),
        "prompt": get_setting(db, "llm_prompt", ""),
    }


def format_prompt(prompt_template: str, work_data: Dict[str, Any]) -> str:
    """填充prompt占位符"""
    if not prompt_template:
        return ""

    placeholders = {
        "{name}": work_data.get("name", ""),
        "{description}": work_data.get("description", ""),
        "{agent_url}": work_data.get("agent_url", ""),
        "{agent_editor_url}": work_data.get("agent_editor_url", ""),
        "{team_name}": work_data.get("team_name", ""),
        "{theme_name}": work_data.get("theme_name", ""),
    }

    result = prompt_template
    for placeholder, value in placeholders.items():
        result = result.replace(placeholder, str(value) if value else "")

    return result


def _validate_llm_config(db: Session, work_data: Dict[str, Any]) -> tuple[bool, Dict[str, Any] | str]:
    """验证LLM配置并返回prompt或错误信息"""
    if not check_llm_enabled(db):
        return False, {"result": "skip", "reason": "LLM检测未启用"}

    config = get_llm_config(db)

    if not config["api_key"]:
        return False, {"result": "error", "reason": "LLM API key未配置"}

    if not config["prompt"]:
        return False, {"result": "error", "reason": "LLM prompt未配置"}

    return True, format_prompt(config["prompt"], work_data)


def _process_llm_response(content: str) -> Dict[str, Any]:
    """处理LLM响应结果"""
    result = parse_llm_response(content)

    # 限制reason长度
    if "reason" in result:
        result["reason"] = truncate_detail(result["reason"])

    # 验证result值
    if result.get("result") not in ("pass", "suspicious", "fail", "error"):
        result["result"] = "suspicious"
        result["reason"] = truncate_detail(f"LLM返回异常结果: {content[:200]}")

    return result


async def call_llm(
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    timeout: float = 30.0
) -> str:
    """调用LLM API"""
    if not api_key:
        raise ValueError("API key is required")

    # 确保base_url以/结尾
    if not base_url.endswith("/"):
        base_url += "/"

    url = f"{base_url}chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

        return content


def parse_llm_response(content: str) -> Dict[str, Any]:
    """解析LLM返回的JSON结果（支持markdown代码块）"""
    # 尝试提取markdown代码块中的JSON
    json_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
    match = re.search(json_pattern, content, re.DOTALL)

    if match:
        json_str = match.group(1)
    else:
        # 尝试直接解析整个响应
        json_str = content.strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # 尝试提取JSON对象
        json_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    return {"result": "error", "reason": "无法解析LLM响应"}


def truncate_detail(detail: str, max_length: int = 4096) -> str:
    """限制detail长度最大4KB"""
    if len(detail) <= max_length:
        return detail
    return detail[:max_length] + "...(truncated)"


async def detect_work_content(db: Session, work_data: Dict[str, Any]) -> Dict[str, Any]:
    """检测作品内容"""
    valid, result_or_prompt = _validate_llm_config(db, work_data)
    if not valid:
        return result_or_prompt

    config = get_llm_config(db)

    try:
        content = await call_llm(
            base_url=config["base_url"],
            api_key=config["api_key"],
            model=config["model"],
            prompt=result_or_prompt
        )
        return _process_llm_response(content)

    except httpx.HTTPError as e:
        return {"result": "error", "reason": f"LLM API调用失败: {str(e)}"}
    except Exception as e:
        return {"result": "error", "reason": f"LLM检测异常: {str(e)}"}


def detect_work_content_sync(db: Session, work_data: Dict[str, Any]) -> Dict[str, Any]:
    """同步版本的内容检测（使用httpx同步客户端）"""
    valid, result_or_prompt = _validate_llm_config(db, work_data)
    if not valid:
        return result_or_prompt

    config = get_llm_config(db)

    try:
        with httpx.Client(timeout=30.0) as client:
            base_url = config["base_url"]
            if not base_url.endswith("/"):
                base_url += "/"

            url = f"{base_url}chat/completions"

            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": config["model"],
                "messages": [{"role": "user", "content": result_or_prompt}],
                "temperature": 0.3,
                "max_tokens": 500,
            }

            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            return _process_llm_response(content)

    except httpx.HTTPError as e:
        return {"result": "error", "reason": f"LLM API调用失败: {str(e)}"}
    except Exception as e:
        return {"result": "error", "reason": f"LLM检测异常: {str(e)}"}