# Roadmap

## Phase 1: Project Initialization

Status: Completed

Completed:

- Project directory structure
- README and AGENTS documentation
- Requirements declaration
- JSON configuration system
- Provider interface and provider placeholders
- Service layer placeholders
- Central logging setup
- Startup entry point

## Phase 2: Desktop Floating Window

Status: Completed

Completed:

- PyQt6 main desktop window
- Frameless window
- Transparent background support
- Always-on-top behavior
- Mouse dragging
- Click event handling
- Character placeholder image at `assets/character/default.png`

## Phase 3: Chat System

Status: Completed

Completed:

- Text input in the desktop floating window
- Chat response display in the desktop floating window
- `ChatService` conversation boundary
- DeepSeek chat provider using OpenAI-compatible API style
- Centralized DeepSeek and Gemini API configuration in `config/settings.json`
- Safe no-key fallback returning `未配置 DeepSeek API Key`

## Phase 4: Desktop UX Enhancement

Status: Completed

Completed:

- Close button and minimize-to-tray behavior
- System tray menu: show, hide, settings, exit
- Window close event hides to tray by default
- Edge resizing and visible bottom-right resize grip
- Window state persistence in `config/window_state.json`
- Startup restoration of window position and size
- Character image resizes while keeping aspect ratio
- Chat layout refined into character, history, and input sections
- Scrollable chat history
- Multiline input with Enter to send and Shift+Enter for newline
- Settings dialog for DeepSeek API Key, Gemini API Key, and model names

## Phase 5: Screenshot Analysis + Gemini Vision

Status: Completed

Completed:

- `ScreenshotService` captures the current primary screen.
- Screenshots are saved to `cache/screenshots`.
- `VisionService` calls the configured vision provider.
- `GeminiProvider` analyzes screenshots when `gemini_api_key` is configured.
- Empty Gemini API Key returns `未配置 Gemini API Key` without crashing.
- Chat window includes a `截图分析` button near the input area.
- Screenshot analysis results appear in chat history.

## Phase 6: Edge-TTS Voice Replies

Status: Completed

Completed:

- `TextToSpeechService` generates MP3 voice files through Edge-TTS.
- Generated audio is saved to `cache/audio`.
- Generated audio is played automatically on Windows.
- Settings include `tts_enabled`, `tts_voice`, `tts_rate`, and `tts_volume`.
- Settings dialog exposes voice reply enablement, voice name, speaking rate, and volume.
- Chat replies are spoken only when `tts_enabled=true`.
- `测试语音` button plays a fixed test phrase.
- Missing `edge-tts` and generation/playback failures are handled without crashing.
- Errors are written through the logging system to `logs/error.log`.

Known issues:

- Real DeepSeek chat requires the user to fill `deepseek_api_key`.
- Real Gemini analysis requires the user to fill `gemini_api_key`.
- Voice playback depends on Windows audio output availability.
- Gemini and chat responses are not streamed.

Next phase:

- Stop after Phase 6. Do not enter Phase 7 automatically.
