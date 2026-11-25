# Развёртывание

Локальный запуск описан в [README](../README.md)

## Render

Создаём PostgreSQL и Web Service в одном регионе, подключаем репозиторий, выбираем ветку main и окружение Python

| Переменная | Значение и назначение |
|---|---|
| PYTHON_VERSION | 3.14.5 |
| DJANGO_SECRET_KEY | Секретный ключ Django |
| DJANGO_DEBUG | False, отключение отладки |
| DJANGO_ALLOWED_HOSTS | Домен сайта без https:// |
| DJANGO_CSRF_TRUSTED_ORIGINS | Адрес сайта с https:// |
| DATABASE_URL | Подключение к PostgreSQL |

В DATABASE_URL указываем Internal Database URL для подключения Web Service к PostgreSQL внутри одного региона Render. Локальная SQLite и облачная PostgreSQL работают отдельно, данные автоматически не переносятся

Build Command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

Первые две команды устанавливают зависимости и собирают статические файлы, последняя выполняет миграции. На бесплатном тарифе Render миграции выполняются при сборке

Start Command:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

После запуска проверяем логи Render, работу сайта, API и сохранение данных в PostgreSQL
