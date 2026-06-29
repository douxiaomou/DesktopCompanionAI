# Repository State

## Current Version

Desktop Companion AI V0.1 Phase 6

## Completed

- Initialized project under `D:\DesktopCompanionAI`.
- Added configuration loading from `config/settings.json`.
- Added logging to console, `logs/app.log`, and `logs/error.log`.
- Added provider architecture with `BaseProvider`, `DeepSeekProvider`, and `GeminiProvider`.
- Implemented `ChatService` with conversation history.
- Implemented DeepSeek chat provider with API Key fallback behavior.
- Added PyQt6 desktop companion chat window.
- Added close, minimize, tray, settings, and resize UX.
- Added visible bottom-right resize grip.
- Added window state persistence in `config/window_state.json`.
- Implemented `ScreenshotService` for primary-screen screenshots.
- Implemented `VisionService` as the service boundary for vision analysis.
- Implemented Gemini screenshot analysis provider.
- Added screenshot analysis button to the main chat window.
- Implemented `TextToSpeechService` for Edge-TTS voice generation and playback.
- Added `测试语音` button to the main chat window.
- Added optional automatic voice reading after AI replies when `tts_enabled=true`.
- Added voice configuration fields to the settings dialog.

## User Configuration Required

All user-editable API and voice settings are centralized in `config/settings.json`.

- `deepseek_api_key`: DeepSeek API Key for chat.
- `deepseek_model`: DeepSeek chat model name.
- `deepseek_base_url`: DeepSeek OpenAI-compatible base URL.
- `gemini_api_key`: Gemini API Key for screenshot analysis.
- `gemini_model`: Gemini vision model name.
- `tts_enabled`: Enables automatic AI reply voice playback when `true`.
- `tts_voice`: Edge-TTS voice name.
- `tts_rate`: Edge-TTS speaking rate.
- `tts_volume`: Edge-TTS volume.

Window position and size are stored in `config/window_state.json`.

## Storage Locations

Screenshots are saved under:

```text
D:\DesktopCompanionAI\cache\screenshots
```

Only the latest 10 PNG screenshots are kept.

Generated voice files are saved under:

```text
D:\DesktopCompanionAI\cache\audio
```

Only the latest 20 MP3 files created by the TTS service are kept.

## Not Completed

- Faster-Whisper microphone input
- SQLite persistence
- Streaming chat or vision responses

## Known Issues

- Empty `deepseek_api_key` intentionally returns `未配置 DeepSeek API Key`.
- Empty `gemini_api_key` intentionally returns `未配置 Gemini API Key`.
- Tray availability depends on the Windows desktop shell being available.
- Edge-TTS playback requires the `edge-tts` package and a working Windows audio output device.

## Next Step

Stop after Phase 6. Do not enter Phase 7 automatically.
