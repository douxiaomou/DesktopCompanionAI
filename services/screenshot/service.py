from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCREENSHOT_DIR = PROJECT_ROOT / "cache" / "screenshots"
MAX_SCREENSHOTS = 10


class ScreenshotService:
    """Capture and store screenshots for later vision analysis."""

    def __init__(self, settings: Any) -> None:
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    def capture_primary_screen(self) -> Path:
        """Capture the current primary screen and return the saved PNG path."""
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        screenshot_path = SCREENSHOT_DIR / f"screenshot_{datetime.now():%Y%m%d_%H%M%S_%f}.png"

        try:
            self._capture_with_mss(screenshot_path)
        except Exception:
            self.logger.exception("mss screenshot capture failed; trying Pillow ImageGrab fallback")
            self._capture_with_pillow(screenshot_path)

        self._cleanup_old_screenshots()
        self.logger.info("Screenshot saved: %s", screenshot_path)
        return screenshot_path

    def latest_screenshot(self) -> Path | None:
        screenshots = sorted(SCREENSHOT_DIR.glob("*.png"), key=lambda path: path.stat().st_mtime, reverse=True)
        return screenshots[0] if screenshots else None

    def start(self) -> None:
        raise NotImplementedError("Continuous screenshot capture is not implemented in Phase 5.")

    def stop(self) -> None:
        raise NotImplementedError("Continuous screenshot capture is not implemented in Phase 5.")

    def _capture_with_mss(self, screenshot_path: Path) -> None:
        import mss
        from PIL import Image

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            raw = sct.grab(monitor)
            image = Image.frombytes("RGB", raw.size, raw.rgb)
            image.save(screenshot_path)

    def _capture_with_pillow(self, screenshot_path: Path) -> None:
        from PIL import ImageGrab

        image = ImageGrab.grab()
        image.save(screenshot_path)

    def _cleanup_old_screenshots(self) -> None:
        screenshots = sorted(SCREENSHOT_DIR.glob("*.png"), key=lambda path: path.stat().st_mtime, reverse=True)
        for old_path in screenshots[MAX_SCREENSHOTS:]:
            try:
                old_path.unlink()
            except OSError:
                self.logger.exception("Failed to remove old screenshot: %s", old_path)
