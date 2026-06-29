from __future__ import annotations

import logging
from typing import Any

from providers.base import BaseProvider


class ChatService:
    """Application chat boundary. UI code talks to this service, not to providers."""

    def __init__(self, provider: BaseProvider, settings: Any) -> None:
        self.provider = provider
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.history: list[dict[str, str]] = []

    def chat(self, message: str, context: dict[str, Any] | None = None) -> str:
        clean_message = message.strip()
        if not clean_message:
            return "请输入聊天内容"

        self.logger.info("Chat request received")
        merged_context = {"history": self.history}
        if context:
            merged_context.update(context)

        reply = self.provider.chat(message=clean_message, context=merged_context)
        self.history.append({"role": "user", "content": clean_message})
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def clear_history(self) -> None:
        self.history.clear()
        self.logger.info("Chat history cleared")
