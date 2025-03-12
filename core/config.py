from typing import Optional
from pydantic import field_validator, ValidationInfo

from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_core.language_models import BaseChatModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


load_dotenv("dev.env")


class Settings(BaseSettings):
    """Class defining configuration settings using Pydantic."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    POKEAPI_BASE_URL: str = "https://pokeapi.co/api/v2"

    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL_NAME: Optional[str] = None

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL_NAME: Optional[str] = None

    LOCAL_DEVELOPMENT: bool = False

    GENERATIVE_MODEL: Optional[BaseChatModel] = None

    LANGSMITH_TRACING: Optional[str] = None
    LANGSMITH_ENDPOINT: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: Optional[str] = None

    @field_validator("GENERATIVE_MODEL")
    def generative_model(
        cls, value: Optional[BaseChatModel], info: ValidationInfo
    ) -> Optional[BaseChatModel]:
        env_data = info.data
        local_development = env_data.get("LOCAL_DEVELOPMENT")

        if local_development:
            model_name = env_data.get("GROQ_MODEL_NAME")

            return ChatGroq(model_name=model_name)

        model_name = env_data.get("OPENAI_MODEL_NAME")

        return ChatOpenAI(model_name=model_name, api_key=env_data.get("OPENAI_API_KEY"))


settings = Settings()
