1. Создать базу данных PostgreSQL на Render.
2. Подключить Web Service к репозиторию.
3. Build Command: pip install -r requirements.txt && python manage.py migrate
4. Start Command: gunicorn config.wsgi:application
