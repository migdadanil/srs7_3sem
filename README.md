# NOTHING . RENT

[![Reproducibility CI](https://github.com/migdadanil/srs7_3sem/actions/workflows/reproducibility.yml/badge.svg)](https://github.com/migdadanil/srs7_3sem/actions)
![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.15-red?logo=django)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0_Swagger-85EA2D?logo=swagger&logoColor=black)

Веб-приложение для учета и бронирования съемочного оборудования. Сервис автоматизирует распределение техники между проектами, фиксирует изменения статусов заявок и ведет журнал действий.

---

## Возможности

* **Учет доступности**: отображение текущего остатка оборудования по категориям (камеры, оптика, свет, звук).
* **Контроль статусов**: перевод заявок по этапам (`draft` → `confirmed` → `in_use` → `returned` / `cancelled`).
* **Предотвращение дефицита**: блокировка записей на уровне транзакций базы данных для исключения повторного бронирования одной единицы.
* **Журнал аудита**: автоматическая фиксация времени, пользователя и характера изменений в отдельной таблице событий.
* **Разграничение доступа**: фильтрация данных на стороне сервера — пользователь видит только собственные бронирования, персонал имеет доступ к полному списку.

---

## Стек технологий

* **Backend**: Python 3.12, Django 5.1, Django REST Framework, drf-spectacular.
* **Базы данных**: SQLite (локальная среда), PostgreSQL (продакшн).
* **Frontend**: JavaScript (Fetch API, CSRF), CSS.
* **Инфраструктура**: Gunicorn, WhiteNoise, GitHub Actions, Makefile.

---

## Быстрый старт

Для работы требуются Python 3.10+ и Git.

### Запуск через Makefile

```bash
make install   # создание venv, установка зависимостей, подготовка .env
make migrate   # применение миграций базы данных
make seed      # загрузка тестовой номенклатуры и заявок
make run       # запуск локального dev-сервера
