from contextlib import asynccontextmanager
from http.client import HTTPException
import logging
import time
from fastapi import FastAPI, Depends
from prompts import BATTLE_EXPERT_PROMPT
from agents.pokemon_expert import PokemonExpertAgent
from core.di import get_agent_factory, get_pokemon_service, initialize_pokemon_service, shutdown_pokemon_service, get_agent_graph
from api.models import ChatRequest
from core.agent_graph import AgentGraph
from core.exceptions import PokemonNotFoundError
from tools.pokeapi import PokeAPIService

agent_graph: AgentGraph | None = None
battle_expert: PokemonExpertAgent | None = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_format = "%(asctime)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_error_logger = logging.getLogger("uvicorn.error")

for logger in (uvicorn_access_logger, uvicorn_error_logger):
    for handler in logger.handlers:
        handler.setFormatter(formatter)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing the Pokémon Multi-Agent System")
    initialize_pokemon_service()

    global agent_graph
    agent_graph = get_agent_graph()

    global battle_expert
    battle_expert = get_agent_factory().create_battle_expert(
        custom_prompt=BATTLE_EXPERT_PROMPT
    )

    yield

    await shutdown_pokemon_service()


app = FastAPI(
    lifespan=lifespan,
    title="Pokémon Multi-Agent System",
    description="A multi-agent system for answering Pokémon-related queries",
    version="1.0.0",
)


@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint."""
    try:
        logger.info(f"Processing chat request")
        result = await agent_graph.invoke(request.question)
        return result
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/battle")
async def battle(
    pokemon1: str,
    pokemon2: str,
    pokemon_service: PokeAPIService = Depends(get_pokemon_service),
):
    """Battle endpoint."""
    try:
        logger.info(f"Processing battle request")
        pokemon1_data = await pokemon_service.get_pokemon_data(pokemon1)
        pokemon2_data = await pokemon_service.get_pokemon_data(pokemon2)

        query = f"Who would win in a battle, {pokemon1}: {pokemon1_data}\nor {pokemon2}: {pokemon2_data}?"
        messages = [{"role": "human", "content": query}]
        result = await battle_expert.process(messages)
        return result

    except PokemonNotFoundError as e:
        return {
            "winner": "BATTLE_IMPOSSIBLE",
            "reasoning": "Could not analyze the battle due to invalid Pokémon. Please check the spelling of Pokémon names.",
        }
    except Exception as e:
        logger.error(f"Error processing battle request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Pokémon Multi-Agent System API"}
