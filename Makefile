.PHONY: venv install tests clean docker-build docker-run lint run-local black coverage test-unittests test-integration

venv:
	python3 -m venv .venv

install:
	pip install -r requirements.txt

tests:
	pytest -v

coverage:
	pytest -v --cov=. -m "not integration"
	coverage report

clean:
	rm -rf __pycache__ .pytest_cache

docker-build:
	docker build -t pokemon-agent-system .

docker-run:
	docker run -p 8000:8000 --env-file .env pokemon-agent-system

run-local:
	uvicorn main:app --reload

lint:
	flake8

black:
	black . --exclude .venv

test-unittests:
	pytest -v -m "not integration"

test-integration:
	pytest -v -m integration

create-env:
	@echo "Creating .env file..."
	@echo "OPENAI_MODEL_NAME=<your_openai_model_name>" > .env
	@echo "OPENAI_API_KEY=<your_openai_api_key>" >> .env
	@echo "" >> .env
	@echo "LOCAL_DEVELOPMENT=true" >> .env
	@echo "GROQ_MODEL_NAME=<your_groq_model_name>" >> .env
	@echo "GROQ_API_KEY=<your_groq_api_key>" >> .env
	@echo "" >> .env
	@echo "# At least one of the above configurations must be provided for the project to function properly." >> .env
	@echo "" >> .env
	@echo "LANGSMITH_TRACING=true" >> .env
	@echo "LANGSMITH_ENDPOINT=<your_langsmith_endpoint>" >> .env
	@echo "LANGSMITH_API_KEY=<your_langsmith_api_key>" >> .env
	@echo "LANGSMITH_PROJECT=<your_langsmith_project>" >> .env
	@echo ".env file created successfully!"
