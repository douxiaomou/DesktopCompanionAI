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

- SQLite `StorageService`
- `data/companion.db`
- `messages` table
- Recent 20-message startup restore
- Settings memory management

## Phase 9: Character Presentation + Interaction UX

Status: Completed

Completed:

- Added character state system: `idle`, `listening`, `thinking`, `speaking`, `error`.
- Added compact state display in the character area.
- Added default placeholder note: `当前使用默认占位角色`.
- Added recent AI reply bubble.
- Linked chat, screenshot analysis, TTS playback, and speech input to character state.
- Test voice success now shows `测试语音播放成功` instead of a full MP3 path.
- Kept `assets/character/default.png` as the placeholder character.

Known issues:

- No Live2D.
- No complex animation engine.
- No character personality or emotional system.
- Real API usage still requires user-filled API keys.

Next phase:

- Stop after Phase 9. Do not enter Phase 10 automatically.
