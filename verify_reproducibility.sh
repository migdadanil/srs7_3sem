set -e

echo "=== [1/6] Создание изолированного каталога в /tmp ==="
TEMP_DIR=$(mktemp -d /tmp/nothing_rent_test_XXXXXX)
cd "$TEMP_DIR"
echo "Директория: $TEMP_DIR"

echo "=== [2/6] Клонирование чистого репозитория ==="
git clone https://github.com/migdadanil/srs7_3sem.git .

echo "=== [3/6] Развертывание виртуального окружения ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== [4/6] Применение конфигурации .env.example ==="
cp .env.example .env

echo "=== [5/6] Миграции и сидинг демо-данных ==="
python manage.py migrate
python manage.py seed_bookings

echo "=== [6/6] Проверка целостности Django ==="
python manage.py check

echo "=========================================================="
echo "✔ ВОСПРОИЗВОДИМОСТЬ ПОДТВЕРЖДЕНА: проект готов к запуску!"
echo "Для старта выполните: cd $TEMP_DIR && source venv/bin/activate && python manage.py runserver"
echo "=========================================================="
