import ctypes
from ctypes import wintypes
from PyQt6 import QtCore
from .config import WinHotkey

user32 = ctypes.windll.user32


class HotkeyFilter(QtCore.QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def nativeEventFilter(self, eventType, message):
        if eventType != "windows_generic_MSG":
            return False, 0
        msg = wintypes.MSG.from_address(message.__int__())
        if msg.message == WinHotkey.WM_HOTKEY:
            self._callback()
            return True, 0
        return False, 0


def register_hotkey(hotkey_id: int, mods: int, key: int) -> bool:
    return bool(user32.RegisterHotKey(None, hotkey_id, mods, key))


def unregister_hotkey(hotkey_id: int) -> None:
    user32.UnregisterHotKey(None, hotkey_id)
