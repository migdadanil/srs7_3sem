# Восстановление данных

Для проверки восстановления используется отдельная SQLite с демонстрационными данными, рабочая база проекта при этом не изменяется

```bash
(
set -e

TEST_DIR=$(mktemp -d)
export DATABASE_URL="sqlite:///$TEST_DIR/test.sqlite3"
export DJANGO_DEBUG=True
export DJANGO_SECRET_KEY=local-development-only

venv/bin/python manage.py migrate
venv/bin/python manage.py seed_gear
venv/bin/python manage.py seed_bookings

sqlite3 "$TEST_DIR/test.sqlite3" ".backup '$TEST_DIR/backup.sqlite3'"
mv "$TEST_DIR/test.sqlite3" "$TEST_DIR/old.sqlite3"
sqlite3 "$TEST_DIR/test.sqlite3" ".restore '$TEST_DIR/backup.sqlite3'"

sqlite3 "$TEST_DIR/test.sqlite3" "PRAGMA integrity_check;"
diff <(sqlite3 "$TEST_DIR/old.sqlite3" .dump) <(sqlite3 "$TEST_DIR/test.sqlite3" .dump)
)
```

При проверке были восстановлены все 6 бронирований, содержимое исходной и восстановленной баз совпало, проверка целостности вернула ok
