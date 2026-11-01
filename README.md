# NOTHING . RENT // Управление арендой съемочной техники

[![Reproducibility CI](https://github.com/migdadanil/srs7_3sem/actions/workflows/reproducibility.yml/badge.svg)](https://github.com/migdadanil/srs7_3sem/actions)
![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.15-red?logo=django)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0_Swagger-85EA2D?logo=swagger&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

Веб-приложение для автоматизации бронирования и диспетчеризации съемочного оборудования кафедры и студенческих медиапроектов. Интерфейс выполнен в монохромной стилистике Nothing OS со стеклянными карточками, динамическим видеофоном и инспектором аудита.

---

## 1. Назначение и функциональность
* **Каталог оборудования**: оперативный учет доступности камер, оптики, света и звука с визуальным контролем остатков.
* **Конечный автомат бронирования (State Machine)**: жесткий регламент состояний (`Черновик` → `Забронировано` → `На съемке` → `Возвращено` / `Аннулировано`).
* **Контроль дефицита**: атомарная блокировка строк на уровне СУБД (`select_for_update`) исключает овербукинг при одновременных запросах.
* **Журнал аудита (Audit Trail)**: неизменяемый лог каждого изменения статуса с фиксацией времени и инициатора.
* **Изоляция данных**: операторы видят только свои заявки, сотрудники кафедры — общий производственный поток.

---

## 2. Технологический стек
* **Бэкенд**: Python 3.12+, Django 5.1, Django REST Framework, drf-spectacular.
* **СУБД**: SQLite (локально) / PostgreSQL 16 (облако Render).
* **Фронтенд**: Нативный JavaScript (ES6+ Fetch API, CSRF-токены), CSS3 Glassmorphism, Video Background.
* **CI/CD & DevOps**: GitHub Actions CI, Gunicorn, WhiteNoise, Makefile.

---

## 3. Быстрый старт (локальный запуск)

```bash
git clone [https://github.com/migdadanil/srs7_3sem.git](https://github.com/migdadanil/srs7_3sem.git)
cd srs7_3sem
make install
make migrate
make seed
make run