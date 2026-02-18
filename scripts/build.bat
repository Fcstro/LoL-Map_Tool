@echo off
setlocal

where pipenv >nul 2>nul
if errorlevel 1 (
  echo pipenv not found. Install pipenv first.
  exit /b 1
)

pipenv install
pipenv run pyinstaller --noconfirm --onefile --windowed --name "LoL Map Tool" --icon "assets\\icons\\lolmapcam.ico" --add-data "assets\\icons\\lolmapcam.ico;assets\\icons" main.py

echo Build complete. Output is in dist\LoL Map Tool.exe
