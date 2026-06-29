from __future__ import annotations

import logging
from typing import Any


class StorageService:
    def __init__(self, settings: Any) -> None:
        self.settings = settings
        self.logger = logging.getLogger(__name__)

    def connect(self) -> None:
        raise NotImplementedError("SQLite storage is reserved for a future phase.")
