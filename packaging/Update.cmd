@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  python -X utf8 update.py --apply
) else (
  py -3 -X utf8 update.py --apply
)
echo Refresh the plugin in Codex and start a new chat after a successful update.
pause
