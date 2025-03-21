from contextlib import asynccontextmanager
from http import HTTPStatus
from fastapi import FastAPI, Depends, HTTPException
from agents.factory import get_agent_factory
from prompts import BATTLE_EXPERT_PROMPT
from agents.pokemon_expert import PokemonExpertAgent
from api.models import ChatRequest
from core.agent_graph import AgentGraph, get_agent_graph
from core.config import PokemonNotFoundStatus
from core.exceptions import PokemonNotFoundError
from tools.pokeapi import (
    PokeAPIService,
    get_pokemon_service,
    initialize_pokemon_service,
    shutdown_pokemon_service,
)
from core.logging import configure_all_loggers, get_logger

configure_all_loggers(debug_mode=False)
logger = get_logger(__name__)

agent_graph: AgentGraph | None = None
battle_expert: PokemonExpertAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for the lifespan of the Pokémon Multi-Agent System.
    Initializes the system, yields control, and then shuts down the system.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    logger.info("Initializing the Pokémon Multi-Agent System")
    initialize_pokemon_service()

    global agent_graph
    agent_graph = get_agent_graph()

    global battle_expert
    battle_expert = get_agent_factory().create_battle_expert(
        custom_prompt=BATTLE_EXPERT_PROMPT,
        use_tool=False,
    )

    logger.info("System initialization complete")
    yield

    logger.info("Shutting down the Pokémon Multi-Agent System")
    await shutdown_pokemon_service()
    logger.info("System shutdown complete")


app = FastAPI(
    lifespan=lifespan,
    title="Pokémon Multi-Agent System",
    description="A multi-agent system for answering Pokémon-related queries",
    version="1.0.0",
)


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Endpoint for processing chat requests.
    Invokes the agent graph to process the request and returns the result.

    Args:
        question : User`s question

    Returns:
        The result of the chat request processing.
    """
    try:
        logger.info(f"Processing chat request: '{request.question}'")
        result = await agent_graph.invoke(request.question)
        logger.info("Chat request processed successfully")
        return result
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/battle")
async def battle(
    pokemon1: str,
    pokemon2: str,
    pokemon_service: PokeAPIService = Depends(get_pokemon_service),
):
    """
    Endpoint for processing battle requests.
    Compares two Pokémon and returns the result of a hypothetical battle.

    Args:
        pokemon1 (str): The name of the first Pokémon.
        pokemon2 (str): The name of the second Pokémon.

    Returns:
        The result of the battle request processing.
    """
    try:
        logger.info(f"Processing battle request: {pokemon1} vs {pokemon2}")
        pokemon1_data = await pokemon_service.get_pokemon_data(
            pokemon1, get_type_data=True
        )
        logger.debug(f"Retrieved data for {pokemon1}")

        pokemon2_data = await pokemon_service.get_pokemon_data(
            pokemon2, get_type_data=True
        )
        logger.debug(f"Retrieved data for {pokemon2}")

        query = f"Who would win in a battle, {pokemon1}: {pokemon1_data}\nor {pokemon2}: {pokemon2_data}?"
        messages = [{"role": "human", "content": query}]

        logger.debug("Sending battle analysis query to expert agent")
        result = await battle_expert.process(messages)

        logger.info("Battle request processed successfully")
        return result

    except PokemonNotFoundError as e:
        logger.warning(f"Pokemon not found: {str(e)}")
        return {
            "winner": PokemonNotFoundStatus.BATTLE_IMPOSSIBLE,
            "reasoning": "Could not analyze the battle due to invalid Pokémon. Please check the spelling of Pokémon names.",
        }
    except Exception as e:
        logger.error(f"Error processing battle request: {e}", exc_info=True)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/")
async def root():
    """
    Root endpoint.
    Returns a welcome message.

    Returns:
        A dictionary containing a welcome message.
    """
    logger.debug("Root endpoint accessed")
    return {"message": "Welcome to the Pokémon Multi-Agent System API"}
