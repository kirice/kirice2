@echo off
title RPG Fitness Tracker
echo Запуск фитнес-трекера...
echo.

REM Проверка наличия Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ОШИБКА: Python не найден в системе!
    pause
    exit /b
)

REM Запуск приложения
REM Если у вас несколько версий Python, замените 'python' на полный путь, например:
REM "C:\Program Files\Python310\python.exe" gui_app.py
python gui_app.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Произошла ошибка при запуске.
    echo Возможно, не установлена библиотека flet.
    echo Выполните команду: pip install flet
    pause
)