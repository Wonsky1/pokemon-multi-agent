from typing import List, Dict
from agents.models import PokemonData
from prompts import RESEARCHER_AGENT_PROMPT
from tools.langchain_tools import async_pokeapi_tool
from agents.base import BaseAgent
from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel
from logging import getLogger

logger = getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """Agent responsible for fetching and providing data from external sources."""
    def __init__(self, llm: BaseChatModel):
        """Initialize the researcher agent."""
        super().__init__(llm)

        self.agent = create_react_agent(
            llm,
            tools=[async_pokeapi_tool],
            prompt=RESEARCHER_AGENT_PROMPT,
            response_format=PokemonData,
        )

    async def process(self, messages: List[Dict[str, str]]) -> dict:
        """Process the message using the react agent asynchronously."""
        try:
            logger.debug(f"Starting Pokémon data retrieval")
            result = await self.agent.ainvoke({"messages": messages})
            return result["structured_response"]
        except Exception as e:
            return {
                "name": "NOT_FOUND",
                "base_stats": {
                    "hp": 0,
                    "attack": 0,
                    "defense": 0,
                    "special_attack": 0,
                    "special_defense": 0,
                    "speed": 0,
                },
            }
