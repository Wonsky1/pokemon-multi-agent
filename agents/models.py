from abc import ABC
from pydantic import BaseModel, Field
from core.config import RouterOptions


class Router(BaseModel):
    """Schema for router response."""

    next: str = Field(
        description="The next agent to route to.",
        json_schema_extra={"enum": [option.value for option in RouterOptions]},
    )


class BaseStats(BaseModel):
    hp: int = Field(description="Hit Points of the Pokémon.")
    attack: int = Field(description="Attack stat of the Pokémon.")
    defense: int = Field(description="Defense stat of the Pokémon.")
    special_attack: int = Field(description="Special Attack stat of the Pokémon.")
    special_defense: int = Field(description="Special Defense stat of the Pokémon.")
    speed: int = Field(description="Speed stat of the Pokémon.")


class PokemonData(BaseModel):
    name: str = Field(description="Name of the Pokémon.")
    base_stats: BaseStats = Field(description="Base stats of the Pokémon.")


class AbstractPokemonBattle(ABC, BaseModel):
    reasoning: str = Field(description="A very detailed analysis with your reasoning")


class DetailedPokemonBattle(AbstractPokemonBattle):
    answer: str = Field(description="A short answer to the battle query.")


class SimplifiedPokemonBattle(AbstractPokemonBattle):
    winner: str = Field(description="The winner of the battle.")
