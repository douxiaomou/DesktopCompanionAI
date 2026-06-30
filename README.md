# Desktop Companion AI

Desktop Companion AI is a Windows 11 desktop AI companion prototype.

V0.1 MVP validates these core capabilities step by step:

- Desktop floating window
- Text chat
- Screenshot capture
- Gemini screenshot analysis
- Edge-TTS voice replies
- Microphone speech input
- SQLite chat memory

## Current Status

Phase 8 is complete. The app starts a PyQt6 desktop floating chat window with chat, screenshot analysis, TTS voice replies, speech input, and SQLite-backed recent chat memory.

Run with:

```powershell
cd D:\DesktopCompanionAI
python main.py
```

## Configuration

Runtime configuration is stored in `config/settings.json`.

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
  "tts_volume": "+0%",
  "stt_enabled": false,
  "stt_model": "base",
  "stt_language": "zh",
  "stt_device": "cpu",
  "memory_enabled": true
}
```

User-filled values:

- `deepseek_api_key`: DeepSeek API Key for chat.
- `gemini_api_key`: Gemini API Key for screenshot analysis.
- `tts_enabled`: Enables AI reply voice playback.
- `stt_enabled`: Enables microphone speech input.
- `memory_enabled`: Enables saving and loading text chat memory. Default: `true`.

No API keys, audio bytes, screenshot image bytes, or recording contents are stored in SQLite.

## SQLite Memory

Database location:

```text
D:\DesktopCompanionAI\data\companion.db
```

Table:

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

Behavior:

- User messages are saved when the user clicks `Send`.
- AI chat replies are saved as `assistant`.
- Screenshot analysis results are saved as `assistant`.
- Speech recognition only fills the input box; it is saved only after the user sends it.
- On startup, the latest 20 messages are loaded into Chat history.
- If `memory_enabled=false`, messages are not saved and history is not loaded.

Memory can be managed from Settings:

- Current message count
- Clear chat memory
- Memory enabled/disabled state

## Runtime Files

Runtime files are ignored by Git:

- `cache/audio`
- `cache/recordings`
- `cache/screenshots`
- `data`
- `logs`
- `config/window_state.json`

## Architecture

Business services must not call model APIs directly. Model access goes through provider classes. Storage access goes through `StorageService`.

Current memory flow:

```text
MainWindow
-> StorageService
-> SQLite data/companion.db
-> messages table
```
