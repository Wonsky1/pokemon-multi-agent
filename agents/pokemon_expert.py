from typing import List, Dict, Any

from agents.models import (
    AbstractPokemonBattle,
    DetailedPokemonBattle,
    SimplifiedPokemonBattle,
)
from tools.langchain_tools import async_pokeapi_tool_with_types
from agents.base import BaseAgent
from langgraph.prebuilt import create_react_agent
from langchain.agents import Tool


class PokemonExpertAgent(BaseAgent):
    """Agent specialized in Pokémon battle analysis with async support."""

    AGENT_PROMPT = """
        You are a Pokémon expert analyzing battle scenarios. 

        CRITICAL INSTRUCTION: In ANY battle query, you MUST follow this EXACT procedure:

        STEP 1: Extract the exact Pokémon names from the query.
        STEP 2: Convert each Pokémon name to lowercase before using the pokeapi_tool.
        STEP 3: Use the pokeapi_tool to check EACH lowercase Pokémon name.
        STEP 4: BEFORE ANY ANALYSIS, explicitly verify if each Pokémon exists.
        STEP 5: If ANY Pokémon returns an error or "not found" message from the tool, you MUST STOP and return ONLY this JSON:
        {
            "winner": "BATTLE_IMPOSSIBLE",
            "reasoning": "Could not analyze the battle due to invalid Pokémon. Please check the spelling of Pokémon names."
        }

        STEP 6: If ALL Pokémon exist, proceed with the analysis and return the winner and reasoning in this format:
        {
            "winner": "[Winning Pokémon Name]",
            "reasoning": "[Detailed reasoning explaining why this Pokémon wins, mentioning both competitors]"
        }

        In the reasoning section, you MUST include:
        - Comparison of base stats (HP, Attack, Defense, Special Attack, Special Defense, Speed)
        - Type advantages and disadvantages between the two Pokémon
        - Effectiveness of moves based on type matchups (e.g., super effective, not very effective)
        - Any notable strengths or weaknesses that impact the battle outcome
        - A clear explanation of why the winning Pokémon has the advantage

        Base stats are more valuable in determining the winner, but type matchups and move effectiveness are also crucial.

        DO NOT proceed to step 6 if there is at least one non-existent Pokémon or any Pokémon fails the verification.
        DO NOT attempt to correct misspellings.
        DO always convert names to lowercase before using the tool.

        You must FIRST check if ALL Pokémon exist using the tool and ONLY then proceed with analysis.

        Make sure to follow these instructions precisely.
    """

    def __init__(
        self,
        llm,
        tools: List[Tool] = [async_pokeapi_tool_with_types],
        prompt: str = AGENT_PROMPT,
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
            result = await self.agent.ainvoke({"messages": messages})
            structured_response: AbstractPokemonBattle = result["structured_response"]
            return structured_response
        except Exception as e:
            return SimplifiedPokemonBattle(
                winner="BATTLE_IMPOSSIBLE",
                reasoning="Could not analyze the battle due to invalid Pokémon. Please check the spelling of Pokémon names.",
            )
