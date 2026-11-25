#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TEMP_DIR="$(mktemp -d)"
SERVER_PID=""

# Останавливаем сервер и удаляем временные файлы
cleanup() {
    if [ -n "$SERVER_PID" ]; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi

    rm -rf "$TEMP_DIR"
}

trap cleanup EXIT

echo "[1/9] Создание чистой копии проекта"
git -C "$ROOT" archive HEAD | tar -xf - -C "$TEMP_DIR"
cd "$TEMP_DIR"

echo "[2/9] Создание виртуального окружения"
python3.14 -m venv venv
source venv/bin/activate

echo "[3/9] Установка зависимостей"
python -m pip install -r requirements.txt
python -m pip check

echo "[4/9] Подготовка конфигурации"
unset DJANGO_SECRET_KEY DJANGO_DEBUG
unset DJANGO_ALLOWED_HOSTS DJANGO_CSRF_TRUSTED_ORIGINS
unset DATABASE_URL

cp .env.example .env

echo "[5/9] Миграции и демонстрационные данные"
python manage.py migrate --noinput
python manage.py seed_bookings

echo "[6/9] Проверка Django и сбор статики"
python manage.py check
python manage.py collectstatic --noinput

echo "[7/9] Запуск тестового сервера"
PORT=$(python -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')

BASE_URL="http://127.0.0.1:$PORT"

python manage.py runserver "127.0.0.1:$PORT" \
    --noreload > server.log 2>&1 &

SERVER_PID=$!

echo "[8/9] Проверка HTTP-ответов"

READY=0

for attempt in $(seq 1 30); do
    if curl -fsL "$BASE_URL/" -o /dev/null; then
        READY=1
        break
    fi
    sleep 1
done

if [ "$READY" -ne 1 ]; then
    echo "Ошибка: сервер не запустился"
    tail -n 30 server.log
    exit 1
fi

check_url() {
    CODE=$(curl -sSL -o /dev/null \
        -w '%{http_code}' "$BASE_URL$1")

    echo "HTTP $CODE — $1"

    if [ "$CODE" != "200" ]; then
        exit 1
    fi
}

check_url "/"
check_url "/api/schema/"
check_url "/api/docs/"
check_url "/static/rentals/img/aurora-loop.mp4"

echo "[9/9] Завершение проверки"
echo "=========================================="
echo "SUCCESS: чистый запуск подтвержден"
echo "Все проверяемые ресурсы доступны"
echo "=========================================="
