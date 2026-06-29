# Manual Test Guide

## Phase 7 Startup Test

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
- The window contains a character area, chat history, input box, `截图分析` button, `测试语音` button, `语音输入` button, and Send button.
- The window can still be resized from edges, corners, and the visible bottom-right grip.

## Speech Recognition Settings Test

1. Open the tray menu.
2. Click `Settings`.

Expected result:

- The dialog shows `Speech recognition`.
- The dialog shows `STT model`.
- The dialog shows `STT language`.
- The dialog shows `STT device`.

Default values:

```text
stt_enabled = false
stt_model = base
stt_language = zh
stt_device = cpu
```

## Speech Input Disabled Test

1. Set `stt_enabled` to `false` in `config/settings.json` or in Settings.
2. Run `python main.py`.
3. Click `语音输入`.

Expected result:

- The app does not crash.
- Chat history shows:

```text
语音识别未启用
```

## Speech Input Recording Test

1. Set `stt_enabled` to `true` in `config/settings.json` or in Settings.
2. Run `python main.py`.
3. Click `语音输入`.
4. Speak into the microphone.
5. Click `停止录音`.

Expected result:

- Button text changes to `停止录音` while recording.
- A WAV file is saved under `cache/recordings`.
- The app attempts transcription.
- Recognized text is filled into the input box.
- The app does not auto-send the message.

If no microphone is available, the app should show:

```text
未检测到可用麦克风
```

If recognition dependencies are not installed, the app should show:

```text
未安装语音识别依赖
```

## Test Voice Button

1. Run `python main.py`.
2. Click `测试语音`.

Expected result:

- The app speaks: `你好，我是你的桌面陪伴助手。`
- A new MP3 file is saved under `cache/audio`.
- The app does not crash if generation or playback fails; the error is logged.

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

## Compatibility Checks

- Drag the bottom-right resize grip: window size changes.
- Drag window edges and corners: window size changes.
- Click `-`: the window hides to the system tray.
- Use tray menu `Show Assistant`: the window appears again.
- Send a chat message with empty DeepSeek key: chat shows `未配置 DeepSeek API Key`.
- Type multiple lines with Shift+Enter: input keeps the newline.

## Phase 7 Limitations

The following are expected not to work yet:

- Automatic send after speech recognition
- Long-term memory
- Active screen observation
