# Manual Test Guide

## Phase 6 Startup Test

1. Open PowerShell.
2. Change directory:

```powershell
cd D:\DesktopCompanionAI
```

3. Run:

```powershell
python main.py
```

Expected result:

- A desktop floating window appears.
- The window contains a character area, chat history, input box, `截图分析` button, `测试语音` button, and Send button.
- The window can still be resized from edges, corners, and the visible bottom-right grip.

## Voice Settings Test

1. Open the tray menu.
2. Click `Settings`.

Expected result:

- The dialog shows `Voice replies`.
- The dialog shows `TTS voice`.
- The dialog shows `TTS rate`.
- The dialog shows `TTS volume`.

Default values:

```text
tts_enabled = false
tts_voice = zh-CN-XiaoxiaoNeural
tts_rate = +0%
tts_volume = +0%
```

## Test Voice Button

1. Run `python main.py`.
2. Click `测试语音`.

Expected result:

- The app speaks: `你好，我是你的桌面陪伴助手。`
- A new MP3 file is saved under `cache/audio`.
- The app does not crash if generation or playback fails; the error is logged.

## Auto Voice Reply Disabled Test

1. Set `tts_enabled` to `false` in `config/settings.json` or in Settings.
2. Send a chat message.

Expected result:

- AI text appears in chat.
- No automatic voice playback starts.

## Auto Voice Reply Enabled Test

1. Set `tts_enabled` to `true` in `config/settings.json` or in Settings.
2. Send a chat message.

Expected result:

- AI text appears in chat.
- The reply is read aloud.
- A new MP3 file is saved under `cache/audio`.

## Screenshot Analysis No-Key Test

1. Confirm `config/settings.json` has an empty `gemini_api_key`.
2. Run `python main.py`.
3. Click `截图分析`.

Expected result:

- A PNG screenshot is saved under `cache/screenshots`.
- The app does not crash.
- Chat history shows:

```text
未配置 Gemini API Key
```

## Screenshot Analysis Real Gemini Test

1. Fill `gemini_api_key` in `config/settings.json`.
2. Confirm `gemini_model` is correct.
3. Run `python main.py`.
4. Click `截图分析`.

Expected result:

- A screenshot is saved under `cache/screenshots`.
- Gemini analyzes the screenshot.
- The analysis text appears in chat history.

## Compatibility Checks

- Drag the bottom-right resize grip: window size changes.
- Drag window edges and corners: window size changes.
- Click `-`: the window hides to the system tray.
- Use tray menu `Show Assistant`: the window appears again.
- Send a chat message with empty DeepSeek key: chat shows `未配置 DeepSeek API Key`.
- Type multiple lines with Shift+Enter: input keeps the newline.

## Phase 6 Limitations

The following are expected not to work yet:

- Speech recognition
- Long-term memory
- Active screen observation
