from PyQt6 import QtCore, QtGui, QtWidgets
from .config import WinHotkey


class HotkeyCaptureDialog(QtWidgets.QDialog):
    def __init__(self, current_mods: int, current_key: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Hotkey")
        self.setModal(True)
        self.setFixedWidth(360)

        self._mods = current_mods
        self._key = current_key

        self._title = QtWidgets.QLabel("Press new hotkey")
        title_font = QtGui.QFont(self._title.font())
        title_font.setPointSize(title_font.pointSize() + 1)
        title_font.setBold(True)
        self._title.setFont(title_font)

        self._help = QtWidgets.QLabel(
            "Press a key combo with at least one modifier.\n"
            "Supported keys: A-Z, 0-9, F1-F12."
        )
        self._help.setWordWrap(True)

        self._current = QtWidgets.QLabel(f"Current: {self._format_hotkey(self._mods, self._key)}")
        self._current.setObjectName("CurrentHotkey")

        self._status = QtWidgets.QLabel("Waiting for input...")
        self._status.setObjectName("HotkeyStatus")

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        buttons.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._help)
        layout.addSpacing(6)
        layout.addWidget(self._current)
        layout.addWidget(self._status)
        layout.addStretch(1)
        layout.addWidget(buttons)

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.grabKeyboard()

    def closeEvent(self, event):
        self.releaseKeyboard()
        super().closeEvent(event)

    def get_hotkey(self) -> tuple[int, int]:
        return self._mods, self._key

    def keyPressEvent(self, event):
        key = event.key()
        if key in (
            QtCore.Qt.Key.Key_Shift,
            QtCore.Qt.Key.Key_Control,
            QtCore.Qt.Key.Key_Alt,
            QtCore.Qt.Key.Key_Meta,
        ):
            event.ignore()
            return

        mods = self._qt_mods_to_win(event.modifiers())
        if mods == 0:
            self._status.setText("Add a modifier (Ctrl/Shift/Alt/Win).")
            return

        vk = self._qt_key_to_vk(key)
        if vk is None:
            self._status.setText("Unsupported key. Use A-Z, 0-9, or F1-F12.")
            return

        self._mods = mods
        self._key = vk
        self.accept()

    @staticmethod
    def _qt_mods_to_win(mods: QtCore.Qt.KeyboardModifier) -> int:
        win_mods = 0
        if mods & QtCore.Qt.KeyboardModifier.ControlModifier:
            win_mods |= WinHotkey.MOD_CONTROL
        if mods & QtCore.Qt.KeyboardModifier.ShiftModifier:
            win_mods |= WinHotkey.MOD_SHIFT
        if mods & QtCore.Qt.KeyboardModifier.AltModifier:
            win_mods |= WinHotkey.MOD_ALT
        if mods & QtCore.Qt.KeyboardModifier.MetaModifier:
            win_mods |= WinHotkey.MOD_WIN
        return win_mods

    @staticmethod
    def _qt_key_to_vk(key: QtCore.Qt.Key) -> int | None:
        if QtCore.Qt.Key.Key_A <= key <= QtCore.Qt.Key.Key_Z:
            return ord(chr(key))
        if QtCore.Qt.Key.Key_0 <= key <= QtCore.Qt.Key.Key_9:
            return ord(chr(key))
        if QtCore.Qt.Key.Key_F1 <= key <= QtCore.Qt.Key.Key_F12:
            return 0x70 + (key - QtCore.Qt.Key.Key_F1)
        return None

    @staticmethod
    def _format_hotkey(mods: int, key: int) -> str:
        parts = []
        if mods & WinHotkey.MOD_CONTROL:
            parts.append("Ctrl")
        if mods & WinHotkey.MOD_SHIFT:
            parts.append("Shift")
        if mods & WinHotkey.MOD_ALT:
            parts.append("Alt")
        if mods & WinHotkey.MOD_WIN:
            parts.append("Win")
        if 0x70 <= key <= 0x7B:
            parts.append(f"F{key - 0x6F}")
        else:
            parts.append(chr(key))
        return "+".join(parts)
