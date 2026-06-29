from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from providers.base import BaseProvider


DEFAULT_SCREEN_PROMPT = (
    "请用简洁中文描述这张桌面截图中的主要内容。"
    "重点说明用户正在使用什么应用、正在查看什么内容、是否有明显需要注意的信息。"
)


class VisionService:
    """Application vision boundary. UI code talks to this service, not provider SDKs."""

    def __init__(self, provider: BaseProvider, settings: Any) -> None:
        self.provider = provider
        self.settings = settings
        self.logger = logging.getLogger(__name__)

    def analyze(self, image_path: str | Path, prompt: str | None = None) -> str:
        self.logger.info("Vision analysis request received: %s", image_path)
        return self.provider.vision(image_path=image_path, prompt=prompt or DEFAULT_SCREEN_PROMPT)
