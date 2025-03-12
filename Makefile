.PHONY: venv install test clean build run lint run-local black coverage

venv:
	python3 -m venv .venv

install:
	pip install -r requirements.txt

test:
	pytest -v --cov=.

coverage:
	coverage report

clean:
	rm -rf __pycache__ .pytest_cache

build:
	docker build -t pokemon-agent-system .

run:
	docker run -p 8000:8000 --env-file .env pokemon-agent-system

run-local:
	uvicorn main:app --reload

lint:
	flake8 --exclude .venv

black:
	black . --exclude .venv


