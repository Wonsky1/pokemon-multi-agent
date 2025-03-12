from fastapi import Depends

from agents import factory
from core.agent_graph import AgentGraph
from tools.pokeapi import PokeAPIService, get_pokemon_service


pokemon_service = None

agent_factory = None

agent_graph = None


async def initialize_pokemon_service() -> None:
    """Initialize the global Pokemon service."""
    global pokemon_service
    pokemon_service = PokeAPIService()


async def shutdown_pokemon_service() -> None:
    """Shutdown the global Pokemon service."""
    global pokemon_service
    if pokemon_service:
        await pokemon_service.close()


async def get_pokemon_service() -> PokeAPIService:
    """Dependency injection provider for PokeAPIService."""
    global pokemon_service
    if pokemon_service is None:
        pokemon_service = PokeAPIService()
    return pokemon_service


async def get_agent_factory() -> factory.AgentFactory:
    """Dependency injection provider for the AgentFactory.
    Ensures singleton behavior.
    """
    global agent_factory
    if agent_factory is None:
        agent_factory = factory.AgentFactory()
    return agent_factory


def get_supervisor_agent(
    factory: factory.AgentFactory = Depends(get_agent_factory),
):
    """Dependency provider for the Supervisor agent."""
    return factory.get_agent("supervisor")


def get_researcher_agent(
    factory: factory.AgentFactory = Depends(get_agent_factory),
):
    """Dependency provider for the Researcher agent."""
    return factory.get_agent("researcher")


def get_pokemon_expert_agent(
    factory: factory.AgentFactory = Depends(get_agent_factory),
    response_format: str = "detailed",
):
    """Dependency provider for the Pokemon Expert agent."""
    return factory.get_agent("pokemon_expert", response_format=response_format)


def get_battle_expert_agent(
    factory: factory.AgentFactory = Depends(get_agent_factory),
    response_format: str = "simplified",
    custom_prompt: str = None,
):
    """Dependency provider for a specialized Battle Expert agent."""
    return factory.create_battle_expert(
        response_format=response_format, custom_prompt=custom_prompt
    )


def get_agent_graph(
    pokemon_service: PokeAPIService = Depends(get_pokemon_service),
    agent_factory: factory.AgentFactory = Depends(get_agent_factory),
) -> AgentGraph:
    """Dependency provider for the AgentGraph."""
    global agent_graph
    if agent_graph is None:
        agent_graph = AgentGraph()
    return agent_graph
