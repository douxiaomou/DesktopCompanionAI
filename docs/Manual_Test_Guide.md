# Manual Test Guide

## Phase 8 Startup Test

```powershell
cd D:\DesktopCompanionAI
python main.py
```

Expected:

- Desktop floating window appears.
- `data/companion.db` exists.
- Existing recent messages appear in Chat history only when `memory_enabled=true`.

## SQLite Memory Test

1. Confirm `memory_enabled=true`.
2. Run `python main.py`.
3. Send a chat message.
4. Inspect `data/companion.db`.

Expected:

- `messages` contains a `user` row.
- `messages` contains an `assistant` row.

## Restart History Test

1. Close the app.
2. Run `python main.py` again.

Expected:

- The latest 20 messages appear in Chat history.

## Screenshot Memory Test

1. Click `截图分析`.

Expected:

- Screenshot analysis output appears in Chat history.
- The result is saved as an `assistant` row in `messages`.

## Memory Disabled Test

1. Set `memory_enabled=false`.
2. Run `python main.py`.
3. Send a message.

Expected:

- No new message rows are saved.
- Startup does not load old history.

## Settings Memory Management Test

1. Open Settings.
2. Confirm `记忆管理` is visible.
3. Confirm current message count is visible.
4. Click `清空聊天记忆`.

Expected:

- `messages` table is cleared.
- Chat history in the UI is cleared.
- The app does not crash.

## Compatibility Checks

- Resize from edges/corners and bottom-right grip.
- Click `截图分析`.
- Click `测试语音`.
- Click `语音输入` with `stt_enabled=false` and confirm the disabled message.
- Hide/show from tray.

## Phase 8 Limitations

- No vector memory.
- No RAG.
- No semantic search.
- No memory summarization.
