from typing import List, Dict

from tools.langchain_tools import pokeapi_tool
from agents.base import BaseAgent
from langgraph.prebuilt import create_react_agent

class PokemonExpertAgent(BaseAgent):
    """Agent specialized in Pokémon battle analysis."""
    
    EXPERT_PROMPT = """
        You are a Pokémon expert analyzing battle scenarios. Follow these steps EXACTLY:

        1. ALWAYS use the pokeapi_tool for EACH Pokémon mentioned in the query.
        2. Analyze the data focusing on:
        - Type matchups and damage relations
        - Base stats comparison
        - Abilities and their effects
        3. Determine the likely winner based on:
        - Type advantages/disadvantages
        - Stat differences
        - Ability interactions
        4. Provide a detailed analysis with your reasoning
        5. Present a clear conclusion about the likely winner

        You MUST use the pokeapi_tool for each Pokémon before making any judgments. Never skip this step.
    """
    
    def __init__(self, llm):
        """Initialize the Pokémon expert agent."""
        super().__init__(llm)
        
        self.agent = create_react_agent(llm, tools=[pokeapi_tool], prompt=self.EXPERT_PROMPT)
    
    def process(self, messages: List[Dict[str, str]]) -> str:
        """Process the message using the react agent."""
        result = self.agent.invoke({"messages": messages})
        return result["messages"][-1].content
