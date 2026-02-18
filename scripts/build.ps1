$ErrorActionPreference = "Stop"

if (-not (Get-Command pipenv -ErrorAction SilentlyContinue)) {
    Write-Error "pipenv not found. Install pipenv first."
}

pipenv install
pipenv run pyinstaller --noconfirm --onefile --windowed --name "LoL-Map_Tool" --icon "assets\\icons\\lolmapcam.ico" --add-data "assets\\icons\\lolmapcam.ico;assets\\icons" main.py

Write-Host "Build complete. Output is in dist\\LoL-Map_Tool.exe"
