## Проблема: Ошибка 403 Forbidden при входе в панель администрирования

### Описание
При попытке авторизации в панели управления (`/admin/`) пользователь получает ошибку доступа, несмотря на корректность введённого пароля.

### Причина
Пользователь зарегистрирован в базе данных, однако в модели `auth_user` атрибут `is_staff` имеет значение `False`. Для доступа к интерфейсу Django Admin учётная запись обязательно должна иметь активный флаг служебного персонала (`is_staff=True`).

### Решение
1. Назначить флаг персонала через интерактивную оболочку Django:
```bash
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='d_migda'); u.is_staff = True; u.is_superuser = True; u.save()"