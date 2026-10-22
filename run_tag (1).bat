@echo off
cd /d "%~dp0"
where py >nul 2>nul && (set PY=py) || (set PY=python)
%PY% -c "import pygame" >nul 2>nul && goto run
echo Installing pygame-ce (works on new Python versions, including 3.14)...
%PY% -m pip install pygame-ce
%PY% -c "import pygame" >nul 2>nul || (
  echo.
  echo Could not install pygame-ce. Try Python 3.12 or 3.13 from python.org, then run this again.
  pause
  exit /b 1
)
:run
%PY% tag_game.py
if errorlevel 1 pause
