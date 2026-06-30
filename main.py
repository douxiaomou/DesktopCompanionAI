from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from config.logging_config import setup_logging
from config.settings import load_settings
from providers.deepseek.provider import DeepSeekProvider
from providers.gemini.provider import GeminiProvider
from services.audio.service import TextToSpeechService
from services.chat.service import ChatService
from services.screenshot.service import ScreenshotService
from services.speech_to_text.service import SpeechToTextService
from services.storage.service import StorageService
from services.vision.service import VisionService
from ui.main_window import MainWindow


PROJECT_NAME = "Desktop Companion AI"
PROJECT_VERSION = "0.1.0"


def build_providers(settings):
    providers = {
        "deepseek": DeepSeekProvider(settings=settings),
        "gemini": GeminiProvider(settings=settings),
    }
    return providers


def build_services(settings, providers):
    chat_provider = providers[settings.chat_provider]
    vision_provider = providers[settings.vision_provider]

    return {
        "screenshot": ScreenshotService(settings=settings),
        "vision": VisionService(provider=vision_provider, settings=settings),
        "speech_to_text": SpeechToTextService(settings=settings),
        "text_to_speech": TextToSpeechService(settings=settings),
        "storage": StorageService(settings=settings),
        "chat": ChatService(provider=chat_provider, settings=settings),
    }


def main() -> int:
    settings = load_settings()
    logger = setup_logging(settings.log_level)

    logger.info("Starting %s v%s", PROJECT_NAME, PROJECT_VERSION)
    logger.info("Configuration loaded: chat_provider=%s, vision_provider=%s", settings.chat_provider, settings.vision_provider)

    providers = build_providers(settings)
    services = build_services(settings, providers)

    logger.info("Providers registered: %s", ", ".join(sorted(providers.keys())))
    logger.info("Services registered: %s", ", ".join(sorted(services.keys())))
    logger.info("Phase 8 SQLite memory starting")

    app = QApplication(sys.argv)
    window = MainWindow(
        chat_service=services["chat"],
        screenshot_service=services["screenshot"],
        vision_service=services["vision"],
        tts_service=services["text_to_speech"],
        stt_service=services["speech_to_text"],
        storage_service=services["storage"],
        settings=settings,
        settings_reload_callback=load_settings,
    )
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
