from __future__ import annotations

import logging
import wave
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RECORDINGS_DIR = PROJECT_ROOT / "cache" / "recordings"
MAX_RECORDINGS = 20
MISSING_STT_DEPENDENCY_MESSAGE = "未安装语音识别依赖"
NO_MICROPHONE_MESSAGE = "未检测到可用麦克风"
STT_DISABLED_MESSAGE = "语音识别未启用"


@dataclass(frozen=True)
class RecordingResult:
    success: bool
    message: str
    audio_path: Path | None = None


@dataclass(frozen=True)
class TranscriptionResult:
    success: bool
    message: str
    text: str = ""


class SpeechToTextService:
    """Record microphone audio and transcribe it through an STT backend."""

    def __init__(self, settings: Any) -> None:
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self._stream: Any | None = None
        self._chunks: list[Any] = []
        self._sample_rate = 16000
        self._channels = 1
        self._is_recording = False
        self._model: Any | None = None
        self._model_key: tuple[str, str] | None = None
        RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def start_recording(self) -> RecordingResult:
        if not getattr(self.settings, "stt_enabled", False):
            return RecordingResult(success=False, message=STT_DISABLED_MESSAGE)
        if self._is_recording:
            return RecordingResult(success=True, message="录音已在进行中")

        try:
            import sounddevice as sd
        except ImportError:
            self.logger.warning(MISSING_STT_DEPENDENCY_MESSAGE)
            return RecordingResult(success=False, message=MISSING_STT_DEPENDENCY_MESSAGE)

        try:
            if not self._has_input_device(sd):
                self.logger.warning(NO_MICROPHONE_MESSAGE)
                return RecordingResult(success=False, message=NO_MICROPHONE_MESSAGE)

            self._chunks = []

            def _callback(indata, frames, time_info, status) -> None:
                if status:
                    self.logger.warning("Microphone recording status: %s", status)
                self._chunks.append(indata.copy())

            self._stream = sd.InputStream(
                samplerate=self._sample_rate,
                channels=self._channels,
                dtype="float32",
                callback=_callback,
            )
            self._stream.start()
            self._is_recording = True
            self.logger.info("Microphone recording started")
            return RecordingResult(success=True, message="开始录音")
        except Exception:
            self.logger.exception("Failed to start microphone recording")
            self._reset_recording_state()
            return RecordingResult(success=False, message=NO_MICROPHONE_MESSAGE)

    def stop_recording(self) -> RecordingResult:
        if not self._is_recording:
            return RecordingResult(success=False, message="当前没有正在进行的录音")

        try:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
            audio_path = self._save_recording()
            self._cleanup_old_recordings()
            self.logger.info("Recording saved: %s", audio_path)
            return RecordingResult(success=True, message="录音已保存", audio_path=audio_path)
        except Exception as exc:
            self.logger.exception("Failed to stop microphone recording")
            return RecordingResult(success=False, message=f"录音保存失败: {exc}")
        finally:
            self._reset_recording_state()

    def cancel_recording(self) -> None:
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                self.logger.exception("Failed to cancel microphone recording")
        self._reset_recording_state()

    def transcribe(self, audio_path: str | Path) -> TranscriptionResult:
        if not getattr(self.settings, "stt_enabled", False):
            return TranscriptionResult(success=False, message=STT_DISABLED_MESSAGE)

        path = Path(audio_path)
        if not path.exists():
            return TranscriptionResult(success=False, message=f"录音文件不存在: {path}")

        try:
            text = self._transcribe_with_faster_whisper(path)
        except ImportError:
            try:
                text = self._transcribe_with_whisper(path)
            except ImportError:
                self.logger.warning(MISSING_STT_DEPENDENCY_MESSAGE)
                return TranscriptionResult(success=False, message=MISSING_STT_DEPENDENCY_MESSAGE)
            except Exception as exc:
                self.logger.exception("Whisper transcription failed")
                return TranscriptionResult(success=False, message=f"语音识别失败: {exc}")
        except Exception as exc:
            self.logger.exception("Faster-Whisper transcription failed")
            return TranscriptionResult(success=False, message=f"语音识别失败: {exc}")

        clean_text = text.strip()
        if not clean_text:
            return TranscriptionResult(success=False, message="未识别到语音内容")
        return TranscriptionResult(success=True, message="语音识别完成", text=clean_text)

    def _transcribe_with_faster_whisper(self, audio_path: Path) -> str:
        from faster_whisper import WhisperModel

        model_key = (self.settings.stt_model, self.settings.stt_device)
        if self._model is None or self._model_key != model_key:
            compute_type = "int8" if self.settings.stt_device == "cpu" else "float16"
            self._model = WhisperModel(
                self.settings.stt_model,
                device=self.settings.stt_device,
                compute_type=compute_type,
            )
            self._model_key = model_key

        language = self.settings.stt_language or None
        segments, _info = self._model.transcribe(str(audio_path), language=language)
        return "".join(segment.text for segment in segments)

    def _transcribe_with_whisper(self, audio_path: Path) -> str:
        import whisper

        model = whisper.load_model(self.settings.stt_model, device=self.settings.stt_device)
        result = model.transcribe(str(audio_path), language=self.settings.stt_language or None)
        return str(result.get("text", ""))

    def _save_recording(self) -> Path:
        if not self._chunks:
            raise RuntimeError("录音内容为空")

        try:
            import numpy as np
        except ImportError:
            raise ImportError(MISSING_STT_DEPENDENCY_MESSAGE) from None

        RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
        audio_path = RECORDINGS_DIR / f"recording_{datetime.now():%Y%m%d_%H%M%S_%f}.wav"
        audio = np.concatenate(self._chunks, axis=0)
        audio = np.clip(audio, -1.0, 1.0)
        pcm_audio = (audio * 32767).astype(np.int16)

        with wave.open(str(audio_path), "wb") as file:
            file.setnchannels(self._channels)
            file.setsampwidth(2)
            file.setframerate(self._sample_rate)
            file.writeframes(pcm_audio.tobytes())
        return audio_path

    def _has_input_device(self, sounddevice_module: Any) -> bool:
        try:
            devices = sounddevice_module.query_devices()
        except Exception:
            self.logger.exception("Failed to query audio input devices")
            return False

        return any(int(device.get("max_input_channels", 0)) > 0 for device in devices)

    def _cleanup_old_recordings(self) -> None:
        recording_files = sorted(RECORDINGS_DIR.glob("*.wav"), key=lambda path: path.stat().st_mtime, reverse=True)
        for old_path in recording_files[MAX_RECORDINGS:]:
            try:
                old_path.unlink()
            except OSError:
                self.logger.exception("Failed to remove old recording file: %s", old_path)

    def _reset_recording_state(self) -> None:
        self._stream = None
        self._chunks = []
        self._is_recording = False
