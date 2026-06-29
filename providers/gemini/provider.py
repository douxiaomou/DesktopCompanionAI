from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """Gemini vision provider."""

    def __init__(self, settings: Any) -> None:
        super().__init__(settings=settings)
        self.logger = logging.getLogger(__name__)

    def chat(self, message: str, context: dict[str, Any] | None = None) -> str:
        raise NotImplementedError("Gemini chat is not implemented in Phase 5.")

    def vision(self, image_path: str | Path, prompt: str | None = None) -> str:
        if not self.settings.gemini_api_key:
            self.logger.warning("Gemini API key is empty. Configure gemini_api_key in config/settings.json.")
            return "未配置 Gemini API Key"

        path = Path(image_path)
        if not path.exists():
            self.logger.error("Vision image not found: %s", path)
            return f"截图文件不存在: {path}"

        try:
            from google import genai
            from PIL import Image
        except ImportError as exc:
            self.logger.exception("Gemini vision dependencies are missing")
            return f"Gemini Vision 依赖未安装: {exc}"

        try:
            client = genai.Client(api_key=self.settings.gemini_api_key)
            image = Image.open(path)
            response = client.models.generate_content(
                model=self.settings.gemini_model,
                contents=[prompt or "Describe this screenshot.", image],
            )
            text = getattr(response, "text", None)
            if not text:
                self.logger.warning("Gemini returned an empty vision response")
                return "Gemini 返回了空结果"
            return text.strip()
        except Exception as exc:
            self.logger.exception("Gemini vision request failed")
            return f"Gemini Vision 调用失败: {exc}"

    def generate(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError("Gemini text generation is not implemented in Phase 5.")
