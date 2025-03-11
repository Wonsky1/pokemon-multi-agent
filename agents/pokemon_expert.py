from typing import List, Dict

from agents.models import PokemonBattle
from tools.langchain_tools import pokeapi_tool_with_types as pokeapi_tool
from agents.base import BaseAgent
from langgraph.prebuilt import create_react_agent

class PokemonExpertAgent(BaseAgent):
    """Agent specialized in Pokémon battle analysis."""
    
    EXPERT_PROMPT = """
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
    
    def __init__(self, llm):
        """Initialize the Pokémon expert agent."""
        super().__init__(llm)
        
        self.agent = create_react_agent(llm, tools=[pokeapi_tool], prompt=self.EXPERT_PROMPT, response_format=PokemonBattle)
    
    def process(self, messages: List[Dict[str, str]]) -> str:
        """Process the message using the react agent."""
        try:
            result = self.agent.invoke({"messages": messages})
            structured_response: PokemonBattle = result["structured_response"]
            return structured_response
        except Exception as e:
            return {
                "winner": "BATTLE_IMPOSSIBLE",
                "reason": "Could not analyze the battle due to invalid Pokémon. Please check the spelling of Pokémon names."
            }
