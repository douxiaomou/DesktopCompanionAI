# Desktop Companion AI

Desktop Companion AI is a Windows 11 desktop AI companion prototype.

V0.1 MVP currently includes:

- Desktop floating window
- Text chat
- Screenshot capture and Gemini analysis
- Edge-TTS voice replies
- Microphone speech input
- SQLite chat memory
- Character status and lightweight interaction feedback

## Current Status

Phase 9 is complete. The app keeps the existing PyQt6 floating window and adds small character-experience improvements without Live2D or a complex animation engine.

Run with:

```powershell
cd D:\DesktopCompanionAI
python main.py
```

## Character UI

The character area now shows:

- Current state: `空闲`, `正在听你说话`, `正在思考`, `正在说话`, or `出错了`
- Placeholder note: `当前使用默认占位角色`
- Recent AI reply bubble above Chat history

State linkage:

- Sending a message: `thinking`
- AI reply received: `idle`, or `speaking` when TTS starts
- TTS playback finished: `idle`
- Recording voice input: `listening`
- Screenshot analysis: `thinking`
- Recoverable failures: short `error` state

The project still uses:

```text
D:\DesktopCompanionAI\assets\character\default.png
```

## Configuration

Runtime configuration remains in `config/settings.json`. Phase 9 does not add, remove, or rename configuration fields and does not configure real API keys.

Important user-filled values:

- `deepseek_api_key`
- `gemini_api_key`
- `tts_enabled`
- `stt_enabled`
- `memory_enabled`

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

## Runtime Files

Runtime files are ignored by Git:

- `cache/audio`
- `cache/recordings`
- `cache/screenshots`
- `data`
- `logs`
- `config/window_state.json`

## Architecture

Business services do not call model APIs directly. Model access goes through providers. Storage access goes through `StorageService`. Phase 9 only changes UI state linkage in `MainWindow`.
