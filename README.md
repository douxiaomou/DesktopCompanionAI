# Desktop Companion AI

Desktop Companion AI is a Windows 11 desktop AI companion prototype.

V0.1 MVP validates these core capabilities step by step:

- Desktop floating window
- Text chat
- Screenshot capture
- Gemini screenshot analysis
- Edge-TTS voice replies
- Future speech recognition

## Current Status

Phase 6 is complete. The app starts a PyQt6 desktop floating chat window with:

- Chat input and DeepSeek chat provider fallback
- Tray show/hide
- Settings dialog
- Visible resize grip and edge resizing
- Screenshot analysis button
- Test voice button
- Optional AI reply voice playback through Edge-TTS

Run with:

```powershell
cd D:\DesktopCompanionAI
python main.py
```

## Requirements

- Windows 11
- Python 3.11+
- VSCode recommended

Install dependencies with:

```powershell
pip install -r requirements.txt
```

## Configuration

Runtime model and voice configuration is stored in `config/settings.json`.

```json
{
  "chat_provider": "deepseek",
  "vision_provider": "gemini",
  "log_level": "INFO",
  "deepseek_api_key": "",
  "deepseek_model": "deepseek-chat",
  "deepseek_base_url": "https://api.deepseek.com",
  "gemini_api_key": "",
  "gemini_model": "gemini-2.5-flash",
  "tts_enabled": false,
  "tts_voice": "zh-CN-XiaoxiaoNeural",
  "tts_rate": "+0%",
  "tts_volume": "+0%"
}
```

```text
========================
USER CONFIG REQUIRED
====================
```

Fill these values later:

- `deepseek_api_key`: DeepSeek API Key for chat.
- `deepseek_model`: DeepSeek model name. Default: `deepseek-chat`.
- `deepseek_base_url`: DeepSeek OpenAI-compatible API base URL.
- `gemini_api_key`: Gemini API Key for screenshot analysis.
- `gemini_model`: Gemini vision model name. Default: `gemini-2.5-flash`.
- `tts_enabled`: Set to `true` to read AI replies aloud. Default: `false`.
- `tts_voice`: Edge-TTS voice name. Default: `zh-CN-XiaoxiaoNeural`.
- `tts_rate`: Edge-TTS speaking rate. Default: `+0%`.
- `tts_volume`: Edge-TTS volume. Default: `+0%`.

If `deepseek_api_key` is empty, chat returns:

```text
未配置 DeepSeek API Key
```

If `gemini_api_key` is empty, screenshot analysis returns:

```text
未配置 Gemini API Key
```

If `edge-tts` is not installed, voice playback returns:

```text
未安装 edge-tts，请先安装依赖
```

## Screenshot Analysis

Click the `截图分析` button in the chat window.

Flow:

```text
Screenshot button
-> ScreenshotService captures the primary screen
-> Image is saved to cache/screenshots
-> VisionService calls GeminiProvider
-> Gemini result or no-key fallback appears in chat history
```

Screenshot files are saved under:

```text
D:\DesktopCompanionAI\cache\screenshots
```

## Voice Replies

Click the `测试语音` button to play:

```text
你好，我是你的桌面陪伴助手。
```

When `tts_enabled` is `true`, AI chat replies are spoken after the text appears in the chat window. When it is `false`, replies are text-only.

Generated audio files are saved under:

```text
D:\DesktopCompanionAI\cache\audio
```

## Desktop UX

- `-` hides the assistant to the system tray.
- `x` exits the program.
- Closing the window hides it to the tray by default.
- The tray menu supports show, hide, settings, and exit.
- Window edges and corners can be dragged to resize.
- The bottom-right resize grip is visible.
- Settings can be edited from the tray menu.

## Architecture

Business services must not call model APIs directly. Model access must go through provider classes implementing the shared provider interface.

Current chat and voice flow:

```text
MainWindow
-> ChatService
-> DeepSeekProvider
-> MainWindow chat display
-> TextToSpeechService when tts_enabled=true
-> Edge-TTS generated audio
```

Current screenshot analysis flow:

```text
MainWindow
-> ScreenshotService
-> VisionService
-> GeminiProvider
-> MainWindow chat display
```
