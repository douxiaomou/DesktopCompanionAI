from __future__ import annotations

import logging
from typing import Any


class SpeechToTextService:
    def __init__(self, settings: Any) -> None:
        self.settings = settings
        self.logger = logging.getLogger(__name__)

    def listen(self) -> str:
        raise NotImplementedError("Speech recognition is not implemented in Phase 1.")
