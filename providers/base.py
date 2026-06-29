from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseProvider(ABC):
    """Shared interface for all model providers."""

    def __init__(self, settings: Any) -> None:
        self.settings = settings

    @abstractmethod
    def chat(self, message: str, context: dict[str, Any] | None = None) -> str:
        """Send a chat message and return provider text."""

    @abstractmethod
    def vision(self, image_path: str | Path, prompt: str | None = None) -> str:
        """Analyze an image and return provider text."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text from a prompt."""
