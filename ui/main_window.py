from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

from PyQt6.QtCore import QEvent, QObject, QPoint, QRect, QThread, QTimer, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import (
    QAction,
    QColor,
    QCloseEvent,
    QIcon,
    QKeyEvent,
    QMouseEvent,
    QMoveEvent,
    QPainter,
    QPen,
    QPixmap,
    QResizeEvent,
)
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config.window_state import (
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    MAX_HEIGHT,
    MAX_WIDTH,
    MIN_HEIGHT,
    MIN_WIDTH,
    WINDOW_STATE_PATH,
    WindowState,
    load_window_state,
    save_window_state,
)
from ui.settings_dialog import SettingsDialog


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHARACTER_PATH = PROJECT_ROOT / "assets" / "character" / "default.png"
RESIZE_MARGIN = 16
RESIZE_GRIP_SIZE = 30
RECENT_REPLY_MAX_LENGTH = 120
CHARACTER_STATUS_TEXT = {
    "idle": "空闲",
    "listening": "正在听你说话",
    "thinking": "正在思考",
    "speaking": "正在说话",
    "error": "出错了",
}


class ChatWorker(QObject):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, chat_service: Any, message: str) -> None:
        super().__init__()
        self.chat_service = chat_service
        self.message = message

    @pyqtSlot()
    def run(self) -> None:
        try:
            self.finished.emit(self.chat_service.chat(self.message))
        except Exception as exc:
            self.failed.emit(f"Chat failed: {exc}")


class ScreenshotAnalysisWorker(QObject):
    finished = pyqtSignal(str, str)
    failed = pyqtSignal(str)

    def __init__(self, screenshot_service: Any, vision_service: Any) -> None:
        super().__init__()
        self.screenshot_service = screenshot_service
        self.vision_service = vision_service

    @pyqtSlot()
    def run(self) -> None:
        try:
            screenshot_path = self.screenshot_service.capture_primary_screen()
            result = self.vision_service.analyze(screenshot_path)
            self.finished.emit(str(screenshot_path), result)
        except Exception as exc:
            self.failed.emit(f"Screenshot analysis failed: {exc}")


class SpeechWorker(QObject):
    finished = pyqtSignal(bool, str, str)

    def __init__(self, tts_service: Any, text: str) -> None:
        super().__init__()
        self.tts_service = tts_service
        self.text = text

    @pyqtSlot()
    def run(self) -> None:
        result = self.tts_service.speak(self.text)
        audio_path = str(result.audio_path) if result.audio_path else ""
        self.finished.emit(result.success, result.message, audio_path)


class TranscriptionWorker(QObject):
    finished = pyqtSignal(bool, str, str)

    def __init__(self, stt_service: Any, audio_path: str) -> None:
        super().__init__()
        self.stt_service = stt_service
        self.audio_path = audio_path

    @pyqtSlot()
    def run(self) -> None:
        result = self.stt_service.transcribe(self.audio_path)
        self.finished.emit(result.success, result.message, result.text)


class ChatInput(QTextEdit):
    send_requested = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                super().keyPressEvent(event)
                return
            self.send_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class ResizeGrip(QWidget):
    """Visible bottom-right resize affordance for the frameless window."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(RESIZE_GRIP_SIZE, RESIZE_GRIP_SIZE)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.setMouseTracking(True)
        self.setToolTip("Drag to resize")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        fill = QColor(255, 255, 255, 28)
        painter.setBrush(fill)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(
            QPoint(self.width(), self.height()),
            QPoint(self.width(), 5),
            QPoint(5, self.height()),
        )

        pen = QPen(QColor(255, 255, 255, 175), 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(self.width() - 6, self.height() - 20, self.width() - 20, self.height() - 6)
        painter.drawLine(self.width() - 6, self.height() - 14, self.width() - 14, self.height() - 6)
        painter.drawLine(self.width() - 6, self.height() - 8, self.width() - 8, self.height() - 6)


class MainWindow(QWidget):
    """Frameless desktop companion window with edge and corner resizing."""

    clicked = pyqtSignal()

    def __init__(
        self,
        chat_service: Any | None = None,
        screenshot_service: Any | None = None,
        vision_service: Any | None = None,
        tts_service: Any | None = None,
        stt_service: Any | None = None,
        storage_service: Any | None = None,
        settings: Any | None = None,
        settings_reload_callback: Callable[[], Any] | None = None,
        character_path: Path | None = None,
    ) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.chat_service = chat_service
        self.screenshot_service = screenshot_service
        self.vision_service = vision_service
        self.tts_service = tts_service
        self.stt_service = stt_service
        self.storage_service = storage_service
        self.settings = settings
        self.settings_reload_callback = settings_reload_callback
        self.character_path = character_path or DEFAULT_CHARACTER_PATH
        self._character_pixmap = QPixmap()
        self._drag_offset = QPoint()
        self._is_dragging = False
        self._drag_moved = False
        self._resize_edges: set[str] = set()
        self._resize_start_geometry = QRect()
        self._resize_start_position = QPoint()
        self._chat_thread: QThread | None = None
        self._chat_worker: ChatWorker | None = None
        self._vision_thread: QThread | None = None
        self._vision_worker: ScreenshotAnalysisWorker | None = None
        self._speech_thread: QThread | None = None
        self._speech_worker: SpeechWorker | None = None
        self._transcription_thread: QThread | None = None
        self._transcription_worker: TranscriptionWorker | None = None
        self._is_recording = False
        self._character_state = "idle"
        self._recent_reply_text = ""
        self._force_exit = False
        self._restoring_state = False
        self._cursor_widgets: list[QWidget] = []
        self.resize_grip: ResizeGrip | None = None

        self._configure_window()
        self._build_ui()
        self._install_resize_event_filters()
        self._create_tray()
        self._restore_window_state()
        self._load_recent_memory()
        self.clicked.connect(self._handle_click)

    def set_chat_service(self, chat_service: Any) -> None:
        self.chat_service = chat_service

    def set_screenshot_analysis_services(self, screenshot_service: Any, vision_service: Any) -> None:
        self.screenshot_service = screenshot_service
        self.vision_service = vision_service

    def set_tts_service(self, tts_service: Any) -> None:
        self.tts_service = tts_service

    def set_stt_service(self, stt_service: Any) -> None:
        self.stt_service = stt_service

    def set_storage_service(self, storage_service: Any) -> None:
        self.storage_service = storage_service

    def _configure_window(self) -> None:
        self.setWindowTitle("Desktop Companion AI")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setMouseTracking(True)
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.setMaximumSize(MAX_WIDTH, MAX_HEIGHT)
        self.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(8)

        self.panel = QWidget(self)
        self.panel.setMouseTracking(True)
        self.panel.setObjectName("panel")
        self.panel.setStyleSheet(
            """
            QWidget#panel {
                background-color: rgba(16, 18, 24, 198);
                border: 1px solid rgba(255, 255, 255, 75);
                border-radius: 14px;
            }
            """
        )
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(10, 8, 10, 10)
        panel_layout.setSpacing(8)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel("Desktop Companion AI", self.panel)
        self.title_label.setStyleSheet("color: #f6f7f9; font-size: 13px; font-weight: 600;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)

        self.minimize_button = QPushButton("-", self.panel)
        self.minimize_button.setToolTip("Hide to system tray")
        self.minimize_button.clicked.connect(self.hide_to_tray)
        self.close_button = QPushButton("x", self.panel)
        self.close_button.setToolTip("Exit")
        self.close_button.clicked.connect(self.exit_application)
        for button in (self.minimize_button, self.close_button):
            button.setFixedSize(28, 24)
            button.setStyleSheet(
                """
                QPushButton {
                    color: white;
                    background-color: rgba(58, 63, 73, 190);
                    border: 1px solid rgba(255, 255, 255, 60);
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: rgba(82, 98, 118, 220);
                }
                """
            )
            title_layout.addWidget(button)

        self.character_label = QLabel(self.panel)
        self.character_label.setMouseTracking(True)
        self.character_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.character_label.setMinimumHeight(120)
        self.character_label.setObjectName("characterLabel")
        self.character_label.setStyleSheet(
            """
            QLabel#characterLabel {
                color: white;
                background-color: rgba(32, 36, 44, 120);
                border: 1px solid rgba(255, 255, 255, 55);
                border-radius: 12px;
                font-size: 18px;
                font-weight: 600;
                padding: 18px;
            }
            """
        )
        self._load_character()

        self.status_label = QLabel(CHARACTER_STATUS_TEXT["idle"], self.panel)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setStyleSheet(
            """
            QLabel#statusLabel {
                color: #f6f7f9;
                background-color: rgba(62, 120, 168, 150);
                border: 1px solid rgba(255, 255, 255, 48);
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: 600;
            }
            """
        )

        self.character_note_label = QLabel("当前使用默认占位角色", self.panel)
        self.character_note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.character_note_label.setObjectName("characterNoteLabel")
        self.character_note_label.setStyleSheet(
            """
            QLabel#characterNoteLabel {
                color: rgba(246, 247, 249, 175);
                font-size: 11px;
                padding: 0 4px;
            }
            """
        )

        self.recent_reply_label = QLabel("", self.panel)
        self.recent_reply_label.setWordWrap(True)
        self.recent_reply_label.setVisible(False)
        self.recent_reply_label.setObjectName("recentReplyLabel")
        self.recent_reply_label.setStyleSheet(
            """
            QLabel#recentReplyLabel {
                color: #f6f7f9;
                background-color: rgba(42, 48, 58, 215);
                border: 1px solid rgba(255, 255, 255, 58);
                border-radius: 8px;
                padding: 7px 9px;
                font-size: 12px;
            }
            """
        )

        self.chat_view = QTextEdit(self.panel)
        self.chat_view.setReadOnly(True)
        self.chat_view.setObjectName("chatView")
        self.chat_view.setPlaceholderText("Chat history")
        self.chat_view.setStyleSheet(
            """
            QTextEdit#chatView {
                color: #f6f7f9;
                background-color: rgba(22, 24, 30, 225);
                border: 1px solid rgba(255, 255, 255, 70);
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
            }
            """
        )

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(6)

        self.screenshot_button = QPushButton("截图分析", self.panel)
        self.screenshot_button.clicked.connect(self._analyze_screenshot)
        self.screenshot_button.setFixedSize(86, 72)
        self.screenshot_button.setStyleSheet(
            """
            QPushButton {
                color: white;
                background-color: rgba(88, 98, 108, 230);
                border: 1px solid rgba(255, 255, 255, 80);
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(108, 118, 130, 235);
            }
            QPushButton:disabled {
                color: rgba(255, 255, 255, 130);
                background-color: rgba(70, 74, 82, 180);
            }
            """
        )

        self.test_voice_button = QPushButton("测试语音", self.panel)
        self.test_voice_button.clicked.connect(self._test_voice)
        self.test_voice_button.setFixedSize(86, 72)
        self.test_voice_button.setStyleSheet(
            """
            QPushButton {
                color: white;
                background-color: rgba(72, 128, 104, 230);
                border: 1px solid rgba(255, 255, 255, 80);
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(86, 148, 120, 235);
            }
            QPushButton:disabled {
                color: rgba(255, 255, 255, 130);
                background-color: rgba(70, 74, 82, 180);
            }
            """
        )

        self.voice_input_button = QPushButton("语音输入", self.panel)
        self.voice_input_button.clicked.connect(self._toggle_voice_input)
        self.voice_input_button.setFixedSize(86, 72)
        self.voice_input_button.setStyleSheet(
            """
            QPushButton {
                color: white;
                background-color: rgba(126, 92, 150, 230);
                border: 1px solid rgba(255, 255, 255, 80);
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(146, 108, 170, 235);
            }
            QPushButton:disabled {
                color: rgba(255, 255, 255, 130);
                background-color: rgba(70, 74, 82, 180);
            }
            """
        )

        self.input_edit = ChatInput(self.panel)
        self.input_edit.setPlaceholderText("Type a message. Enter sends, Shift+Enter adds a new line.")
        self.input_edit.setFixedHeight(72)
        self.input_edit.send_requested.connect(self._send_message)
        self.input_edit.setStyleSheet(
            """
            QTextEdit {
                color: #f6f7f9;
                background-color: rgba(22, 24, 30, 235);
                border: 1px solid rgba(255, 255, 255, 85);
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 13px;
            }
            """
        )

        self.send_button = QPushButton("Send", self.panel)
        self.send_button.clicked.connect(self._send_message)
        self.send_button.setFixedSize(68, 72)
        self.send_button.setStyleSheet(
            """
            QPushButton {
                color: white;
                background-color: rgba(62, 120, 168, 230);
                border: 1px solid rgba(255, 255, 255, 80);
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:disabled {
                color: rgba(255, 255, 255, 130);
                background-color: rgba(70, 74, 82, 180);
            }
            """
        )

        input_layout.addWidget(self.screenshot_button)
        input_layout.addWidget(self.test_voice_button)
        input_layout.addWidget(self.voice_input_button)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.send_button)

        panel_layout.addLayout(title_layout)
        panel_layout.addWidget(self.character_label, 2)
        panel_layout.addWidget(self.status_label)
        panel_layout.addWidget(self.character_note_label)
        panel_layout.addWidget(self.recent_reply_label)
        panel_layout.addWidget(self.chat_view, 3)
        panel_layout.addLayout(input_layout)
        root_layout.addWidget(self.panel)

        self.resize_grip = ResizeGrip(self)
        self.resize_grip.raise_()
        self._position_resize_grip()

    def _install_resize_event_filters(self) -> None:
        self.installEventFilter(self)
        self._cursor_widgets = [self]
        for widget in self.findChildren(QWidget):
            widget.installEventFilter(self)
            widget.setMouseTracking(True)
            self._cursor_widgets.append(widget)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if isinstance(event, QMouseEvent):
            if event.type() == QEvent.Type.MouseButtonPress and self._handle_resize_press(event):
                return True
            if event.type() == QEvent.Type.MouseMove and self._handle_resize_move(event):
                return True
            if event.type() == QEvent.Type.MouseButtonRelease and self._handle_resize_release(event):
                return True
            if not self._is_dragging:
                self._update_resize_cursor(event.globalPosition().toPoint())
        return super().eventFilter(watched, event)

    def _handle_resize_press(self, event: QMouseEvent) -> bool:
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        edges = self._edges_at_global(event.globalPosition().toPoint())
        if not edges:
            return False
        self._resize_edges = edges
        self._resize_start_geometry = self.geometry()
        self._resize_start_position = event.globalPosition().toPoint()
        event.accept()
        return True

    def _handle_resize_move(self, event: QMouseEvent) -> bool:
        if self._resize_edges and event.buttons() & Qt.MouseButton.LeftButton:
            self._resize_window(event.globalPosition().toPoint())
            event.accept()
            return True
        return False

    def _handle_resize_release(self, event: QMouseEvent) -> bool:
        if event.button() == Qt.MouseButton.LeftButton and self._resize_edges:
            self._resize_edges = set()
            self._save_current_window_state()
            self._update_resize_cursor(event.globalPosition().toPoint())
            event.accept()
            return True
        return False

    def _edges_at_global(self, global_position: QPoint) -> set[str]:
        if self._is_on_resize_grip(global_position):
            return {"right", "bottom"}

        geometry = self.frameGeometry()
        x = global_position.x()
        y = global_position.y()
        edges: set[str] = set()
        if geometry.left() <= x <= geometry.left() + RESIZE_MARGIN:
            edges.add("left")
        elif geometry.right() - RESIZE_MARGIN <= x <= geometry.right():
            edges.add("right")
        if geometry.top() <= y <= geometry.top() + RESIZE_MARGIN:
            edges.add("top")
        elif geometry.bottom() - RESIZE_MARGIN <= y <= geometry.bottom():
            edges.add("bottom")
        return edges

    def _is_on_resize_grip(self, global_position: QPoint) -> bool:
        if self.resize_grip is None:
            return False
        local_position = self.resize_grip.mapFromGlobal(global_position)
        return self.resize_grip.rect().contains(local_position)

    def _resize_window(self, global_position: QPoint) -> None:
        delta = global_position - self._resize_start_position
        start = self._resize_start_geometry
        left = start.left()
        top = start.top()
        right = start.right()
        bottom = start.bottom()

        if "left" in self._resize_edges:
            left += delta.x()
        if "right" in self._resize_edges:
            right += delta.x()
        if "top" in self._resize_edges:
            top += delta.y()
        if "bottom" in self._resize_edges:
            bottom += delta.y()

        if right - left + 1 < MIN_WIDTH:
            if "left" in self._resize_edges:
                left = right - MIN_WIDTH + 1
            else:
                right = left + MIN_WIDTH - 1
        if bottom - top + 1 < MIN_HEIGHT:
            if "top" in self._resize_edges:
                top = bottom - MIN_HEIGHT + 1
            else:
                bottom = top + MIN_HEIGHT - 1
        if right - left + 1 > MAX_WIDTH:
            if "left" in self._resize_edges:
                left = right - MAX_WIDTH + 1
            else:
                right = left + MAX_WIDTH - 1
        if bottom - top + 1 > MAX_HEIGHT:
            if "top" in self._resize_edges:
                top = bottom - MAX_HEIGHT + 1
            else:
                bottom = top + MAX_HEIGHT - 1

        self.setGeometry(QRect(QPoint(left, top), QPoint(right, bottom)))

    def _update_resize_cursor(self, global_position: QPoint) -> None:
        edges = self._edges_at_global(global_position)
        if edges in ({"left", "top"}, {"right", "bottom"}):
            self._set_resize_cursor(Qt.CursorShape.SizeFDiagCursor)
        elif edges in ({"right", "top"}, {"left", "bottom"}):
            self._set_resize_cursor(Qt.CursorShape.SizeBDiagCursor)
        elif edges & {"left", "right"}:
            self._set_resize_cursor(Qt.CursorShape.SizeHorCursor)
        elif edges & {"top", "bottom"}:
            self._set_resize_cursor(Qt.CursorShape.SizeVerCursor)
        elif not self._resize_edges:
            self._unset_resize_cursor()

    def _set_resize_cursor(self, cursor_shape: Qt.CursorShape) -> None:
        for widget in self._cursor_widgets:
            widget.setCursor(cursor_shape)

    def _unset_resize_cursor(self) -> None:
        for widget in self._cursor_widgets:
            widget.unsetCursor()

    def _create_tray(self) -> None:
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self._window_icon())
        self.tray_icon.setToolTip("Desktop Companion AI")

        tray_menu = QMenu()
        self.show_action = QAction("Show Assistant", self)
        self.show_action.triggered.connect(self.show_from_tray)
        self.hide_action = QAction("Hide Assistant", self)
        self.hide_action.triggered.connect(self.hide_to_tray)
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.open_settings)
        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.exit_application)

        tray_menu.addAction(self.show_action)
        tray_menu.addAction(self.hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(self.settings_action)
        tray_menu.addSeparator()
        tray_menu.addAction(self.exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._handle_tray_activated)
        self.tray_icon.show()

    def _window_icon(self) -> QIcon:
        if self.character_path.exists():
            return QIcon(str(self.character_path))
        return QIcon()

    def _load_character(self) -> None:
        if self.character_path.exists():
            pixmap = QPixmap(str(self.character_path))
            if not pixmap.isNull():
                self._character_pixmap = pixmap
                self._update_character_pixmap()
                return

        self.character_label.setText("Desktop\nCompanion AI")
        self.logger.warning("Character image not found or invalid: %s", self.character_path)

    def _update_character_pixmap(self) -> None:
        if self._character_pixmap.isNull():
            return
        target_size = self.character_label.size()
        if target_size.width() <= 0 or target_size.height() <= 0:
            return
        scaled = self._character_pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.character_label.setPixmap(scaled)
        self.character_label.setStyleSheet("background: transparent;")

    def _restore_window_state(self) -> None:
        self._restoring_state = True
        try:
            if WINDOW_STATE_PATH.exists():
                state = load_window_state()
                geometry = QRect(state.x, state.y, state.width, state.height)
            else:
                geometry = self._default_geometry()
            self.setGeometry(self._fit_geometry_to_screen(geometry))
        finally:
            self._restoring_state = False

    def _default_geometry(self) -> QRect:
        available = self._available_geometry()
        width = min(DEFAULT_WIDTH, available.width())
        height = min(DEFAULT_HEIGHT, available.height())
        x = max(available.left(), available.right() - width - 48)
        y = max(available.top(), available.bottom() - height - 72)
        return QRect(x, y, width, height)

    def _fit_geometry_to_screen(self, geometry: QRect) -> QRect:
        available = self._available_geometry()
        width = min(MAX_WIDTH, max(MIN_WIDTH, geometry.width()))
        height = min(MAX_HEIGHT, max(MIN_HEIGHT, geometry.height()))
        width = min(width, available.width())
        height = min(height, available.height())
        x = min(max(geometry.x(), available.left()), available.right() - width + 1)
        y = min(max(geometry.y(), available.top()), available.bottom() - height + 1)
        return QRect(x, y, width, height)

    def _available_geometry(self) -> QRect:
        screen = self.screen() or QApplication.primaryScreen()
        if screen:
            return screen.availableGeometry()
        return QRect(0, 0, DEFAULT_WIDTH + 96, DEFAULT_HEIGHT + 96)

    def _save_current_window_state(self) -> None:
        if self._restoring_state:
            return
        geometry = self.geometry()
        save_window_state(
            WindowState(
                x=geometry.x(),
                y=geometry.y(),
                width=geometry.width(),
                height=geometry.height(),
            )
        )

    def _append_message(self, sender: str, message: str) -> None:
        self.chat_view.append(f"{sender}: {message}")
        scrollbar = self.chat_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _set_character_state(self, state: str, temporary_ms: int = 0) -> None:
        if state not in CHARACTER_STATUS_TEXT:
            state = "idle"
        self._character_state = state
        self.status_label.setText(CHARACTER_STATUS_TEXT[state])
        if temporary_ms > 0:
            QTimer.singleShot(temporary_ms, self._restore_idle_from_temporary_state)

    def _restore_idle_from_temporary_state(self) -> None:
        if self._character_state == "error":
            self._set_character_state("idle")

    def _show_error_state(self) -> None:
        self._set_character_state("error", temporary_ms=1800)

    def _update_recent_reply_bubble(self, text: str) -> None:
        clean_text = " ".join(text.strip().split())
        if not clean_text:
            return
        if len(clean_text) > RECENT_REPLY_MAX_LENGTH:
            clean_text = f"{clean_text[:RECENT_REPLY_MAX_LENGTH - 3]}..."
        self._recent_reply_text = clean_text
        self.recent_reply_label.setText(f"最近回复：{clean_text}")
        self.recent_reply_label.setVisible(True)

    def _load_recent_memory(self) -> None:
        if not self._memory_enabled():
            return
        if self.storage_service is None:
            return
        try:
            messages = self.storage_service.get_recent_messages(limit=20)
        except Exception:
            self.logger.exception("Failed to load recent chat memory")
            return
        if not messages:
            return

        if self.chat_service is not None and hasattr(self.chat_service, "history"):
            self.chat_service.history = self.storage_service.replace_chat_history(messages)

        for message in messages:
            self._append_message(self._sender_for_role(message.role), message.content)
            if message.role == "assistant":
                self._update_recent_reply_bubble(message.content)

    def _save_memory_message(self, role: str, content: str) -> None:
        if not self._memory_enabled():
            return
        if self.storage_service is None:
            return
        try:
            self.storage_service.add_message(role, content)
        except Exception:
            self.logger.exception("Failed to save chat memory")

    def _memory_enabled(self) -> bool:
        return bool(self.settings and getattr(self.settings, "memory_enabled", True))

    def _sender_for_role(self, role: str) -> str:
        if role == "user":
            return "Me"
        if role == "assistant":
            return "AI"
        return "System"

    def _send_message(self) -> None:
        message = self.input_edit.toPlainText().strip()
        if not message:
            return
        if not self.chat_service:
            self._append_message("AI", "Chat service is not initialized")
            self._show_error_state()
            return

        self.input_edit.clear()
        self._append_message("Me", message)
        self._save_memory_message("user", message)
        self._set_character_state("thinking")
        self._set_chat_busy(True)

        self._chat_thread = QThread(self)
        self._chat_worker = ChatWorker(self.chat_service, message)
        self._chat_worker.moveToThread(self._chat_thread)
        self._chat_thread.started.connect(self._chat_worker.run)
        self._chat_worker.finished.connect(self._handle_chat_reply)
        self._chat_worker.failed.connect(self._handle_chat_error)
        self._chat_worker.finished.connect(self._chat_thread.quit)
        self._chat_worker.failed.connect(self._chat_thread.quit)
        self._chat_thread.finished.connect(self._chat_worker.deleteLater)
        self._chat_thread.finished.connect(self._chat_thread.deleteLater)
        self._chat_thread.finished.connect(self._clear_chat_thread)
        self._chat_thread.start()

    def _handle_chat_reply(self, reply: str) -> None:
        self._append_message("AI", reply)
        self._update_recent_reply_bubble(reply)
        self._save_memory_message("assistant", reply)
        self._set_chat_busy(False)
        if not self._speak_ai_reply_if_enabled(reply):
            self._set_character_state("idle")

    def _handle_chat_error(self, message: str) -> None:
        self._append_message("AI", message)
        self._set_chat_busy(False)
        self._show_error_state()

    def _clear_chat_thread(self) -> None:
        self._chat_worker = None
        self._chat_thread = None

    def _set_chat_busy(self, busy: bool) -> None:
        self.input_edit.setEnabled(not busy)
        self.send_button.setEnabled(not busy)
        self.send_button.setText("Waiting" if busy else "Send")

    def _speak_ai_reply_if_enabled(self, reply: str) -> bool:
        if self.settings_reload_callback:
            self.settings = self.settings_reload_callback()
            self._sync_settings_to_services()
        if not self.settings or not getattr(self.settings, "tts_enabled", False):
            return False
        return self._speak_text(reply, show_success=False)

    def _test_voice(self) -> None:
        self._append_message("System", "Testing voice playback...")
        self._speak_text("你好，我是你的桌面陪伴助手。", show_success=True)

    def _speak_text(self, text: str, show_success: bool) -> bool:
        if not self.tts_service:
            self._append_message("AI", "Text-to-speech service is not initialized")
            self._show_error_state()
            return False
        if self._speech_thread and self._speech_thread.isRunning():
            self._append_message("System", "Voice playback is already running")
            return False

        self._set_character_state("speaking")
        self._set_tts_busy(True)
        self._speech_thread = QThread(self)
        self._speech_worker = SpeechWorker(self.tts_service, text)
        self._speech_worker.moveToThread(self._speech_thread)
        self._speech_thread.started.connect(self._speech_worker.run)
        self._speech_worker.finished.connect(
            lambda success, message, audio_path: self._handle_speech_result(
                success,
                message,
                audio_path,
                show_success,
            )
        )
        self._speech_worker.finished.connect(self._speech_thread.quit)
        self._speech_thread.finished.connect(self._speech_worker.deleteLater)
        self._speech_thread.finished.connect(self._speech_thread.deleteLater)
        self._speech_thread.finished.connect(self._clear_speech_thread)
        self._speech_thread.start()
        return True

    def _handle_speech_result(self, success: bool, message: str, audio_path: str, show_success: bool) -> None:
        if success:
            if show_success:
                self._append_message("System", "测试语音播放成功")
                if audio_path:
                    self.logger.info("Test voice audio played: %s", audio_path)
            self._set_character_state("idle")
        else:
            self._append_message("AI", message)
            self._show_error_state()
        self._set_tts_busy(False)

    def _clear_speech_thread(self) -> None:
        self._speech_worker = None
        self._speech_thread = None

    def _set_tts_busy(self, busy: bool) -> None:
        self.test_voice_button.setEnabled(not busy)
        self.test_voice_button.setText("播放中" if busy else "测试语音")

    def _toggle_voice_input(self) -> None:
        if self._is_recording:
            self._stop_voice_input()
        else:
            self._start_voice_input()

    def _start_voice_input(self) -> None:
        if not self.stt_service:
            self._append_message("AI", "Speech-to-text service is not initialized")
            self._show_error_state()
            return
        if self._transcription_thread and self._transcription_thread.isRunning():
            return
        if self.settings_reload_callback:
            self.settings = self.settings_reload_callback()
            self._sync_settings_to_services()
        if not self.settings or not getattr(self.settings, "stt_enabled", False):
            self._append_message("AI", "语音识别未启用")
            return

        result = self.stt_service.start_recording()
        if not result.success:
            self._append_message("AI", result.message)
            self._set_voice_input_recording(False)
            if result.message != "语音识别未启用":
                self._show_error_state()
            return

        self._append_message("System", result.message)
        self._set_voice_input_recording(True)

    def _stop_voice_input(self) -> None:
        if not self.stt_service:
            self._append_message("AI", "Speech-to-text service is not initialized")
            self._set_voice_input_recording(False)
            self._show_error_state()
            return

        result = self.stt_service.stop_recording()
        self._set_voice_input_recording(False)
        if not result.success:
            self._append_message("AI", result.message)
            self._show_error_state()
            return
        if result.audio_path is None:
            self._append_message("AI", "录音文件未生成")
            self._show_error_state()
            return

        self._append_message("System", f"Recording saved: {result.audio_path}")
        self._start_transcription(str(result.audio_path))

    def _start_transcription(self, audio_path: str) -> None:
        if not self.stt_service:
            return
        if self._transcription_thread and self._transcription_thread.isRunning():
            return

        self._set_character_state("thinking")
        self.voice_input_button.setEnabled(False)
        self.voice_input_button.setText("识别中")
        self._transcription_thread = QThread(self)
        self._transcription_worker = TranscriptionWorker(self.stt_service, audio_path)
        self._transcription_worker.moveToThread(self._transcription_thread)
        self._transcription_thread.started.connect(self._transcription_worker.run)
        self._transcription_worker.finished.connect(self._handle_transcription_result)
        self._transcription_worker.finished.connect(self._transcription_thread.quit)
        self._transcription_thread.finished.connect(self._transcription_worker.deleteLater)
        self._transcription_thread.finished.connect(self._transcription_thread.deleteLater)
        self._transcription_thread.finished.connect(self._clear_transcription_thread)
        self._transcription_thread.start()

    def _handle_transcription_result(self, success: bool, message: str, text: str) -> None:
        if success:
            self.input_edit.setPlainText(text)
            self._append_message("System", "语音识别完成，已填入输入框")
            self._set_character_state("idle")
        else:
            self._append_message("AI", message)
            self._show_error_state()
        self._set_voice_input_recording(False)

    def _clear_transcription_thread(self) -> None:
        self._transcription_worker = None
        self._transcription_thread = None

    def _set_voice_input_recording(self, recording: bool) -> None:
        self._is_recording = recording
        self.voice_input_button.setEnabled(True)
        self.voice_input_button.setText("停止录音" if recording else "语音输入")
        if recording:
            self._set_character_state("listening")

    def _analyze_screenshot(self) -> None:
        if not self.screenshot_service or not self.vision_service:
            self._append_message("AI", "Screenshot analysis service is not initialized")
            self._show_error_state()
            return
        if self._vision_thread and self._vision_thread.isRunning():
            return

        self._append_message("System", "Capturing screenshot for analysis...")
        self._set_character_state("thinking")
        self._set_screenshot_busy(True)

        self._vision_thread = QThread(self)
        self._vision_worker = ScreenshotAnalysisWorker(self.screenshot_service, self.vision_service)
        self._vision_worker.moveToThread(self._vision_thread)
        self._vision_thread.started.connect(self._vision_worker.run)
        self._vision_worker.finished.connect(self._handle_screenshot_analysis_result)
        self._vision_worker.failed.connect(self._handle_screenshot_analysis_error)
        self._vision_worker.finished.connect(self._vision_thread.quit)
        self._vision_worker.failed.connect(self._vision_thread.quit)
        self._vision_thread.finished.connect(self._vision_worker.deleteLater)
        self._vision_thread.finished.connect(self._vision_thread.deleteLater)
        self._vision_thread.finished.connect(self._clear_vision_thread)
        self._vision_thread.start()

    def _handle_screenshot_analysis_result(self, screenshot_path: str, result: str) -> None:
        self._append_message("System", f"Screenshot saved: {screenshot_path}")
        self._append_message("AI", result)
        self._update_recent_reply_bubble(result)
        self._save_memory_message("assistant", result)
        self._set_screenshot_busy(False)
        self._set_character_state("idle")

    def _handle_screenshot_analysis_error(self, message: str) -> None:
        self._append_message("AI", message)
        self._set_screenshot_busy(False)
        self._show_error_state()

    def _clear_vision_thread(self) -> None:
        self._vision_worker = None
        self._vision_thread = None

    def _set_screenshot_busy(self, busy: bool) -> None:
        self.screenshot_button.setEnabled(not busy)
        self.screenshot_button.setText("分析中" if busy else "截图分析")

    def open_settings(self) -> None:
        if self.settings_reload_callback:
            self.settings = self.settings_reload_callback()
        if self.settings is None:
            self._append_message("AI", "Settings are not initialized")
            return

        dialog = SettingsDialog(
            self.settings,
            parent=self,
            storage_service=self.storage_service,
            memory_cleared_callback=self._clear_memory_view,
        )
        if dialog.exec():
            if self.settings_reload_callback:
                self.settings = self.settings_reload_callback()
            self._sync_settings_to_services()
            self._append_message("System", "Settings saved")

    def _sync_settings_to_services(self) -> None:
        if self.settings is None:
            return
        for service in (
            self.chat_service,
            self.screenshot_service,
            self.vision_service,
            self.tts_service,
            self.stt_service,
            self.storage_service,
        ):
            if service is None:
                continue
            if hasattr(service, "settings"):
                service.settings = self.settings
            if hasattr(service, "provider") and hasattr(service.provider, "settings"):
                service.provider.settings = self.settings

    def _clear_memory_view(self) -> None:
        self.chat_view.clear()
        self._recent_reply_text = ""
        self.recent_reply_label.clear()
        self.recent_reply_label.setVisible(False)
        if self.chat_service is not None and hasattr(self.chat_service, "clear_history"):
            self.chat_service.clear_history()

    def hide_to_tray(self) -> None:
        self._save_current_window_state()
        self.hide()
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage("Desktop Companion AI", "Assistant hidden to system tray")

    def show_from_tray(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def exit_application(self) -> None:
        self._force_exit = True
        self._save_current_window_state()
        self._cleanup_chat_thread()
        self.tray_icon.hide()
        QApplication.quit()

    def _cleanup_chat_thread(self) -> None:
        if self._chat_thread and self._chat_thread.isRunning():
            self._chat_thread.quit()
            self._chat_thread.wait(1500)
        if self._vision_thread and self._vision_thread.isRunning():
            self._vision_thread.quit()
            self._vision_thread.wait(3000)
        if self._speech_thread and self._speech_thread.isRunning():
            self._speech_thread.quit()
            self._speech_thread.wait(3000)
        if self._transcription_thread and self._transcription_thread.isRunning():
            self._transcription_thread.quit()
            self._transcription_thread.wait(3000)
        if self._is_recording and self.stt_service is not None and hasattr(self.stt_service, "cancel_recording"):
            self.stt_service.cancel_recording()
            self._set_voice_input_recording(False)

    def _handle_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide_to_tray()
            else:
                self.show_from_tray()

    def closeEvent(self, event: QCloseEvent) -> None:
        self._save_current_window_state()
        if self._force_exit:
            self._cleanup_chat_thread()
            event.accept()
            return
        event.ignore()
        self.hide_to_tray()

    def moveEvent(self, event: QMoveEvent) -> None:
        super().moveEvent(event)
        if self.isVisible():
            self._save_current_window_state()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._update_character_pixmap()
        self._position_resize_grip()
        if self.isVisible():
            self._save_current_window_state()

    def _position_resize_grip(self) -> None:
        if self.resize_grip is None:
            return
        self.resize_grip.move(self.width() - RESIZE_GRIP_SIZE - 10, self.height() - RESIZE_GRIP_SIZE - 10)
        self.resize_grip.raise_()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._is_drag_area(event):
            self._is_dragging = True
            self._drag_moved = False
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            next_position = event.globalPosition().toPoint() - self._drag_offset
            if (next_position - self.pos()).manhattanLength() > 2:
                self._drag_moved = True
            self.move(next_position)
            event.accept()
            return
        self._update_resize_cursor(event.globalPosition().toPoint())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._is_dragging:
            was_click = not self._drag_moved
            self._is_dragging = False
            self._drag_moved = False
            self._save_current_window_state()
            if was_click:
                self.clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _is_drag_area(self, event: QMouseEvent) -> bool:
        widget = self.childAt(event.position().toPoint())
        if widget in {
            self.input_edit,
            self.chat_view,
            self.send_button,
            self.screenshot_button,
            self.test_voice_button,
            self.voice_input_button,
            self.minimize_button,
            self.close_button,
            self.resize_grip,
        }:
            return False
        return event.position().toPoint().y() <= self.character_label.geometry().bottom() + 18

    def _handle_click(self) -> None:
        self.logger.info("Desktop companion window clicked")
        if not self.chat_view.isVisible():
            self.chat_view.show()
            self.recent_reply_label.setVisible(bool(self._recent_reply_text))
