@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto use_python
py -3 -X utf8 "%~dp0install.py" --apply
goto finished
:use_python
python -X utf8 "%~dp0install.py" --apply
:finished
if errorlevel 1 echo Installation failed. See the message above.
pause
