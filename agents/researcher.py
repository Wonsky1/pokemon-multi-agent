from typing import List, Dict
from agents.models import PokemonData
from tools.langchain_tools import async_pokeapi_tool
from agents.base import BaseAgent
from langgraph.prebuilt import create_react_agent


class ResearcherAgent(BaseAgent):
    """Agent responsible for fetching and providing data from external sources."""

    AGENT_PROMPT = """
        You are a researcher. When asked about Pokémon, use the provided tool to fetch data from the PokéAPI. Provide a clear, comprehensive answer that directly addresses the user's question.

        IMPORTANT: You must ONLY return real Pokémon data from the PokéAPI tool.
        
        If the tool returns an error message or any indication that the Pokémon was not found, you MUST ALWAYS return EXACTLY this structure:
        {
          "name": "NOT_FOUND",
          "base_stats": {
            "hp": 0,
            "attack": 0,
            "defense": 0,
            "special_attack": 0,
            "special_defense": 0,
            "speed": 0
          }
        }
        
        DO NOT correct any misspellings, look for only the exact Pokémon name provided.
        DO NOT make up or hallucinate stats for Pokémon that don't exist. 
    """

    def __init__(self, llm):
        """Initialize the researcher agent."""
        super().__init__(llm)

        self.agent = create_react_agent(
            llm,
            tools=[async_pokeapi_tool],
            prompt=self.AGENT_PROMPT,
            response_format=PokemonData,
        )

    async def process(self, messages: List[Dict[str, str]]) -> dict:
        """Process the message using the react agent asynchronously."""
        try:
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
