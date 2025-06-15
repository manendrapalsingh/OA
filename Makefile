.PHONY: setup migrate test run docker-up docker-down

setup:
	python -m venv venv
	source venv/bin/activate && pip install -r requirements.txt

migrate:
	source venv/bin/activate && python manage.py migrate

test:
	source venv/bin/activate && python manage.py test

run:
	source venv/bin/activate && python manage.py runserver

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down 