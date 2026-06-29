from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from providers.base import BaseProvider


class DeepSeekProvider(BaseProvider):
    """DeepSeek chat provider using the OpenAI-compatible DeepSeek API."""

    def __init__(self, settings: Any) -> None:
        super().__init__(settings=settings)
        self.logger = logging.getLogger(__name__)

    def chat(self, message: str, context: dict[str, Any] | None = None) -> str:
        if not self.settings.deepseek_api_key:
            self.logger.warning("DeepSeek API key is empty. Configure deepseek_api_key in config/settings.json.")
            return "未配置 DeepSeek API Key"

        try:
            from openai import OpenAI
        except ImportError:
            self.logger.exception("The openai package is required for DeepSeekProvider.")
            return "DeepSeek 依赖未安装：openai"

        messages = self._build_messages(message=message, context=context)

        try:
            client = OpenAI(
                api_key=self.settings.deepseek_api_key,
                base_url=self.settings.deepseek_base_url,
            )
            response = client.chat.completions.create(
                model=self.settings.deepseek_model,
                messages=messages,
            )
            content = response.choices[0].message.content
            if not content:
                self.logger.warning("DeepSeek returned an empty response.")
                return "DeepSeek 返回了空回复"
            return content.strip()
        except Exception as exc:
            self.logger.exception("DeepSeek chat request failed")
            return f"DeepSeek 调用失败：{exc}"

    def vision(self, image_path: str | Path, prompt: str | None = None) -> str:
        raise NotImplementedError("DeepSeek vision is not implemented in Phase 3.")

    def generate(self, prompt: str, **kwargs: Any) -> str:
        return self.chat(message=prompt, context=kwargs or None)

    def _build_messages(self, message: str, context: dict[str, Any] | None = None) -> list[dict[str, str]]:
        system_prompt = "You are Desktop Companion AI, a concise and helpful desktop assistant."
        messages = [{"role": "system", "content": system_prompt}]

        history = (context or {}).get("history", [])
        for item in history:
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": str(content)})

        messages.append({"role": "user", "content": message})
        return messages
