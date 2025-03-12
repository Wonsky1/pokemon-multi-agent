from typing import Dict, Any
import httpx
from core.config import settings
from core.exceptions import PokemonNotFoundError


class PokeAPIService:
    """Service for interacting with the PokéAPI with caching and async support."""

    BASE_URL = settings.POKEAPI_BASE_URL

    def __init__(self, cache_size: int = 100):
        """Initialize the service with an optional cache size."""
        self.client = httpx.AsyncClient(timeout=10.0)

        self.pokemon_cache = {}
        self.type_cache = {}
        self.cache_size = cache_size

    async def close(self):
        """Close the HTTP client when the service is done."""
        await self.client.aclose()

    async def pokemon_exists(self, pokemon_name: str) -> bool:
        """Check if a Pokémon exists in the PokéAPI."""
        try:
            await self.get_pokemon_data(pokemon_name.lower(), False)
            return True
        except PokemonNotFoundError:
            return False

    async def get_pokemon_data(
        self, pokemon_name: str, get_type_data: bool = False
    ) -> Dict[str, Any]:
        """Fetch Pokémon data from the PokéAPI with caching."""
        cache_key = f"{pokemon_name}_{get_type_data}"

        if cache_key in self.pokemon_cache:
            return self.pokemon_cache[cache_key]

        data = await self._fetch_pokemon_data(pokemon_name, get_type_data)

        if len(self.pokemon_cache) >= self.cache_size:
            self.pokemon_cache.pop(next(iter(self.pokemon_cache)))

        self.pokemon_cache[cache_key] = data
        return data

    async def _fetch_pokemon_data(
        self, pokemon_name: str, get_type_data: bool = False
    ) -> Dict[str, Any]:
        """Fetch Pokémon data from the PokéAPI (internal implementation)."""
        url = f"{self.BASE_URL}/pokemon/{pokemon_name.lower()}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            essential_info = {
                "id": data.get("id"),
                "name": data.get("name"),
                "base_experience": data.get("base_experience"),
                "height": data.get("height"),
                "weight": data.get("weight"),
                "abilities": [
                    ability["ability"]["name"] for ability in data.get("abilities", [])
                ],
                "stats": {
                    stat["stat"]["name"]: stat["base_stat"]
                    for stat in data.get("stats", [])
                },
                "types": [ptype["type"]["name"] for ptype in data.get("types", [])],
            }

            if get_type_data:
                essential_info["type_details"] = {}
                for type_name in essential_info["types"]:
                    type_data = await self.get_type_data(type_name)
                    if isinstance(type_data, dict) and "damage_relations" in type_data:
                        essential_info["type_details"][type_name] = type_data[
                            "damage_relations"
                        ]

            return essential_info

        except httpx.HTTPError as e:
            raise PokemonNotFoundError(
                f"TOOL ERROR: Pokémon '{pokemon_name}' not found. Details: {str(e)}"
            )

    async def get_type_data(self, type_name: str) -> Dict[str, Any]:
        """Fetch data about a specific Pokémon type including damage relations with caching."""
        if type_name in self.type_cache:
            return self.type_cache[type_name]

        data = await self._fetch_type_data(type_name)

        if len(self.type_cache) >= self.cache_size:
            self.type_cache.pop(next(iter(self.type_cache)))

        self.type_cache[type_name] = data
        return data

    async def _fetch_type_data(self, type_name: str) -> Dict[str, Any]:
        """Fetch data about a specific Pokémon type including damage relations (internal implementation)."""
        url = f"{self.BASE_URL}/type/{type_name.lower()}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            type_info = {
                "id": data.get("id"),
                "name": data.get("name"),
                "damage_relations": data.get("damage_relations"),
            }
            return type_info

        except httpx.HTTPError as e:
            raise ValueError(f"Error: Type '{type_name}' not found. Details: {str(e)}")
