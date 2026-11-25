.DEFAULT_GOAL := help

PYTHON ?= python3.14
VENV_PYTHON = venv/bin/python

.PHONY: help install migrate seed run check test static test-clean

help:
	@echo "NOTHING.RENT — команды разработчика"
	@echo "make install    — установка зависимостей"
	@echo "make migrate    — миграции базы данных"
	@echo "make seed       — демонстрационные данные"
	@echo "make run        — запуск приложения"
	@echo "make check      — проверка Django"
	@echo "make test       — автоматические тесты"
	@echo "make static     — сбор статических файлов"
	@echo "make test-clean — проверка чистого запуска"

install:
	test -x $(VENV_PYTHON) || $(PYTHON) -m venv venv
	$(VENV_PYTHON) -m pip install -r requirements.txt
	test -f .env || cp .env.example .env

migrate:
	$(VENV_PYTHON) manage.py migrate

seed:
	$(VENV_PYTHON) manage.py seed_gear
	$(VENV_PYTHON) manage.py seed_bookings

run:
	$(VENV_PYTHON) manage.py runserver 127.0.0.1:8000

check:
	$(VENV_PYTHON) manage.py check

test:
	$(VENV_PYTHON) manage.py test

static:
	$(VENV_PYTHON) manage.py collectstatic --noinput

test-clean:
	bash verify_reproducibility.sh
