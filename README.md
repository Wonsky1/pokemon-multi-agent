
# Pokémon Multi-Agent System

LLM-powered question-answering system for Pokémon-related queries, built with a multi-agent architecture.

This project implements a specialized AI system designed to answer questions about Pokémon, with particular focus on analyzing hypothetical battle scenarios. The system uses multiple specialized LLM agents that coordinate through a graph-based workflow to handle different types of queries.

It uses GROQ model for local development and OpenAI model for deployment


## Agents graph structure diagram

![agents graph structure diagram](https://i.imgur.com/PEvyMKn.png)

## Contents
1. [Environment Variables](#environment-variables)
2. [Run Locally](#run-locally)
3. [Run Locally with Docker](#run-locally-using-docker)
4. [API Reference](#api-reference)
5. [Troubleshooting](#troubleshooting)
6. [Running Tests](#running-tests)
7. [Documentation](#documentation)
8. [Make commands](#make-commands)
9. [FAQ](#faq)

## Environment Variables

To run this project, you must add **at least one** model configuration (OpenAI or Groq) to your `.env` file.

#### To use OpenAI model:  
`OPENAI_MODEL_NAME` = `<your_openai_model_name>`  
`OPENAI_API_KEY` = `<your_openai_api_key>`  

#### To use Groq model:  
`LOCAL_DEVELOPMENT` = `true`  
`GROQ_MODEL_NAME` = `<your_groq_model_name>`  
`GROQ_API_KEY` = `<your_groq_api_key>`  

At least one of the above configurations must be provided for the project to function properly.  

#### To enable Langsmith tracing (optional):  
`LANGSMITH_TRACING` = `true`  
`LANGSMITH_ENDPOINT` = `<your_langsmith_endpoint>`  
`LANGSMITH_API_KEY` = `<your_langsmith_api_key>`  
`LANGSMITH_PROJECT` = `<your_langsmith_project>`  

## Run Locally

1. Clone the project:

```bash
  git clone https://github.com/Wonsky1/pokemon-multi-agent.git
```

2. Go to the project directory:

```bash
  cd pokemon-multi-agent
```

3. Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows use `.venv\Scripts\activate`
```

OR

```bash
make venv
source .venv/bin/activate   # On Windows use `.venv\Scripts\activate`
```


4. Install dependencies:

```bash
  pip install -r requirements.txt
```

OR

```bash
make install
```

5. Create .env file in root directory and fill it with [Environment Variables](#environment-variables):
```
  make create-env
```
OR

manualy

6. Run app:
```bash
  uvicorn app:app --host 0.0.0.0 --port 8000
```

OR

```bash
make run-local
```

7. Go to http://localhost:8000/docs
## Run Locally using Docker

1. Clone the project:

```bash
  git clone https://github.com/Wonsky1/pokemon-multi-agent.git
```

2. Go to the project directory:

```bash
  cd pokemon-multi-agent
```

3. Create .env file in root directory and fill it with [Environment Variables](#environment-variables):
```bash
  make create-env
```
OR

manualy

4. Build Docker image:
```bash
  make docker-build
```

OR

```bash
docker build -t pokemon-agent-system .
```

5. Run Docker image:
```bash
  make docker-run
```

OR

```bash
docker run -p 8000:8000 --env-file .env pokemon-agent-system
```

6. Go to http://localhost:8000/docs
## API Reference

#### Ask something

```http
  POST /chat
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `question` | `string` | **Required**. Your question |

If you asked general question not related to Pokémon, it will answer you directly.

If you asked question about some stats of a Pokémon, it will answer with its stats if the Pokémon exist.

If you asked some question about Pokémon analysis or battle scenarios, or any other pokemon questions it will give you an answer and the reasoning.

| Question example | Agent triggered     | Answer                |
| :-------- | :------- | :------------------------- |
| What is the capital of France | Direct answer (supervisor) | `{"answer": "The capital of France is Paris."}` |
| What are the base stats of Charizard?| Researcher Agent | `{"name": "charizard", "base_stats": {"hp": 78, "attack": 84, "defense": 78, "special_attack": 109, "special_defense": 85, "speed": 100}}` |
| Who would win in a battle, Pikachu or Bulbasaur? | Pokemon Expert Agent | `{"answer": "Pikachu has an electric-type advantage over Bulbasaur, so it would likely win.", "reasoning": "Electric-type moves are strong against Water and Flying-types, but Bulbasaur is Grass/Poison. However, Pikachu has higher speed and access to strong electric moves."}` |
| Who would win in a battle, Pikachu or Stonehedge? | Pokemon Expert Agent | `{"answer": "ANSWER_IMPOSSIBLE", "reasoning": "Could not analyze the query due to invalid Pokémon. Please check the spelling of Pokémon names."}` |

- **Error (500)**: Returns an error message if something goes wrong during processing.

#### Battle endpoint

```http
  GET /battle?pokemon1={pokemon1_name}?pokemon2={pokemon2_name}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `pokemon1`      | `string` | **Required**. First pokemon in the battle |
| `pokemon2`      | `string` | **Required**. Second pokemon in the battle |

Ask Battle Expert Agent to return a predicted winner of the battle. It gets each pokemon types strength and weaknesses and base stats, and predicts a winner.

| Pokemon1 example | Pokemon2 example     | Answer example                |
| :-------- | :------- | :------------------------- |
| Pikachu | Bulbasaur | `{"winner": "Pikachu", "reasoning": "Pikachu has a higher base speed and access to strong electric moves, which are effective against Bulbasaur."}` |
| Pikachu | Stonehedge | `{"winner": "BATTLE_IMPOSSIBLE", "reasoning": "Could not analyze the battle due to invalid Pokémon. Please check the spelling of Pokémon names."}` |

- **Error (500)**: Returns an error message if something goes wrong during processing.





## Troubleshooting
- Common Issues:
  - Ensure all environment variables are correctly set in the `.env` file.
  - Verify that all dependencies are installed by checking the `requirements.txt` file.

- Error Messages:
  - If you encounter errors, check the application logs for detailed error messages and stack traces.

## Running Tests
- To run unittests, run:
```bash
  make test-unittests
```

OR 

```bash
  pytest -v -m "not integration"
```


- To run integration tests, run:
`> NOTE: Integration tests may fail on models other than gpt-4o-mini-2024-07-18 due to LLM unpredictability 🙂`

```bash
  make test-integration
```

OR

```bash
  pytest -v -m integration
```

- To run both, run:
```bash
  make tests
```

OR

```bash
  pytest -v
```

- To get test coverage, run:
```bash
  make coverage
```

OR

```bash
  pytest -v --cov=. -m "not integration"
  coverage report
```




## Documentation

  The API documentation is available at `http://localhost:8000/docs` after starting the application.


## Make Commands

| Command             | Executes                            | Description                                                                 |
|---------------------|-------------------------------------|-----------------------------------------------------------------------------|
| `make venv`         | `python3 -m venv .venv`             | Creates a new Python virtual environment in the `.venv` directory.          |
| `make install`      | `pip install -r requirements.txt`   | Installs project dependencies from `requirements.txt`.                      |
| `make tests`        | `pytest -v`                         | Runs all tests with verbose output.                                         |
| `make coverage`     | `pytest -v --cov=. -m "not integration"` + `coverage report` | Runs unit tests with code coverage and prints a coverage report.            |
| `make clean`        | `rm -rf __pycache__ .pytest_cache`  | Cleans up Python cache and test artifacts.                                  |
| `make docker-build` | `docker build -t pokemon-agent-system .` | Builds a Docker image tagged as `pokemon-agent-system`.                      |
| `make docker-run`   | `docker run -p 8000:8000 --env-file .env pokemon-agent-system` | Runs the Docker container locally with environment variables from `.env`.   |
| `make run-local`    | `uvicorn main:app --reload`         | Runs the app locally using Uvicorn in auto-reload development mode.         |
| `make lint`         | `flake8`                            | Runs `flake8` to check code for style and linting errors.                   |
| `make black`        | `black . --exclude .venv`           | Formats the code using `black`, excluding the virtual environment.          |
| `make test-unittests` | `pytest -v -m "not integration"`  | Runs only unit tests (excluding integration tests).                         |
| `make test-integration` | `pytest -v -m integration`      | Runs only integration tests.                                                |
| `make create-env`   | (Creates a `.env` file with placeholder values) | Creates a default `.env` file with environment variable placeholders.       |

## FAQ

#### How do I get my OpenAI key?

   - Create an account in openai platform: https://platform.openai.com
   - Follow the guide for getting API key: https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key
   - Set up billing: https://platform.openai.com/settings/organization/billing/overview

#### How do I get my GROQ key?

   - Create an account in groqcloud: https://console.groq.com/login
   - Create and copy API key: https://console.groq.com/keys
   - Choose any model: https://console.groq.com/playground


#### How do I get my langsmith project and key?

   - Create an account in langsmith: https://smith.langchain.com/
   - Click `Set up tracing` and follow the guide
