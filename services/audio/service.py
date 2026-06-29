from __future__ import annotations

import asyncio
import logging
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIO_DIR = PROJECT_ROOT / "cache" / "audio"
MAX_AUDIO_FILES = 20
MISSING_EDGE_TTS_MESSAGE = "未安装 edge-tts，请先安装依赖"


@dataclass(frozen=True)
class SpeechResult:
    success: bool
    message: str
    audio_path: Path | None = None


class TextToSpeechService:
    """Generate and play voice replies with Edge-TTS."""

    def __init__(self, settings: Any) -> None:
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    def speak(self, text: str) -> SpeechResult:
        clean_text = text.strip()
        if not clean_text:
            return SpeechResult(success=False, message="没有可朗读的文本")

        try:
            audio_path = self.generate(clean_text)
            self.play(audio_path)
            return SpeechResult(success=True, message="语音播放完成", audio_path=audio_path)
        except ImportError:
            self.logger.exception(MISSING_EDGE_TTS_MESSAGE)
            return SpeechResult(success=False, message=MISSING_EDGE_TTS_MESSAGE)
        except Exception as exc:
            self.logger.exception("Text-to-speech failed")
            return SpeechResult(success=False, message=f"语音生成或播放失败: {exc}")

    def generate(self, text: str) -> Path:
        try:
            import edge_tts
        except ImportError:
            raise

        AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        audio_path = AUDIO_DIR / f"tts_{datetime.now():%Y%m%d_%H%M%S_%f}.mp3"

        async def _save() -> None:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.settings.tts_voice,
                rate=self.settings.tts_rate,
                volume=self.settings.tts_volume,
            )
            await communicate.save(str(audio_path))

        asyncio.run(_save())
        self._cleanup_old_audio()
        self.logger.info("TTS audio saved: %s", audio_path)
        return audio_path

    def play(self, audio_path: Path) -> None:
        if sys.platform != "win32":
            self.logger.warning("Audio playback is currently implemented for Windows only: %s", audio_path)
            return

        script = (
            "Add-Type -AssemblyName PresentationCore; "
            "$player = New-Object System.Windows.Media.MediaPlayer; "
            f"$player.Open([Uri]'{audio_path.resolve().as_uri()}'); "
            "while (-not $player.NaturalDuration.HasTimeSpan) { Start-Sleep -Milliseconds 100 }; "
            "$player.Play(); "
            "$duration = [int]$player.NaturalDuration.TimeSpan.TotalMilliseconds + 500; "
            "Start-Sleep -Milliseconds $duration; "
            "$player.Close();"
        )
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            timeout=60,
            creationflags=creationflags,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or "Windows audio playback failed")

    def _cleanup_old_audio(self) -> None:
        audio_files = sorted(AUDIO_DIR.glob("*.mp3"), key=lambda path: path.stat().st_mtime, reverse=True)
        for old_path in audio_files[MAX_AUDIO_FILES:]:
            try:
                old_path.unlink()
            except OSError:
                self.logger.exception("Failed to remove old audio file: %s", old_path)
