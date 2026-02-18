import os
import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from .config import CONFIG, WinHotkey
from .hotkey import HotkeyFilter, register_hotkey, unregister_hotkey
from .hotkey_dialog import HotkeyCaptureDialog
from .overlay import SnipOverlay
from .preview import PreviewWindow
from .style import Style
from .version import __version__


class App(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setStyleSheet(Style.BASE)
        self.setApplicationName("LoL-Map_Tool")
        self.setApplicationVersion(__version__)
        self.setQuitOnLastWindowClosed(False)

        self._overlay = SnipOverlay(CONFIG)
        self._preview = PreviewWindow(self._on_hotkey, self._change_hotkey, self.quit, CONFIG, __version__)
        self._overlay.selectionMade.connect(self._preview.set_rect)
        self._overlay.canceled.connect(self._preview.stop_preview)
        self._preview.minimized.connect(self._on_preview_minimized)
        self._preview.status_changed.connect(self._on_preview_status_changed)

        self._hotkey_filter = HotkeyFilter(self._on_hotkey)
        self.installNativeEventFilter(self._hotkey_filter)

        self._tray = self._init_tray()

        # Register global hotkey
        self._hotkey_id = 1
        self._hotkey_mods = CONFIG.hotkey_mods
        self._hotkey_key = CONFIG.hotkey_key
        if not self._register_hotkey():
            hotkey_text = self._format_hotkey(CONFIG.hotkey_mods, CONFIG.hotkey_key)
            QtWidgets.QMessageBox.warning(
                None,
                "Hotkey Error",
                f"Failed to register hotkey {hotkey_text}. It may be in use by another app.",
            )

        self.aboutToQuit.connect(self._cleanup)

    def _on_hotkey(self):
        self._overlay.start()

    def _cleanup(self):
        unregister_hotkey(self._hotkey_id)

    def _init_tray(self) -> QtWidgets.QSystemTrayIcon:
        icon = self._load_tray_icon()
        tray = QtWidgets.QSystemTrayIcon(icon, self)
        tray.setToolTip(f"LoL-Map_Tool v{__version__} (IDLE)")

        menu = QtWidgets.QMenu()
        action_select = menu.addAction("Select Region")
        action_select.triggered.connect(self._on_hotkey)

        action_show = menu.addAction("Show Preview")
        action_show.triggered.connect(self._show_or_select)

        action_hotkey = menu.addAction("Change Hotkey")
        action_hotkey.triggered.connect(self._change_hotkey)

        menu.addSeparator()
        action_quit = menu.addAction("Quit")
        action_quit.triggered.connect(self.quit)

        tray.setContextMenu(menu)
        tray.activated.connect(self._on_tray_activated)
        tray.show()
        return tray

    def _load_tray_icon(self) -> QtGui.QIcon:
        ico_path = self._resource_path("assets/icons/lolmapcam.ico")
        if QtCore.QFile.exists(ico_path):
            return QtGui.QIcon(ico_path)
        return self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon)

    @staticmethod
    def _resource_path(relative_path: str) -> str:
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    def _show_or_select(self):
        if not self._preview.show_if_ready():
            self._on_hotkey()

    def _on_tray_activated(self, reason: QtWidgets.QSystemTrayIcon.ActivationReason):
        if reason in (
            QtWidgets.QSystemTrayIcon.ActivationReason.Trigger,
            QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self._show_or_select()

    def _on_preview_minimized(self):
        if self._tray:
            self._tray.showMessage(
                "LoL-Map_Tool",
                "Preview minimized. Click the tray icon to restore it.",
                QtWidgets.QSystemTrayIcon.MessageIcon.Information,
                2500,
            )

    def _on_preview_status_changed(self, status: str):
        if self._tray:
            self._tray.setToolTip(f"LoL-Map_Tool v{__version__} ({status})")

    def _register_hotkey(self) -> bool:
        return register_hotkey(self._hotkey_id, self._hotkey_mods, self._hotkey_key)

    def _change_hotkey(self):
        dialog = HotkeyCaptureDialog(self._hotkey_mods, self._hotkey_key)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        new_mods, new_key = dialog.get_hotkey()
        old_mods, old_key = self._hotkey_mods, self._hotkey_key

        unregister_hotkey(self._hotkey_id)
        self._hotkey_mods, self._hotkey_key = new_mods, new_key
        if not self._register_hotkey():
            # Revert on failure
            self._hotkey_mods, self._hotkey_key = old_mods, old_key
            self._register_hotkey()
            QtWidgets.QMessageBox.warning(
                None,
                "Hotkey Error",
                "Failed to register the new hotkey. It may be in use by another app.",
            )
            return

        QtWidgets.QMessageBox.information(
            None,
            "Hotkey Updated",
            f"New hotkey set to {self._format_hotkey(self._hotkey_mods, self._hotkey_key)}.",
        )

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
