from typing import List, Dict, Any

from agents.models import (
    AbstractPokemonBattle,
    DetailedPokemonBattle,
    SimplifiedPokemonBattle,
)
from prompts import EXPERT_AGENT_PROMPT
from tools.langchain_tools import async_pokeapi_tool_with_types
from agents.base import BaseAgent
from langgraph.prebuilt import create_react_agent
from langchain.agents import Tool
from langchain_core.language_models import BaseChatModel
from logging import getLogger

logger = getLogger(__name__)


class PokemonExpertAgent(BaseAgent):
    """Agent specialized in Pokémon battle analysis with async support."""
    def __init__(
        self,
        llm: BaseChatModel,
        tools: List[Tool] = [async_pokeapi_tool_with_types],
        prompt: str = EXPERT_AGENT_PROMPT,
        response_format: str = "detailed",
    ):
        """Initialize the Pokémon expert agent."""
        super().__init__(llm)
        response_format = (
            DetailedPokemonBattle
            if response_format == "detailed"
            else SimplifiedPokemonBattle
        )
        self.agent = create_react_agent(
            llm, tools=tools, prompt=prompt, response_format=response_format
        )

    async def process(self, messages: List[Dict[str, str]]) -> AbstractPokemonBattle:
        """Process the message using the react agent asynchronously."""
        try:
            logger.debug(f"Starting Pokémon battle analysis")
            result = await self.agent.ainvoke({"messages": messages})
            structured_response: AbstractPokemonBattle = result["structured_response"]
            return structured_response
        except Exception as e:
            return SimplifiedPokemonBattle(
                winner="BATTLE_IMPOSSIBLE",
                reasoning="Could not analyze the battle due to invalid Pokémon. Please check the spelling of Pokémon names.",
            )
