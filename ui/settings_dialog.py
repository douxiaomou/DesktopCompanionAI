from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from config.settings import SETTINGS_PATH, update_settings_file


class SettingsDialog(QDialog):
    """Dialog for user-editable model and voice configuration."""

    def __init__(
        self,
        settings,
        settings_path: Path = SETTINGS_PATH,
        parent=None,
        storage_service=None,
        memory_cleared_callback=None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self.settings_path = settings_path
        self.storage_service = storage_service
        self.memory_cleared_callback = memory_cleared_callback
        self.setWindowTitle("Settings")
        self.setMinimumWidth(460)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.deepseek_api_key_edit = QLineEdit(self.settings.deepseek_api_key, self)
        self.deepseek_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.deepseek_model_edit = QLineEdit(self.settings.deepseek_model, self)
        self.deepseek_base_url_edit = QLineEdit(self.settings.deepseek_base_url, self)
        self.gemini_api_key_edit = QLineEdit(self.settings.gemini_api_key, self)
        self.gemini_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_model_edit = QLineEdit(self.settings.gemini_model, self)

        self.tts_enabled_edit = QCheckBox("Enable voice replies", self)
        self.tts_enabled_edit.setChecked(bool(self.settings.tts_enabled))
        self.tts_voice_edit = QLineEdit(self.settings.tts_voice, self)
        self.tts_rate_edit = QLineEdit(self.settings.tts_rate, self)
        self.tts_volume_edit = QLineEdit(self.settings.tts_volume, self)
        self.stt_enabled_edit = QCheckBox("Enable speech recognition", self)
        self.stt_enabled_edit.setChecked(bool(self.settings.stt_enabled))
        self.stt_model_edit = QLineEdit(self.settings.stt_model, self)
        self.stt_language_edit = QLineEdit(self.settings.stt_language, self)
        self.stt_device_edit = QComboBox(self)
        self.stt_device_edit.addItems(["cpu", "cuda"])
        current_device = self.settings.stt_device if self.settings.stt_device in {"cpu", "cuda"} else "cpu"
        self.stt_device_edit.setCurrentText(current_device)
        self.memory_enabled_edit = QCheckBox("Enable chat memory", self)
        self.memory_enabled_edit.setChecked(bool(self.settings.memory_enabled))

        form.addRow("DeepSeek API Key", self.deepseek_api_key_edit)
        form.addRow("DeepSeek model", self.deepseek_model_edit)
        form.addRow("DeepSeek Base URL", self.deepseek_base_url_edit)
        form.addRow("Gemini API Key", self.gemini_api_key_edit)
        form.addRow("Gemini model", self.gemini_model_edit)
        form.addRow("Voice replies", self.tts_enabled_edit)
        form.addRow("TTS voice", self.tts_voice_edit)
        form.addRow("TTS rate", self.tts_rate_edit)
        form.addRow("TTS volume", self.tts_volume_edit)
        form.addRow("Speech recognition", self.stt_enabled_edit)
        form.addRow("STT model", self.stt_model_edit)
        form.addRow("STT language", self.stt_language_edit)
        form.addRow("STT device", self.stt_device_edit)
        form.addRow("Chat memory", self.memory_enabled_edit)
        layout.addLayout(form)

        memory_group = QGroupBox("记忆管理", self)
        memory_layout = QFormLayout(memory_group)
        self.memory_count_label = QLabel(self._memory_count_text(), memory_group)
        self.clear_memory_button = QPushButton("清空聊天记忆", memory_group)
        self.clear_memory_button.clicked.connect(self._clear_memory)
        memory_layout.addRow("当前消息数量", self.memory_count_label)
        memory_layout.addRow(self.clear_memory_button)
        layout.addWidget(memory_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self) -> None:
        update_settings_file(
            {
                "deepseek_api_key": self.deepseek_api_key_edit.text().strip(),
                "deepseek_model": self.deepseek_model_edit.text().strip() or "deepseek-chat",
                "deepseek_base_url": self.deepseek_base_url_edit.text().strip() or "https://api.deepseek.com",
                "gemini_api_key": self.gemini_api_key_edit.text().strip(),
                "gemini_model": self.gemini_model_edit.text().strip() or "gemini-2.5-flash",
                "tts_enabled": self.tts_enabled_edit.isChecked(),
                "tts_voice": self.tts_voice_edit.text().strip() or "zh-CN-XiaoxiaoNeural",
                "tts_rate": self.tts_rate_edit.text().strip() or "+0%",
                "tts_volume": self.tts_volume_edit.text().strip() or "+0%",
                "stt_enabled": self.stt_enabled_edit.isChecked(),
                "stt_model": self.stt_model_edit.text().strip() or "base",
                "stt_language": self.stt_language_edit.text().strip() or "zh",
                "stt_device": self.stt_device_edit.currentText(),
                "memory_enabled": self.memory_enabled_edit.isChecked(),
            },
            path=self.settings_path,
        )
        super().accept()

    def _memory_count_text(self) -> str:
        if not bool(self.settings.memory_enabled):
            return "记忆已关闭"
        if self.storage_service is None:
            return "不可用"
        try:
            return str(self.storage_service.count_messages())
        except Exception:
            return "读取失败"

    def _clear_memory(self) -> None:
        if self.storage_service is not None:
            self.storage_service.clear_messages()
        if self.memory_cleared_callback is not None:
            self.memory_cleared_callback()
        self.memory_count_label.setText("0")
