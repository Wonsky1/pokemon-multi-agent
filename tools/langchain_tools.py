from typing import Any, Dict, Type
from typing_extensions import Literal
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from core.exceptions import PokemonNotFoundError
from core.di import get_pokemon_service

class PokemonInput(BaseModel):
    """Input for the Pokemon tool."""

    pokemon_name: str = Field(..., description="The name of the Pokemon to look up")


class AsyncPokeapiTool(BaseTool):
    name: Literal["async_pokeapi_tool"] = "async_pokeapi_tool"
    description: Literal["Tool to fetch essential Pokémon data from PokéAPI."] = (
        "Tool to fetch essential Pokémon data from PokéAPI."
    )
    args_schema: Type[BaseModel] = PokemonInput

    async def _arun(self, pokemon_name: str) -> Dict[str, Any] | str:
        """Run the tool asynchronously."""
        try:
            service = await get_pokemon_service()
            return await service.get_pokemon_data(pokemon_name.lower())
        except PokemonNotFoundError as e:
            return str(e)

    def _run(self, pokemon_name: str) -> Dict[str, Any] | str:
        """This shouldn't be called but is required for the interface."""
        raise NotImplementedError("This tool only supports async operation")


class AsyncPokeapiToolWithTypes(BaseTool):
    name: Literal["async_pokeapi_tool_with_types"] = "async_pokeapi_tool_with_types"
    description: Literal[
        "Tool to fetch essential Pokémon data from PokéAPI including type damage relations."
    ] = "Tool to fetch essential Pokémon data from PokéAPI including type damage relations."
    args_schema: Type[BaseModel] = PokemonInput

    async def _arun(self, pokemon_name: str) -> Dict[str, Any] | str:
        """Run the tool asynchronously."""
        try:
            service = await get_pokemon_service()
            return await service.get_pokemon_data(
                pokemon_name.lower(), get_type_data=True
            )
        except PokemonNotFoundError as e:
            return str(e)

    def _run(self, pokemon_name: str) -> Dict[str, Any] | str:
        """This shouldn't be called but is required for the interface."""
        raise NotImplementedError("This tool only supports async operation")


async_pokeapi_tool = AsyncPokeapiTool()
async_pokeapi_tool_with_types = AsyncPokeapiToolWithTypes()
