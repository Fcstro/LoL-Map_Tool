# LoL-Map_Tool

LoL-Map_Tool is a Windows-only PyQt6 utility that lets you select any screen region and view a zoomed live preview in a floating window. Its main purpose is to provide a larger, zoomed-in view of the minimap in League of Legends, but it can be used for any other on-screen region you want to zoom.

## Requirements
- Windows
- Python 3.11
- Pipenv
- PyQt6 (installed via Pipenv)

## Install
```bash
pipenv install
```

## Run
```bash
pipenv run python main.py
```

## Build (Windows .exe)
```powershell
.\scripts\build.ps1
```
Or from cmd:
```bat
scripts\build.bat
```
The executable will be at `dist\LoL-Map_Tool.exe`.
If you want an embedded icon, place it at `assets/icons/lolmapcam.ico` (already wired into the build scripts).

## Usage
1. Press `Ctrl+Shift+S` to start the selection overlay.
2. Drag to select a region and release to open the preview window.
3. Click `Cancel` to stop selection.

## Controls
- Zoom in/out buttons or mouse wheel
- Freeze/Live toggle
- Reselect button
- Hotkey button (set a new hotkey)
- Close button
- Opacity slider
- Drag the title bar to move
- Resize using the size grip

## Configuration
You can adjust the hotkey and behavior in `app/config.py` (hotkey modifiers/key, zoom limits, default opacity, etc.).
The app version is defined in `app/version.py`.

## Troubleshooting
- If you see a hotkey registration warning, another app may already be using `Ctrl+Shift+S`.

## Changelog
### 0.8.2
- Added responsive title bar layouts for small widths (compact/tiny modes).
- Hides labels and the zoom reset button on narrow windows to prevent overlap.
- Shortens button labels and shrinks the opacity slider at very small sizes.

### 0.8.1
- Made the title bar more responsive at small widths.
- Reduced large gaps in the header when the window is wide.
- Increased header height to prevent text clipping.

### 0.8.0
- Moved the Opacity and Zoom labels to the right of their controls in the title bar.
- Added a title bar status indicator (IDLE/LIVE/PAUSED/NO SIGNAL).
- Tray tooltip now reflects the current status.
- Tray notification appears when the preview is minimized.
