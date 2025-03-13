from enum import Enum, StrEnum
from typing import Any, Dict, Optional
from pydantic import field_validator, ValidationInfo

from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_core.language_models import BaseChatModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


load_dotenv("dev.env")


class ResponseFormat(StrEnum):
    """Enum for agent response formats."""
    SIMPLIFIED = "simplified"
    DETAILED = "detailed"


class AgentType(StrEnum):
    """Enum for agent types."""
    SUPERVISOR = "supervisor"
    RESEARCHER = "researcher"
    POKEMON_EXPERT = "pokemon_expert"
    DIRECT_RESPONSE = "direct_response"


class RouterOptions(StrEnum):
    """Enum for router response options."""
    RESEARCHER = AgentType.RESEARCHER
    POKEMON_EXPERT = AgentType.POKEMON_EXPERT
    DIRECT_RESPONSE = AgentType.DIRECT_RESPONSE


class PokemonNotFoundStatus(StrEnum):
    """Enum for Pokemon not found status."""
    NOT_FOUND = "NOT_FOUND"
    BATTLE_IMPOSSIBLE = "BATTLE_IMPOSSIBLE"
    ANSWER_IMPOSSIBLE = "ANSWER_IMPOSSIBLE"


class Settings(BaseSettings):
    """Class defining configuration settings using Pydantic."""
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    # API Configuration
    POKEAPI_BASE_URL: str = "https://pokeapi.co/api/v2"

    # HTTP Client Configuration
    HTTP_TIMEOUT_SECONDS: float = 10.0
    CACHE_SIZE: int = 100

    # Model Configuration
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL_NAME: Optional[str] = None

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL_NAME: Optional[str] = None

    LOCAL_DEVELOPMENT: bool = False

    GENERATIVE_MODEL: Optional[BaseChatModel] = None

    # LangSmith Configuration
    LANGSMITH_TRACING: Optional[str] = None
    LANGSMITH_ENDPOINT: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: Optional[str] = None

    # Agent Configuration
    DEFAULT_RESPONSE_FORMAT: ResponseFormat = ResponseFormat.DETAILED

    # Default agent configurations
    DEFAULT_AGENT_CONFIGS: Dict[str, Dict[str, Any]] = {
        AgentType.SUPERVISOR: {},
        AgentType.RESEARCHER: {},
        AgentType.POKEMON_EXPERT: {
            "response_format": ResponseFormat.DETAILED,
        },
    }

    @field_validator("GENERATIVE_MODEL")
    def generative_model(
        cls, value: Optional[BaseChatModel], info: ValidationInfo
    ) -> Optional[BaseChatModel]:
        env_data = info.data
        local_development = env_data.get("LOCAL_DEVELOPMENT")

        if local_development:
            model_name = env_data.get("GROQ_MODEL_NAME")
            api_key = env_data.get("GROQ_API_KEY")

            if model_name:
                return ChatGroq(model_name=model_name, api_key=api_key)
            else:
                raise ValueError(
                    "GROQ_MODEL_NAME must be set when LOCAL_DEVELOPMENT is True"
                )
        else:
            model_name = env_data.get("OPENAI_MODEL_NAME")
            api_key = env_data.get("OPENAI_API_KEY")

            if model_name:
                return ChatOpenAI(model_name=model_name, api_key=api_key)
            else:
                raise ValueError(
                    "OPENAI_MODEL_NAME must be set when LOCAL_DEVELOPMENT is False"
                )


settings = Settings()
