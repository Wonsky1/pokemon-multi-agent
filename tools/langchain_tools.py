from typing import Any, Dict
from langchain.agents import tool

from core.exceptions import PokemonNotFoundError
from tools.pokeapi import PokeAPIService


@tool
def pokeapi_tool_with_types(pokemon_name: str) -> Dict[str, Any] | str:
    """Tool to fetch essential Pokémon data from PokéAPI including type damage relations."""
    try:
        return PokeAPIService.get_pokemon_data(pokemon_name, get_type_data=True)
    except PokemonNotFoundError as e:
        return str(e)

@tool
def pokeapi_tool(pokemon_name: str) -> Dict[str, Any] | str:
    """Tool to fetch essential Pokémon data from PokéAPI."""
    try:
        return PokeAPIService.get_pokemon_data(pokemon_name)
    except PokemonNotFoundError as e:
        return str(e)
