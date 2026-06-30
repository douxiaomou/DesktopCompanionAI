from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.json"
SUPPORTED_CHAT_PROVIDERS = {"deepseek"}
SUPPORTED_VISION_PROVIDERS = {"gemini"}


@dataclass(frozen=True)
class Settings:
    chat_provider: str = "deepseek"
    vision_provider: str = "gemini"
    log_level: str = "INFO"

    # ========================
    # USER CONFIG REQUIRED
    # ====================
    # Fill these values in config/settings.json when the matching API keys are available.
    # DeepSeek powers chat. Gemini powers screenshot analysis.
    # Edge-TTS powers voice replies. Faster-Whisper/Whisper powers speech input.
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    tts_enabled: bool = False
    tts_voice: str = "zh-CN-XiaoxiaoNeural"
    tts_rate: str = "+0%"
    tts_volume: str = "+0%"
    stt_enabled: bool = False
    stt_model: str = "base"
    stt_language: str = "zh"
    stt_device: str = "cpu"
    memory_enabled: bool = True


def load_settings(path: Path = SETTINGS_PATH) -> Settings:
    if not path.exists():
        raise FileNotFoundError(f"Settings file not found: {path}")

    with path.open("r", encoding="utf-8-sig") as file:
        raw: dict[str, Any] = json.load(file)

    settings = Settings(
        chat_provider=str(raw.get("chat_provider", Settings.chat_provider)).lower(),
        vision_provider=str(raw.get("vision_provider", Settings.vision_provider)).lower(),
        log_level=str(raw.get("log_level", Settings.log_level)).upper(),
        deepseek_api_key=str(raw.get("deepseek_api_key", Settings.deepseek_api_key)).strip(),
        deepseek_model=str(raw.get("deepseek_model", Settings.deepseek_model)).strip(),
        deepseek_base_url=str(raw.get("deepseek_base_url", Settings.deepseek_base_url)).strip(),
        gemini_api_key=str(raw.get("gemini_api_key", Settings.gemini_api_key)).strip(),
        gemini_model=str(raw.get("gemini_model", Settings.gemini_model)).strip(),
        tts_enabled=_as_bool(raw.get("tts_enabled", Settings.tts_enabled)),
        tts_voice=str(raw.get("tts_voice", Settings.tts_voice)).strip(),
        tts_rate=str(raw.get("tts_rate", Settings.tts_rate)).strip(),
        tts_volume=str(raw.get("tts_volume", Settings.tts_volume)).strip(),
        stt_enabled=_as_bool(raw.get("stt_enabled", Settings.stt_enabled)),
        stt_model=str(raw.get("stt_model", Settings.stt_model)).strip(),
        stt_language=str(raw.get("stt_language", Settings.stt_language)).strip(),
        stt_device=str(raw.get("stt_device", Settings.stt_device)).strip().lower(),
        memory_enabled=_as_bool(raw.get("memory_enabled", Settings.memory_enabled)),
    )
    validate_settings(settings)
    return settings


def update_settings_file(updates: dict[str, Any], path: Path = SETTINGS_PATH) -> None:
    if path.exists():
        with path.open("r", encoding="utf-8-sig") as file:
            raw: dict[str, Any] = json.load(file)
    else:
        raw = {}

    raw.update(updates)
    with path.open("w", encoding="utf-8") as file:
        json.dump(raw, file, ensure_ascii=False, indent=2)
        file.write("\n")


def validate_settings(settings: Settings) -> None:
    if settings.chat_provider not in SUPPORTED_CHAT_PROVIDERS:
        raise ValueError(f"Unsupported chat provider: {settings.chat_provider}")
    if settings.vision_provider not in SUPPORTED_VISION_PROVIDERS:
        raise ValueError(f"Unsupported vision provider: {settings.vision_provider}")
    if not settings.deepseek_model:
        raise ValueError("deepseek_model must not be empty")
    if not settings.deepseek_base_url:
        raise ValueError("deepseek_base_url must not be empty")
    if not settings.gemini_model:
        raise ValueError("gemini_model must not be empty")
    if not settings.tts_voice:
        raise ValueError("tts_voice must not be empty")
    if not settings.tts_rate:
        raise ValueError("tts_rate must not be empty")
    if not settings.tts_volume:
        raise ValueError("tts_volume must not be empty")
    if not settings.stt_model:
        raise ValueError("stt_model must not be empty")
    if not settings.stt_language:
        raise ValueError("stt_language must not be empty")
    if settings.stt_device not in {"cpu", "cuda"}:
        raise ValueError("stt_device must be cpu or cuda")


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)
