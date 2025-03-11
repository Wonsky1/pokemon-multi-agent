from typing import Dict, Any
from core.config import settings
import requests

from core.exceptions import PokemonNotFoundError

class PokeAPIService:
    """Service for interacting with the PokéAPI."""
    
    BASE_URL = settings.POKEAPI_BASE_URL
    
    @classmethod
    def get_pokemon_data(cls, pokemon_name: str) -> Dict[str, Any]:
        """Fetch Pokémon data from the PokéAPI."""
        url = f"{cls.BASE_URL}/pokemon/{pokemon_name.lower()}"
        response = requests.get(url)
        
        if response.status_code == 200:
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
                "type_details": {}
            }
            
            for type_name in essential_info["types"]:
                type_data = cls.get_type_data(type_name)
                if isinstance(type_data, dict) and "damage_relations" in type_data:
                    essential_info["type_details"][type_name] = type_data["damage_relations"]
            
            return essential_info
        else:
            raise PokemonNotFoundError(f"TOOL ERROR: Pokémon '{pokemon_name}' not found.")
    
    @classmethod
    def get_type_data(cls, type_name: str) -> Dict[str, Any]:
        """Fetch data about a specific Pokémon type including damage relations."""
        url = f"{cls.BASE_URL}/type/{type_name.lower()}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            type_info = {
                "id": data.get("id"),
                "name": data.get("name"),
                "damage_relations": data.get("damage_relations")
            }
            return type_info
        else:
            raise ValueError(f"Error: Type '{type_name}' not found.")
