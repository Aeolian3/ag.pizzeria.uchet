#!/bin/bash
set -e

# Проверяем, существует ли папка alembic и файл конфигурации
if [ -d "/app/alembic" ] && [ -f "/app/alembic.ini" ]; then
    echo "Running Alembic migrations..."
    alembic upgrade head
else
    echo "Alembic not configured. Skipping migrations."
fi

echo "Starting bot..."
python -m main
