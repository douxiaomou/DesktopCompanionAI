# Roadmap

## Phase 1: Project Initialization

Status: Completed

## Phase 2: Desktop Floating Window

Status: Completed

## Phase 3: Chat System

Status: Completed

## Phase 4: Desktop UX Enhancement

Status: Completed

Completed:

- Tray show/hide
- Edge resizing and visible bottom-right resize grip
- Window state persistence
- Settings dialog

## Phase 5: Screenshot Analysis + Gemini Vision

Status: Completed

Completed:

- Screenshot capture to `cache/screenshots`
- GeminiProvider no-key fallback
- `截图分析` button and chat display

## Phase 6: Edge-TTS Voice Replies

Status: Completed

Completed:

- Edge-TTS MP3 generation to `cache/audio`
- Test voice button
- Optional AI reply voice playback

## Phase 7: Microphone Speech Input

Status: Completed

Completed:

- `SpeechToTextService`
- `语音输入` / `停止录音` button states
- WAV recordings to `cache/recordings`
- Speech recognition fallback when dependencies are missing
- Recognized text fills the input box without auto-send

## Phase 8: SQLite Chat Memory

Status: Completed

Completed:

- Implemented `StorageService` with SQLite.
- Database path: `data/companion.db`.
- Created `messages` table with `id`, `role`, `content`, and `created_at`.
- Saves user messages after Send.
- Saves AI chat replies as assistant messages.
- Saves screenshot analysis results as assistant messages.
- Loads the latest 20 messages into Chat history on startup.
- `memory_enabled=false` disables save/load.
- Settings dialog shows memory state, message count, and a clear memory button.
- `.gitignore` excludes `data/`, `*.db`, `*.sqlite`, and `*.sqlite3`.

Known issues:

- Memory is plain SQLite text history only.
- No vector memory, embeddings, RAG, or semantic search.
- Real DeepSeek/Gemini usage still requires API keys.

Next phase:

- Stop after Phase 8. Do not enter Phase 9 automatically.
