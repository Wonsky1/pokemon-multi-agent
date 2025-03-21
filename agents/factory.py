from typing import Dict, Optional, Type, Any
from agents.base import BaseAgent
from agents.pokemon_expert import PokemonExpertAgent
from core.config import settings, AgentType, ResponseFormat
from tools.langchain_tools import async_pokeapi_tool_with_types
from agents.supervisor import SupervisorAgent
from agents.researcher import ResearcherAgent
from tools.langchain_tools import async_pokeapi_tool


class AgentFactory:
    """Factory for creating agent instances with async support."""

    _instances: Dict[str, BaseAgent] = {}
    _agent_classes = {}
    _default_configs = {}

    @classmethod
    def initialize(cls):
        """Initialize agent classes and configurations - called after imports are resolved."""
        cls._agent_classes = {
            AgentType.SUPERVISOR: SupervisorAgent,
            AgentType.RESEARCHER: ResearcherAgent,
            AgentType.POKEMON_EXPERT: PokemonExpertAgent,
        }

        cls._default_configs = settings.DEFAULT_AGENT_CONFIGS.copy()

    @classmethod
    def get_agent(cls, agent_type: str, **kwargs) -> BaseAgent:
        """
        Get an agent instance of the specified type.

        Args:
            agent_type: Type of agent to create
            **kwargs: Additional configuration options for the agent

        Returns:
            An instance of the requested agent

        Raises:
            ValueError: If the agent type is not recognized
        """
        if not cls._agent_classes:
            cls.initialize()

        if agent_type not in cls._agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}")

        if not kwargs and agent_type in cls._instances:
            return cls._instances[agent_type]

        config = cls._default_configs.get(agent_type, {}).copy()
        config.update(kwargs)

        if "llm" not in config:
            config["llm"] = settings.GENERATIVE_MODEL

        agent_class = cls._agent_classes[agent_type]
        agent_instance = agent_class(**config)

        if not kwargs:
            cls._instances[agent_type] = agent_instance

        return agent_instance

    @classmethod
    def register_agent_class(
        cls,
        agent_type: str,
        agent_class: Type[BaseAgent],
        default_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a new agent class with the factory.

        Args:
            agent_type: Type identifier for the agent
            agent_class: Class to instantiate for this agent type
            default_config: Default configuration for this agent type
        """
        cls._agent_classes[agent_type] = agent_class
        if default_config:
            cls._default_configs[agent_type] = default_config
        else:
            cls._default_configs[agent_type] = {}

    @classmethod
    def create_battle_expert(
        cls,
        response_format: str = ResponseFormat.SIMPLIFIED,
        custom_prompt: Optional[str] = None,
        use_tool: bool = True,
    ) -> PokemonExpertAgent:
        """
        Create a specialized battle expert agent.

        Args:
            response_format: Format of the response ("detailed" or "simplified")
            custom_prompt: Custom prompt to use for the battle expert

        Returns:
            A configured PokemonExpertAgent for battle analysis
        """
        tools = []
        if use_tool:
            tools = [async_pokeapi_tool_with_types]

        battle_expert_config = {
            "tools": tools,
            "response_format": response_format,
        }

        if custom_prompt:
            battle_expert_config["prompt"] = custom_prompt

        return cls.get_agent(AgentType.POKEMON_EXPERT, **battle_expert_config)


agent_factory = None


def get_agent_factory() -> AgentFactory:
    """Dependency injection provider for the AgentFactory.
    Ensures singleton behavior.
    """
    global agent_factory
    if agent_factory is None:
        agent_factory = AgentFactory()
    return agent_factory


def get_supervisor_agent(
    factory: AgentFactory = get_agent_factory(),
):
    """Dependency provider for the Supervisor agent."""
    return factory.get_agent(AgentType.SUPERVISOR)


def get_researcher_agent(
    factory: AgentFactory = get_agent_factory(),
):
    """Dependency provider for the Researcher agent."""
    return factory.get_agent(AgentType.RESEARCHER)


def get_pokemon_expert_agent(
    factory: AgentFactory = get_agent_factory(),
    response_format: str = ResponseFormat.DETAILED,
):
    """Dependency provider for the Pokemon Expert agent."""
    return factory.get_agent(AgentType.POKEMON_EXPERT, response_format=response_format)


def get_battle_expert_agent(
    factory: AgentFactory = get_agent_factory(),
    response_format: str = ResponseFormat.SIMPLIFIED,
    custom_prompt: str = None,
):
    """Dependency provider for a specialized Battle Expert agent."""
    return factory.create_battle_expert(
        response_format=response_format, custom_prompt=custom_prompt
    )
