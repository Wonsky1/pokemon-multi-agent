# agents/factory.py
from typing import Dict, Optional, Type, Any
from langchain.agents import Tool
from agents.base import BaseAgent
from agents.direct_response import DirectResponseAgent
from agents.pokemon_expert import PokemonExpertAgent
from agents.researcher import ResearcherAgent
from agents.supervisor import SupervisorAgent
from tools.langchain_tools import pokeapi_tool, pokeapi_tool_with_types
from core.config import settings

class AgentFactory:
    """Factory for creating agent instances."""
    
    _instances: Dict[str, BaseAgent] = {}
    
    _agent_classes = {
        "supervisor": SupervisorAgent,
        "direct_response": DirectResponseAgent,
        "researcher": ResearcherAgent,
        "pokemon_expert": PokemonExpertAgent,
    }
    
    _default_configs = {
        "supervisor": {},
        "direct_response": {},
        "researcher": {},
        "pokemon_expert": {
            "tools": [pokeapi_tool],
            "response_format": "detailed"
        }
    }
    
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
    def register_agent_class(cls, agent_type: str, agent_class: Type[BaseAgent], 
                            default_config: Optional[Dict[str, Any]] = None) -> None:
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
    def create_battle_expert(cls, response_format: str = "simplified", 
                           custom_prompt: Optional[str] = None) -> PokemonExpertAgent:
        """
        Create a specialized battle expert agent.
        
        Args:
            response_format: Format of the response ("detailed" or "simplified")
            custom_prompt: Custom prompt to use for the battle expert
            
        Returns:
            A configured PokemonExpertAgent for battle analysis
        """
        battle_expert_config = {
            "tools": [pokeapi_tool_with_types],
            "response_format": response_format
        }
        
        if custom_prompt:
            battle_expert_config["prompt"] = custom_prompt
            
        return cls.get_agent("pokemon_expert", **battle_expert_config)
