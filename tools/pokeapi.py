from typing import Dict, Any
from functools import lru_cache
import requests
from core.config import settings
from core.exceptions import PokemonNotFoundError

class PokeAPIService:
    """Service for interacting with the PokéAPI with caching."""
    
    BASE_URL = settings.POKEAPI_BASE_URL
    
    def __init__(self, cache_size: int = 100):
        """Initialize the service with an optional cache size."""
        self.get_pokemon_data = self._create_cached_method(self._get_pokemon_data, cache_size)
        self.get_type_data = self._create_cached_method(self._get_type_data, cache_size)
    
    def _create_cached_method(self, method, cache_size):
        """Creates a cached version of the given method."""
        return lru_cache(maxsize=cache_size)(method)
    
    def pokemon_exists(self, pokemon_name: str) -> bool:
        """Check if a Pokémon exists in the PokéAPI."""
        try:
            self.get_pokemon_data(pokemon_name.lower(), False)
            return True
        except PokemonNotFoundError:
            return False
    
    def _get_pokemon_data(self, pokemon_name: str, get_type_data: bool = False) -> Dict[str, Any]:
        """Fetch Pokémon data from the PokéAPI (internal implementation)."""
        url = f"{self.BASE_URL}/pokemon/{pokemon_name.lower()}"
        
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            essential_info = {
                "id": data.get("id"),
                "name": data.get("name"),
                "base_experience": data.get("base_experience"),
                "height": data.get("height"),
                "weight": data.get("weight"),
                "abilities": [ability["ability"]["name"] for ability in data.get("abilities", [])],
                "stats": {stat["stat"]["name"]: stat["base_stat"] for stat in data.get("stats", [])},
                "types": [ptype["type"]["name"] for ptype in data.get("types", [])],
            }
            
            if get_type_data:
                essential_info["type_details"] = {}
                for type_name in essential_info["types"]:
                    type_data = self.get_type_data(type_name)
                    if isinstance(type_data, dict) and "damage_relations" in type_data:
                        essential_info["type_details"][type_name] = type_data["damage_relations"]
                
            return essential_info
            
        except requests.RequestException as e:
            raise PokemonNotFoundError(f"TOOL ERROR: Pokémon '{pokemon_name}' not found. Details: {str(e)}")
    
    def _get_type_data(self, type_name: str) -> Dict[str, Any]:
        """Fetch data about a specific Pokémon type including damage relations (internal implementation)."""
        url = f"{self.BASE_URL}/type/{type_name.lower()}"
        
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            type_info = {
                "id": data.get("id"),
                "name": data.get("name"),
                "damage_relations": data.get("damage_relations")
            }
            return type_info
            
        except requests.RequestException as e:
            raise ValueError(f"Error: Type '{type_name}' not found. Details: {str(e)}")

pokemon_service = PokeAPIService()

def get_pokemon_service() -> PokeAPIService:
    """Dependency injection provider for PokeAPIService."""
    return pokemon_service
