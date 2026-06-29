# Repository State

## Current Version

Desktop Companion AI V0.1 Phase 7

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
- Added voice reply configuration fields to the settings dialog.
- Implemented `SpeechToTextService` for microphone recording and speech recognition.
- Added `语音输入` button to the main chat window.
- Added recording state switching between `语音输入` and `停止录音`.
- Added speech recognition configuration fields to the settings dialog.

## User Configuration Required

All user-editable API, voice reply, and speech input settings are centralized in `config/settings.json`.

- `deepseek_api_key`: DeepSeek API Key for chat.
- `deepseek_model`: DeepSeek chat model name.
- `deepseek_base_url`: DeepSeek OpenAI-compatible base URL.
- `gemini_api_key`: Gemini API Key for screenshot analysis.
- `gemini_model`: Gemini vision model name.
- `tts_enabled`: Enables automatic AI reply voice playback when `true`.
- `tts_voice`: Edge-TTS voice name.
- `tts_rate`: Edge-TTS speaking rate.
- `tts_volume`: Edge-TTS volume.
- `stt_enabled`: Enables microphone speech input when `true`.
- `stt_model`: STT model name.
- `stt_language`: STT language code.
- `stt_device`: STT device, `cpu` or `cuda`.

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

Recordings are saved under:

```text
D:\DesktopCompanionAI\cache\recordings
```

Only the latest 20 WAV recordings are kept.

## Not Completed

- Automatic sending after speech recognition
- SQLite persistence
- Streaming chat, vision, or speech recognition responses

## Known Issues

- Empty `deepseek_api_key` intentionally returns `未配置 DeepSeek API Key`.
- Empty `gemini_api_key` intentionally returns `未配置 Gemini API Key`.
- Empty or disabled `stt_enabled` intentionally returns `语音识别未启用`.
- Tray availability depends on the Windows desktop shell being available.
- Edge-TTS playback requires the `edge-tts` package and a working Windows audio output device.
- Speech input requires a working microphone and recognition dependencies.

## Next Step

Stop after Phase 7. Do not enter Phase 8 automatically.
