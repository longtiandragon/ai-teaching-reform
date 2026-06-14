"""AI 模型配置管理 — 读写 .env 文件中的 DeepSeek 配置。"""

from __future__ import annotations

import os
from pathlib import Path

from backend.app.config import ROOT_DIR

ENV_PATH = ROOT_DIR / ".env"

# 预置模型配置
MODEL_PRESETS = [
    {
        "name": "DeepSeek V3",
        "baseUrl": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "description": "DeepSeek V3，通用对话模型",
    },
    {
        "name": "DeepSeek R1",
        "baseUrl": "https://api.deepseek.com",
        "model": "deepseek-reasoner",
        "description": "DeepSeek R1，深度推理模型",
    },
    {
        "name": "通义千问 Plus",
        "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "description": "阿里云通义千问 Plus",
    },
    {
        "name": "智谱 GLM-4",
        "baseUrl": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
        "description": "智谱 GLM-4 Flash",
    },
]


def _read_env() -> dict[str, str]:
    """读取 .env 文件为字典。"""
    config: dict[str, str] = {}
    if not ENV_PATH.exists():
        return config
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            config[key.strip()] = value.strip()
    return config


def _write_env(config: dict[str, str]) -> None:
    """将字典写回 .env 文件，保留注释和格式。"""
    lines: list[str] = []
    existing_keys: set[str] = set()

    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                lines.append(line)
                continue
            if "=" in stripped:
                key, _, _ = stripped.partition("=")
                key = key.strip()
                existing_keys.add(key)
                if key in config:
                    lines.append(f"{key}={config[key]}")
                else:
                    lines.append(line)
            else:
                lines.append(line)

    # 追加新增的键
    for key, value in config.items():
        if key not in existing_keys:
            lines.append(f"{key}={value}")

    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_ai_config() -> dict:
    """获取当前 AI 配置（隐藏 API Key）。"""
    env = _read_env()
    api_key = env.get("DEEPSEEK_API_KEY", "")
    return {
        "apiKey": api_key,
        "apiKeyMasked": _mask_key(api_key),
        "baseUrl": env.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        "model": env.get("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        "live": env.get("DEEPSEEK_LIVE", "false").lower() == "true",
        "timeout": int(env.get("DEEPSEEK_TIMEOUT_SECONDS", "15")),
    }


def update_ai_config(
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    live: bool | None = None,
    timeout: int | None = None,
) -> dict:
    """更新 AI 配置。"""
    env = _read_env()

    if api_key is not None:
        env["DEEPSEEK_API_KEY"] = api_key
    if base_url is not None:
        env["DEEPSEEK_BASE_URL"] = base_url
    if model is not None:
        env["DEEPSEEK_MODEL"] = model
    if live is not None:
        env["DEEPSEEK_LIVE"] = "true" if live else "false"
    if timeout is not None:
        env["DEEPSEEK_TIMEOUT_SECONDS"] = str(timeout)

    _write_env(env)
    return get_ai_config()


def get_presets() -> list[dict]:
    """获取预置模型列表。"""
    return MODEL_PRESETS


def _mask_key(key: str) -> str:
    """掩码 API Key。"""
    if not key:
        return ""
    if len(key) <= 8:
        return "••••••••"
    return key[:4] + "•" * (len(key) - 8) + key[-4:]
