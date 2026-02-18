from PyQt6 import QtCore, QtGui, QtWidgets
from .capture import CaptureManager
from .config import AppConfig


class TitleBar(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self._drag_pos = None
        self.setFixedHeight(32)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


class PreviewWindow(QtWidgets.QWidget):
    minimized = QtCore.pyqtSignal()
    status_changed = QtCore.pyqtSignal(str)

    def __init__(self, on_reselect, on_change_hotkey, on_close_app, config: AppConfig, version: str):
        super().__init__()
        self._config = config
        self._version = version
        self._on_close_app = on_close_app
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
            | QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setMinimumSize(240, 180)
        self.setWindowTitle(f"LoL-Map_Tool v{self._version}")

        self._rect = None
        self._zoom = 1.0
        self._frozen = False
        self._capture = CaptureManager()
        self._on_reselect = on_reselect
        self._on_change_hotkey = on_change_hotkey

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._update_frame)

        self._label = QtWidgets.QLabel()
        self._label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._label.setObjectName("Preview")

        self._title = TitleBar(self)
        self._title.setObjectName("TitleBar")
        self._title.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self._title.customContextMenuRequested.connect(self._show_title_menu)

        self._btn_zoom_in = QtWidgets.QToolButton()
        self._btn_zoom_in.setText("+")
        self._btn_zoom_out = QtWidgets.QToolButton()
        self._btn_zoom_out.setText("-")
        self._btn_zoom_reset = QtWidgets.QToolButton()
        self._btn_zoom_reset.setText("Reset")
        self._btn_freeze = QtWidgets.QToolButton()
        self._btn_freeze.setText("Freeze")
        self._btn_reselect = QtWidgets.QToolButton()
        self._btn_reselect.setText("Reselect")
        self._btn_hotkey = QtWidgets.QToolButton()
        self._btn_hotkey.setText("Hotkey")
        self._btn_minimize = QtWidgets.QToolButton()
        self._btn_minimize.setText("_")
        self._btn_close = QtWidgets.QToolButton()
        self._btn_close.setText("X")

        self._btn_zoom_in.clicked.connect(lambda: self._set_zoom(self._zoom * self._config.zoom_step))
        self._btn_zoom_out.clicked.connect(lambda: self._set_zoom(self._zoom / self._config.zoom_step))
        self._btn_zoom_reset.clicked.connect(self._reset_zoom)
        self._btn_freeze.clicked.connect(self._toggle_freeze)
        self._btn_reselect.clicked.connect(self._on_reselect)
        self._btn_hotkey.clicked.connect(self._on_change_hotkey)
        self._btn_minimize.clicked.connect(self.showMinimized)
        self._btn_close.clicked.connect(self._on_close_app)

        title_layout = QtWidgets.QHBoxLayout(self._title)
        title_layout.setContentsMargins(8, 0, 8, 0)
        title_layout.setSpacing(6)

        self._opacity_label = QtWidgets.QLabel("Opacity")
        self._opacity_label.setObjectName("TitleLabel")
        self._opacity = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self._opacity.setFixedWidth(110)
        self._opacity.setRange(30, 100)
        self._opacity.setValue(int(self._config.default_opacity * 100))
        self._opacity.valueChanged.connect(self._set_opacity)

        opacity_row = QtWidgets.QHBoxLayout()
        opacity_row.setSpacing(6)
        opacity_row.addWidget(self._opacity)
        opacity_row.addWidget(self._opacity_label)

        opacity_wrap = QtWidgets.QWidget()
        opacity_wrap.setLayout(opacity_row)
        opacity_wrap.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )

        self._zoom_label = QtWidgets.QLabel("Zoom")
        self._zoom_label.setObjectName("TitleLabel")
        self._zoom_value = QtWidgets.QLabel(self._format_zoom(self._zoom))
        self._zoom_value.setObjectName("ZoomValue")
        zoom_row = QtWidgets.QHBoxLayout()
        zoom_row.setSpacing(6)
        zoom_row.addWidget(self._zoom_value)
        zoom_row.addWidget(self._zoom_label)
        zoom_row.addSpacing(6)
        zoom_row.addWidget(self._btn_zoom_out)
        zoom_row.addWidget(self._btn_zoom_in)
        zoom_row.addWidget(self._btn_zoom_reset)

        zoom_wrap = QtWidgets.QWidget()
        zoom_wrap.setLayout(zoom_row)
        zoom_wrap.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )

        self._status = QtWidgets.QLabel("IDLE")
        self._status.setObjectName("StatusIndicator")
        self._status.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._status.setMinimumWidth(64)
        self._status_mode = "normal"

        left_group = QtWidgets.QWidget()
        left_layout = QtWidgets.QHBoxLayout(left_group)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        left_layout.addWidget(opacity_wrap)
        left_layout.addWidget(zoom_wrap)
        left_group.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )

        right_group = QtWidgets.QWidget()
        right_layout = QtWidgets.QHBoxLayout(right_group)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        right_layout.addWidget(self._status)
        right_layout.addWidget(self._btn_freeze)
        right_layout.addWidget(self._btn_reselect)
        right_layout.addWidget(self._btn_hotkey)
        right_layout.addWidget(self._btn_minimize)
        right_layout.addWidget(self._btn_close)
        right_group.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )

        title_layout.addWidget(left_group, 1)
        title_layout.addWidget(right_group, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        layout.addWidget(self._title)
        layout.addWidget(self._label, 1)

        self._size_grip = QtWidgets.QSizeGrip(self)
        layout.addWidget(self._size_grip, 0, QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignRight)

        self._apply_opacity(self._config.default_opacity, update_slider=True)
        self._last_pix = None

        self._btn_zoom_in.setToolTip("Zoom in")
        self._btn_zoom_out.setToolTip("Zoom out")
        self._btn_zoom_reset.setToolTip("Reset zoom")
        self._btn_freeze.setToolTip("Toggle live/freeze")
        self._btn_reselect.setToolTip("Reselect capture area")
        self._btn_hotkey.setToolTip("Change hotkey")
        self._btn_minimize.setToolTip("Minimize window")
        self._btn_close.setToolTip("Close app")
        self._status.setToolTip("Capture status")

        for btn in (
            self._btn_zoom_in,
            self._btn_zoom_out,
            self._btn_zoom_reset,
            self._btn_freeze,
            self._btn_reselect,
            self._btn_hotkey,
            self._btn_minimize,
            self._btn_close,
        ):
            btn.setFixedHeight(22)
            btn.setMinimumWidth(24)

        self._btn_texts = {
            "freeze": self._btn_freeze.text(),
            "reselect": self._btn_reselect.text(),
            "hotkey": self._btn_hotkey.text(),
        }

        self._set_status("idle")
        self._apply_title_layout(self.width())

    def set_rect(self, rect: QtCore.QRect):
        self._rect = rect
        self._frozen = False
        self._btn_freeze.setText("Freeze")
        self._zoom = 1.0
        self._update_zoom_label()
        self._set_status("live")
        self._timer.start(self._config.capture_fps_ms)
        self._update_frame()
        self.show()
        self.raise_()

    def stop_preview(self):
        self._stop_capture()
        self.hide()

    def show_if_ready(self) -> bool:
        if not self._rect:
            return False
        self.show()
        self.raise_()
        return True

    def hideEvent(self, event):
        super().hideEvent(event)
        self._stop_capture()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.WindowStateChange and self.isMinimized():
            self.minimized.emit()
        super().changeEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_title_layout(event.size().width())
        self._render_pixmap()

    def _toggle_freeze(self):
        self._frozen = not self._frozen
        self._btn_freeze.setText("Live" if self._frozen else "Freeze")
        if self._frozen:
            self._set_status("paused")
            self._timer.stop()
        else:
            self._set_status("live")
            self._timer.start(self._config.capture_fps_ms)

    def _set_zoom(self, zoom):
        self._zoom = max(self._config.zoom_min, min(zoom, self._config.zoom_max))
        self._update_zoom_label()
        self._update_frame()

    def _set_opacity(self, value):
        self._apply_opacity(value / 100.0, update_slider=False)

    def _apply_opacity(self, value, update_slider=False):
        self.setWindowOpacity(value)
        if update_slider:
            self._opacity.blockSignals(True)
            self._opacity.setValue(int(round(value * 100)))
            self._opacity.blockSignals(False)

    def _reset_zoom(self):
        self._set_zoom(1.0)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self._set_zoom(self._zoom * self._config.zoom_step)
        else:
            self._set_zoom(self._zoom / self._config.zoom_step)

    def _update_frame(self):
        if not self._rect:
            return
        pix = self._capture.grab_rect(self._rect)
        if pix.isNull():
            self._label.clear()
            self._label.setText("No signal")
            self._set_status("no_signal")
            return
        self._label.setText("")
        self._last_pix = pix
        self._set_status("live")
        self._render_pixmap()

    def _render_pixmap(self):
        if not self._last_pix or not self._rect:
            return
        zoomed_size = QtCore.QSize(
            max(1, int(self._rect.width() * self._zoom)),
            max(1, int(self._rect.height() * self._zoom)),
        )
        label_size = self._label.size()
        target_size = QtCore.QSize(
            max(zoomed_size.width(), label_size.width()),
            max(zoomed_size.height(), label_size.height()),
        )
        scaled = self._last_pix.scaled(
            target_size,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setPixmap(scaled)

    def _close_preview(self):
        self._stop_capture()
        self.hide()

    def _stop_capture(self):
        self._timer.stop()
        self._frozen = False
        self._btn_freeze.setText("Freeze")
        self._set_status("idle")

    def _format_zoom(self, zoom):
        return f"{zoom:.2f}".rstrip("0").rstrip(".") + "x"

    def _update_zoom_label(self):
        self._zoom_value.setText(self._format_zoom(self._zoom))

    def _set_status(self, status: str):
        palette = {
            "idle": ("IDLE", "#9AA4B2"),
            "live": ("LIVE", "#5ED5FF"),
            "paused": ("PAUSED", "#F2C94C"),
            "no_signal": ("NO SIGNAL", "#F2994A"),
        }
        text, color = palette.get(status, ("IDLE", "#9AA4B2"))
        if self._status_mode == "tiny":
            display = "•"
            self._status.setFixedWidth(12)
        else:
            display = text
            self._status.setFixedWidth(64)
        self._status.setText(display)
        self._status.setStyleSheet(f"color: {color}; font-weight: 600;")
        self.status_changed.emit(text)

    def _apply_title_layout(self, width: int):
        if width < 360:
            mode = "tiny"
        elif width < 460:
            mode = "compact"
        else:
            mode = "normal"

        if mode == "normal":
            self._opacity_label.show()
            self._zoom_label.show()
            self._btn_zoom_reset.show()
            self._opacity.setFixedWidth(110)
            self._btn_reselect.setText(self._btn_texts["reselect"])
            self._btn_hotkey.setText(self._btn_texts["hotkey"])
            self._status_mode = "normal"
        elif mode == "compact":
            self._opacity_label.hide()
            self._zoom_label.hide()
            self._btn_zoom_reset.hide()
            self._opacity.setFixedWidth(90)
            self._btn_reselect.setText("Select")
            self._btn_hotkey.setText("Key")
            self._status_mode = "normal"
        else:
            self._opacity_label.hide()
            self._zoom_label.hide()
            self._btn_zoom_reset.hide()
            self._opacity.setFixedWidth(70)
            self._btn_reselect.setText("Sel")
            self._btn_hotkey.setText("Key")
            self._status_mode = "tiny"

        # Refresh status display to match current mode.
        self._set_status("live" if self._timer.isActive() else ("paused" if self._frozen else "idle"))

    def _show_title_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        action_freeze = menu.addAction("Freeze" if not self._frozen else "Live")
        action_reselect = menu.addAction("Reselect")
        action_hotkey = menu.addAction("Hotkey")
        menu.addSeparator()
        action_exit = menu.addAction("Exit")

        action = menu.exec(self._title.mapToGlobal(pos))
        if action == action_freeze:
            self._toggle_freeze()
        elif action == action_reselect:
            self._on_reselect()
        elif action == action_hotkey:
            self._on_change_hotkey()
        elif action == action_exit:
            self._on_close_app()
