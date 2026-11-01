.PHONY: install run migrate seed check test-clean
install:
	python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt && cp .env.example .env

migrate:
	python manage.py migrate

seed:
	python manage.py seed_bookings

run:
	python manage.py runserver 127.0.0.1:8000

test-clean:
	./verify_reproducibility.sh
