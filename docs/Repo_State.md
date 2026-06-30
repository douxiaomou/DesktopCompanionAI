# Repository State

## Current Version

Desktop Companion AI V0.1 Phase 8

## Completed

- Provider/service architecture.
- PyQt6 floating desktop window.
- Phase 4.2 resize and tray UX.
- DeepSeek chat provider with no-key fallback.
- Gemini screenshot analysis with no-key fallback.
- Edge-TTS voice reply service and test voice button.
- Microphone speech input MVP.
- SQLite chat memory MVP.

## SQLite Memory

Database:

```text
D:\DesktopCompanionAI\data\companion.db
```

Table:

```sql
messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  created_at TEXT NOT NULL
)
```

Saved content:

- User text messages after Send.
- Assistant chat replies.
- Assistant screenshot analysis results.

Not saved:

- API keys.
- Audio file contents.
- Screenshot image contents.
- Recording file contents.

## User Configuration Required

All user-editable settings are centralized in `config/settings.json`.

- `deepseek_api_key`
- `deepseek_model`
- `deepseek_base_url`
- `gemini_api_key`
- `gemini_model`
- `tts_enabled`
- `tts_voice`
- `tts_rate`
- `tts_volume`
- `stt_enabled`
- `stt_model`
- `stt_language`
- `stt_device`
- `memory_enabled`

## Runtime Storage

Ignored runtime paths:

- `cache/audio`
- `cache/recordings`
- `cache/screenshots`
- `data`
- `logs`
- `config/window_state.json`

## Not Completed

- Vector memory
- RAG
- Semantic search
- Long-term memory summarization
- Automatic send after speech recognition

## Next Step

Stop after Phase 8. Do not enter Phase 9 automatically.
