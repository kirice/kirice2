#!/bin/bash
# Запуск RPG Fitness Tracker GUI
# Этот скрипт создает ярлык и запускает приложение

echo "🚀 Запуск RPG Fitness Tracker..."

# Проверка установки flet
if ! python -c "import flet" 2>/dev/null; then
    echo "⚠️  Flet не найден. Установка..."
    pip install flet
fi

# Запуск приложения
python gui_app.py
