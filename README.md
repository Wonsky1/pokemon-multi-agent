# Pokémon Multi-Agent System

A sophisticated LLM-powered question-answering system for Pokémon-related queries, built with a multi-agent architecture.

This project implements a specialized AI system designed to answer questions about Pokémon, with particular focus on analyzing hypothetical battle scenarios. The system uses multiple specialized LLM agents that coordinate through a graph-based workflow to handle different types of queries. 

This system was tested on the OpenAI `gpt-4o-mini-2024-07-18` model, and it's important to note that using other models might lead to some unpredictable answers.


## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for different tasks working together
- **Battle Analysis**: Predict battle outcomes between Pokémon with detailed reasoning
- **Stats Lookup**: Quickly retrieve base stats and information about any Pokémon
- **General Q&A**: Answer general Pokémon-related questions
- **Flexible Routing**: Intelligent request routing to the most appropriate agent
- **Easy Model Switching**: Use either GROQ models for local development or OpenAI models for deployment

## 🏗️ Architecture

The system uses a graph-based workflow with specialized agents:

- **Supervisor Agent**: Routes queries to the appropriate specialized agent
- **Researcher Agent**: Retrieves and provides data from external sources (PokéAPI)
- **Pokémon Expert Agent**: Analyzes battle scenarios and answers complex Pokémon questions
- **Battle Expert Agent**: Specialized agent for battle outcome prediction

![agents graph structure diagram](https://i.imgur.com/PEvyMKn.png)

## 🛠️ Setup

### Environment Variables

To run this project, you must add **at least one** model configuration (OpenAI or Groq) to your `.env` file.

#### To use OpenAI model:  
```
OPENAI_MODEL_NAME=<your_openai_model_name>
OPENAI_API_KEY=<your_openai_api_key>
```

#### To use Groq model:  
```
LOCAL_DEVELOPMENT=true
GROQ_MODEL_NAME=<your_groq_model_name>
GROQ_API_KEY=<your_groq_api_key>
```

#### To enable Langsmith tracing (optional):  
```
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=<your_langsmith_endpoint>
LANGSMITH_API_KEY=<your_langsmith_api_key>
LANGSMITH_PROJECT=<your_langsmith_project>
```

### Run Locally

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

5. Create `.env` file in root directory and fill it with environment variables:
```bash
make create-env
```

6. Run app:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

OR

```bash
make run-local
```

7. Access the API documentation at http://localhost:8000/docs

### Run with Docker

1. Clone the project:
```bash
git clone https://github.com/Wonsky1/pokemon-multi-agent.git
```

2. Go to the project directory:
```bash
cd pokemon-multi-agent
```

3. Create `.env` file in root directory and fill it with environment variables:
```bash
make create-env
```

4. Build Docker image:
```bash
make docker-build
```

5. Run Docker image:
```bash
make docker-run
```

6. Access the API documentation at http://localhost:8000/docs

## 📚 API Reference

### Ask a Question

```http
POST /chat
```

| Parameter  | Type     | Description                |
| :--------- | :------- | :------------------------- |
| `question` | `string` | **Required**. Your question |

Response examples based on query type:

| Question Example | Agent Triggered | Response |
| :--------------- | :-------------- | :------- |
| What is the capital of France? | Direct answer (supervisor) | `{"answer": "The capital of France is Paris."}` |
| What are the base stats of Charizard? | Researcher Agent | `{"name": "charizard", "base_stats": {"hp": 78, "attack": 84, "defense": 78, "special_attack": 109, "special_defense": 85, "speed": 100}}` |
| Who would win in a battle, Pikachu or Bulbasaur? | Pokemon Expert Agent | `{"answer": "Pikachu has an electric-type advantage over Bulbasaur, so it would likely win.", "reasoning": "Electric-type moves are strong against Water and Flying-types, but Bulbasaur is Grass/Poison. However, Pikachu has higher speed and access to strong electric moves."}` |
| Who would win in a battle, Pikachu or Stonehenge? | Pokemon Expert Agent | `{"answer": "ANSWER_IMPOSSIBLE", "reasoning": "Could not analyze the query due to invalid Pokémon. Please check the spelling of Pokémon names."}` |

### Battle Analysis

```http
GET /battle?pokemon1={pokemon1_name}&pokemon2={pokemon2_name}
```

| Parameter  | Type     | Description                       |
| :--------- | :------- | :-------------------------------- |
| `pokemon1` | `string` | **Required**. First pokemon in the battle |
| `pokemon2` | `string` | **Required**. Second pokemon in the battle |

Response examples:

| Pokemon1 | Pokemon2 | Response |
| :------- | :------- | :------- |
| Pikachu | Bulbasaur | `{"winner": "Pikachu", "reasoning": "Pikachu has a higher base speed and access to strong electric moves, which are effective against Bulbasaur."}` |
| Pikachu | Stonehenge | `{"winner": "BATTLE_IMPOSSIBLE", "reasoning": "Could not analyze the battle due to invalid Pokémon. Please check the spelling of Pokémon names."}` |

## 🧪 Testing

### Run Unit Tests
```bash
make test-unittests
```

OR 

```bash
pytest -v -m "not integration"
```

### Run Integration Tests
> NOTE: Integration tests may fail on models other than gpt-4o-mini-2024-07-18 due to LLM unpredictability 🙂

```bash
make test-integration
```

OR

```bash
pytest -v -m integration
```

### Run All Tests
```bash
make tests
```

OR

```bash
pytest -v
```

### Get Test Coverage
```bash
make coverage
```

OR

```bash
pytest -v --cov=. -m "not integration"
coverage report
```

## 📋 Make Commands

All underlying commands can be accessed in the `Makefile`.

| Command             | Description                                                |
|---------------------|------------------------------------------------------------|
| `make venv`         | Creates a new Python virtual environment                   |
| `make install`      | Installs project dependencies                              |
| `make tests`        | Runs all tests with verbose output                         |
| `make coverage`     | Runs unit tests with code coverage and prints a report     |
| `make clean`        | Cleans up Python cache and test artifacts                  |
| `make docker-build` | Builds a Docker image                                      |
| `make docker-run`   | Runs the Docker container locally                          |
| `make run-local`    | Runs the app locally using Uvicorn in development mode     |
| `make lint`         | Checks code for style and linting errors                   |
| `make black`        | Formats the code using `black`                             |
| `make test-unittests` | Runs only unit tests                                     |
| `make test-integration` | Runs only integration tests                            |
| `make create-env`   | Creates a default `.env` file with placeholder values      |

## 🔧 Troubleshooting

### Common Issues
- **Environment Variables**: Ensure all environment variables are correctly set in the `.env` file.
- **Dependencies**: Verify that all dependencies are installed by checking the `requirements.txt` file.
- **API Keys**: Double-check that your API keys for OpenAI/GROQ are valid and have sufficient quota.

### Error Messages
- If you encounter errors, check the application logs for detailed error messages and stack traces.
- For model-related errors, verify that you're using a supported model and have configured it correctly.

## ❓ FAQ

### How do I get my OpenAI key?

1. Create an account on the OpenAI platform: https://platform.openai.com
2. Follow the guide for getting API key: https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key
3. Set up billing: https://platform.openai.com/settings/organization/billing/overview

### How do I get my GROQ key?

1. Create an account in GROQ Cloud: https://console.groq.com/login
2. Create and copy API key: https://console.groq.com/keys
3. Choose any model: https://console.groq.com/playground

### How do I get my Langsmith project and key?

1. Create an account in Langsmith: https://smith.langchain.com/
2. Click `Set up tracing` and follow the guide

## 📝 License

This project uses the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
