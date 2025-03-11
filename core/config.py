from typing import Optional
from pydantic import field_validator, ValidationInfo

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv("dev.env")


class Settings(BaseSettings):
    """Class defining configuration settings using Pydantic."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    POKEAPI_BASE_URL: str = "https://pokeapi.co/api/v2"

    GROQ_API_KEY: str
    GROQ_MODEL_NAME: str

    GENERATIVE_MODEL: Optional[ChatGroq] = None

    LANGSMITH_TRACING: Optional[str] = None
    LANGSMITH_ENDPOINT: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: Optional[str] = None

    @field_validator("GENERATIVE_MODEL")
    def generative_model(
        cls, value: Optional[ChatGroq], info: ValidationInfo
    ) -> Optional[ChatGroq]:
        env_data = info.data

        model_name = env_data.get("GROQ_MODEL_NAME")

        return ChatGroq(model_name=model_name)

settings = Settings()
