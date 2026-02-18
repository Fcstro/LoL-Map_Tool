from dataclasses import dataclass


class WinHotkey:
    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    MOD_SHIFT = 0x0004
    MOD_WIN = 0x0008
    WM_HOTKEY = 0x0312


@dataclass(frozen=True)
class AppConfig:
    hotkey_mods: int = WinHotkey.MOD_CONTROL | WinHotkey.MOD_SHIFT
    hotkey_key: int = ord("S")
    capture_fps_ms: int = 33  # ~30 FPS
    zoom_min: float = 0.2
    zoom_max: float = 6.0
    zoom_step: float = 1.1
    default_opacity: float = 0.95
    min_selection_px: int = 5


CONFIG = AppConfig()
