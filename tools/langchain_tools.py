from typing import Any, Dict
from langchain.agents import tool

from tools.pokeapi import PokeAPIService


@tool
def pokeapi_tool(pokemon_name: str) -> Dict[str, Any]:
    """Tool to fetch essential Pokémon data from PokéAPI including type damage relations."""
    return PokeAPIService.get_pokemon_data(pokemon_name)
