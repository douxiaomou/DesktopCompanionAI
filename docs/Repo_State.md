# Repository State

## Current Version

Desktop Companion AI V0.1 Phase 9

## Completed

- Provider/service architecture.
- PyQt6 floating desktop window.
- Phase 4.2 resize and tray UX.
- DeepSeek chat provider with no-key fallback.
- Gemini screenshot analysis with no-key fallback.
- Edge-TTS voice reply service and test voice button.
- Microphone speech input MVP.
- SQLite chat memory MVP.
- Character status display and recent reply bubble.

## Phase 9 Character UX

States:

- `idle`: 空闲
- `listening`: 正在听你说话
- `thinking`: 正在思考
- `speaking`: 正在说话
- `error`: 出错了

UI additions:

- Compact status label in the character area.
- Placeholder note: `当前使用默认占位角色`.
- Recent AI reply bubble above Chat history.

Behavior:

- Sending chat sets `thinking`.
- AI reply returns to `idle`, or moves to `speaking` when TTS plays.
- TTS completion returns to `idle`.
- Voice recording sets `listening`.
- Screenshot analysis sets `thinking`.
- Recoverable failures briefly show `error`.

## Unchanged Boundaries

- No real API keys were configured.
- No provider core logic was changed.
- No TTS/STT service core logic was changed.
- Existing `config/settings.json` fields keep their meaning.
- `assets/character/default.png` remains the placeholder character.

## Not Completed

- Live2D
- Complex animation engine
- Character personality
- Emotional system
- Desktop pet mode switching

## Next Step

Stop after Phase 9. Do not enter Phase 10 automatically.
