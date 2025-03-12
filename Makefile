.PHONY: test clean build run lint run-local

test:
	pytest -v

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


