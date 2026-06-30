# Manual Test Guide

## Phase 9 Startup Test

```powershell
cd D:\DesktopCompanionAI
python main.py
```

Expected:

- Desktop floating window appears.
- Character area shows a compact state label.
- Character area shows `当前使用默认占位角色`.
- Chat history and controls remain visible.

## Character State Checks

- Idle startup: state shows `空闲`.
- Send a chat message: state changes to `正在思考`.
- AI reply completes with TTS disabled: state returns to `空闲`.
- Click `测试语音`: state changes to `正在说话`.
- Test voice success: Chat history shows `测试语音播放成功` and does not show a full `.mp3` path.
- Click `语音输入` with STT enabled: state changes to `正在听你说话`.
- Click `截图分析`: state changes to `正在思考`.
- Recoverable failures briefly show `出错了`.

## Recent Reply Bubble

Expected:

- The latest AI reply summary appears above Chat history.
- Long replies are truncated.
- Chat history still contains the full message.

## Compatibility Checks

- Resize from edges/corners and bottom-right grip.
- Click `截图分析`.
- Click `测试语音`.
- Click `语音输入`.
- Send a chat message and confirm SQLite memory still saves user/assistant rows.
- Restart and confirm recent memory still loads.
- Hide/show from tray.

## Phase 9 Limitations

- No Live2D.
- No complex animation engine.
- No desktop pet mode.
- No personality or emotion system.
